"""
FAQ API Router
FAQ 管理接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import FAQ, Category
from app.datamodels import (
    FAQCreate,
    FAQUpdate,
)
from app.exceptions import success, created, no_content, bad_request, not_found
from app.services import EmbeddingClient
from app.services.elasticsearch import ESDocument

router = APIRouter(prefix="/admin/faqs", tags=["FAQ管理"])


# ============================================
# FAQ CRUD
# ============================================

@router.post("")
def create_faq(
        data: FAQCreate,
        db: Session = Depends(get_db)
):
    """创建 FAQ"""
    parent = db.get(Category, data.category_id)
    if not parent or parent.env != data.env.value:
        return bad_request(msg="类目环境与FAQ环境不匹配")

    faq = FAQ(
        env=data.env.value,
        category_id=data.category_id,
        title=data.title,
        similar_queries=data.similar_queries or [],
        related_ids=data.related_ids or [],
        tags=data.tags or [],
        status=data.status.value,
        is_permanent=data.is_permanent,
        start_time=data.start_time,
        end_time=data.end_time,
        updated_at=datetime.now(),
        creator=data.creator,
        modifier=data.creator,
        content=data.content,
    )
    db.add(faq)
    db.flush()
    db.refresh(faq)

    title_vector = EmbeddingClient.encode_one(data.title)
    content_vector = EmbeddingClient.encode_one(data.content)
    ESDocument.index_faq(
        faq_id=faq.id,
        title=faq.title,
        content=faq.content,
        similar_queries=faq.similar_queries,
        tags=faq.tags,
        category_id=faq.category_id,
        env=faq.env,
        status=faq.status,
        title_vector=title_vector,
        content_vector=content_vector,
        is_permanent=faq.is_permanent,
        start_time=faq.start_time,
        end_time=faq.end_time,
    )

    return created(data={"id": faq.id, "env": faq.env, "status": faq.status})


@router.get("")
def list_faqs(
        env: str = Query("TEST", description="环境"),
        category_id: Optional[int] = Query(None, description="类目ID"),
        status: Optional[str] = Query(None, description="状态"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db)
):
    """获取 FAQ 列表"""
    conditions = [FAQ.env == env]

    if category_id:
        conditions.append(FAQ.category_id == category_id)
    if status:
        conditions.append(FAQ.status == status)

    # 查询总数
    count_stmt = select(func.count(FAQ.id)).where(and_(*conditions))
    total_result = db.execute(count_stmt)
    total = total_result.scalar()

    # 分页查询
    stmt = select(FAQ).where(and_(*conditions)).order_by(FAQ.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = db.execute(stmt)
    faqs = result.scalars().all()

    items = [f.__dict__ for f in faqs]

    return success(data={
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@router.get("/{faq_id}")
def get_faq(
        faq_id: int,
        db: Session = Depends(get_db)
):
    """获取 FAQ 详情（含答案）"""
    faq = db.get(FAQ, faq_id)
    if not faq:
        return not_found(msg="FAQ不存在")

    return success(data=faq.__dict__)


@router.put("/{faq_id}")
def update_faq(
        faq_id: int,
        env: str,
        data: FAQUpdate,
        db: Session = Depends(get_db)
):
    """更新 FAQ"""
    faq = db.get(FAQ, faq_id)
    if not faq:
        return not_found(msg="FAQ不存在")

    # 更新字段
    if data.title is not None:
        faq.title = data.title
    if data.category_id is not None:
        faq.category_id = data.category_id
    if data.similar_queries is not None:
        faq.similar_queries = data.similar_queries
    if data.related_ids is not None:
        faq.related_ids = data.related_ids
    if data.tags is not None:
        faq.tags = data.tags
    if data.is_permanent is not None:
        faq.is_permanent = data.is_permanent
    if data.start_time is not None:
        faq.start_time = data.start_time
    if data.end_time is not None:
        faq.end_time = data.end_time
    if data.modifier is not None:
        faq.modifier = data.modifier
    if data.content is not None:
        faq.content = data.content

    db.flush()
    db.refresh(faq)

    faq = db.get(FAQ, faq_id)
    ESDocument.delete_faq(faq_id=faq_id, env=env)

    title_vector = EmbeddingClient.encode_one(faq.title)
    content_vector = EmbeddingClient.encode_one(faq.content)
    ESDocument.index_faq(
        faq_id=faq.id,
        title=faq.title,
        content=faq.content,
        similar_queries=faq.similar_queries,
        tags=faq.tags,
        category_id=faq.category_id,
        env=faq.env,
        status=faq.status,
        title_vector=title_vector,
        content_vector=content_vector,
        is_permanent=faq.is_permanent,
        start_time=faq.start_time,
        end_time=faq.end_time,
    )

    return success(data={"id": faq.id, "env": faq.env, "status": faq.status})


@router.delete("/{faq_id}")
def delete_faq(
        faq_id: int,
        env: str = Query("TEST", description="环境"),
        db: Session = Depends(get_db)
):
    """删除 FAQ"""
    stmt = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.env == env))
    result = db.execute(stmt)
    faq = result.scalar_one_or_none()

    if not faq:
        return not_found(msg="FAQ不存在")

    db.delete(faq)
    db.flush()

    ESDocument.delete_faq(faq_id=faq_id, env=env)
    return no_content(msg="删除成功")
