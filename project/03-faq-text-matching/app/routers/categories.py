"""
Category API Router
类目管理接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, FAQ
from app.datamodels import (
    CategoryCreate,
    CategoryUpdate,
    Category as CategoryModel,
    CategoryTreeNode,
)
from app.exceptions import success, created, no_content, bad_request, not_found, conflict

router = APIRouter(prefix="/admin/categories", tags=["类目管理"])


# ============================================
# CRUD Operations
# ============================================

@router.post("")
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """创建类目"""
    # 验证父类目
    if data.parent_id is not None:
        parent = db.get(Category, data.parent_id)
        if not parent:
            return not_found(msg="父类目不存在")
        if parent.level >= 2:
            return bad_request(msg="不支持超过二级类目")

    category = Category(
        env=data.env.value,
        name=data.name,
        parent_id=data.parent_id,
        level=data.level,
        creator=data.creator,
    )
    db.add(category)
    db.flush()
    db.refresh(category)

    return created(data=CategoryModel.model_validate(category).model_dump())


@router.get("/tree")
def get_category_tree(
        env: str = Query("TEST", description="环境: TEST/PROD"),
        db: Session = Depends(get_db)
):
    """获取类目树"""
    # 查询所有类目
    stmt = select(Category).where(Category.env == env).order_by(Category.level, Category.id)
    result = db.execute(stmt)
    categories = result.scalars().all()

    # 构建树形结构
    category_map = {c.id: c for c in categories}
    tree_nodes = {}

    for cat in categories:
        node = CategoryTreeNode(
            id=cat.id,
            name=cat.name,
            level=cat.level,
            children=[]
        )

        if cat.parent_id:
            parent = category_map.get(cat.parent_id)
            if parent:
                parent_node = tree_nodes.get(parent.id)
                if parent_node:
                    parent_node.children.append(node)
        else:
            tree_nodes[cat.id] = node

    # 返回顶级节点
    tree_data = [tree_nodes[c.id].model_dump() for c in categories if c.parent_id is None]
    return success(data=tree_data)


@router.get("")
def list_categories(
        env: str = Query("TEST", description="环境"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db)
):
    """获取类目列表"""
    # 查询总数
    count_stmt = select(func.count(Category.id)).where(Category.env == env)
    total_result = db.execute(count_stmt)
    total = total_result.scalar()

    # 分页查询
    stmt = select(Category).where(Category.env == env).order_by(Category.id)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = db.execute(stmt)
    categories = result.scalars().all()

    items = [CategoryModel.model_validate(c).model_dump() for c in categories]

    return success(data={
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@router.get("/{category_id}")
def get_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """获取类目详情"""
    category = db.get(Category, category_id)
    if not category:
        return not_found(msg="类目不存在")

    return success(data=CategoryModel.model_validate(category).model_dump())


@router.put("/{category_id}")
def update_category(
        category_id: int,
        data: CategoryUpdate,
        db: Session = Depends(get_db)
):
    """更新类目"""
    category = db.get(Category, category_id)
    if not category:
        return not_found(msg="类目不存在")

    if data.name is not None:
        category.name = data.name
    if data.modifier is not None:
        category.modifier = data.modifier

    db.flush()
    db.refresh(category)

    return success(data=CategoryModel.model_validate(category).model_dump())


@router.delete("/{category_id}")
def delete_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """删除类目"""
    category = db.get(Category, category_id)
    if not category:
        return not_found(msg="类目不存在")

    # 检查是否有子分类
    stmt = select(Category).where(Category.parent_id == category_id)
    result = db.execute(stmt)
    children = result.scalars().first()
    if children:
        return bad_request(msg="请先删除子类目")

    # 检查是否有关联 FAQ
    stmt = select(FAQ).where(FAQ.category_id == category_id)
    result = db.execute(stmt)
    faq = result.scalars().first()
    if faq:
        return conflict(msg="该类目下存在FAQ，无法删除")

    db.delete(category)
    db.flush()

    return no_content(msg="删除成功")
