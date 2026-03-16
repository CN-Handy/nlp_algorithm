"""
Service API Router
对外服务模块 - Bot Service
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FAQ
from app.datamodels import (
    AskRequest
)
from app.exceptions import success, not_found
from app.services.elasticsearch import ESSearch
from app.services.embedding import EmbeddingClient

router = APIRouter(prefix="/service", tags=["对外服务"])


# ============================================
# Smart Q&A
# ============================================

@router.post("/ask")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    """
    智能问答 - 语义检索

    多路召回策略:
    1. 向量搜索 - 语义相似度匹配 (ES dense_vector)
    2. 关键词搜索 - ES 全文检索 (IK 分词)
    3. 混合搜索 - 结合向量和关键词 (RRF 融合)
    """

    # 1. 生成问题的向量表示
    query_vector = EmbeddingClient.encode_one(request.question)

    # 2. 混合搜索 (向量 + 关键词)
    search_results = ESSearch.hybrid_search(
        query=request.question,
        query_vector=query_vector,
        env=request.env,
        status="ENABLE",
        top_k=request.top_k,
        keyword_weight=0.4,
        vector_weight=0.6
    )

    # 5. 构建响应
    answers = []
    for result in search_results[:request.top_k]:
        faq_id = result["faq_id"]

        print(result)
        # 从数据库获取答案
        solution = _get_solution(db, faq_id)

        if solution:
            answers.append({
                "faq_id": faq_id,
                "title": result["title"],
                "content": result.get("content", ""),
                "score": result.get("score", 0),
                "answer_type": result.get("answer_type"),
            })

    return success(data={"answers": answers, "total": len(answers)})


def _get_solution(db: Session, faq_id: int):
    """获取指定渠道的答案"""
    # 优先查询对应渠道的答案，没有则使用默认答案
    stmt = select(FAQ).where(
        and_(
            FAQ.id == faq_id
        )
    )
    result = db.execute(stmt)
    solution = result.scalar_one_or_none()

    return solution


@router.get("/search")
def search_faqs(
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    env: str = Query("TEST", description="环境"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    """关键词搜索 FAQ (仅使用 ES 关键词检索)"""
    # 使用 ES 关键词搜索
    results = ESSearch.search_by_keyword(
        query=q,
        env=env,
        status="ENABLE",
        top_k=limit,
    )

    answers = []
    for result in results:
        answers.append({
            "faq_id": result["faq_id"],
            "title": result["title"],
            "content": result.get("content", ""),
            "score": result.get("score", 0),
        })

    return success(data={"results": answers, "total": len(answers)})


# ============================================
# FAQ Detail
# ============================================

@router.get("/faq/{faq_id}")
def get_faq_detail(
    faq_id: int,
    env: str,
    db: Session = Depends(get_db)
):
    """获取 FAQ 详情"""
    stmt = select(FAQ).where(and_(FAQ.id == faq_id, FAQ.env == env))
    result = db.execute(stmt)
    faq = result.scalar_one_or_none()
    if not faq:
        return not_found(msg="FAQ不存在")

    data = {
        "id": faq,
        "title": faq.title,
        "similar_queries": faq.similar_queries,
        "tags": faq.tags,
        "content": faq.content,
        "related_ids": faq.related_ids,
        "created_at": faq.created_at.isoformat() if faq.created_at else None,
        "updated_at": faq.updated_at.isoformat() if faq.updated_at else None,
    }

    return success(data=data)
