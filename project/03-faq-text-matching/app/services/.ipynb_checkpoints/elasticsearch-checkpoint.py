"""
Elasticsearch Service
Elasticsearch 服务 - 全文检索和向量搜索
"""
from typing import List, Dict, Any, Optional
import hashlib

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from app.config import settings


# ============================================
# ES Client
# ============================================

class ESClient:
    """Elasticsearch 客户端"""

    _client: Optional[AsyncElasticsearch] = None

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        """获取 ES 客户端"""
        if cls._client is None:
            cls._client = AsyncElasticsearch(
                hosts=settings.elasticsearch.hosts,
                timeout=settings.elasticsearch.timeout,
                max_retries=settings.elasticsearch.max_retries,
                retry_on_timeout=settings.elasticsearch.retry_on_timeout,
            )
        return cls._client

    @classmethod
    async def close(cls):
        """关闭 ES 连接"""
        if cls._client:
            await cls._client.close()
            cls._client = None


# ============================================
# Index Management
# ============================================

class ESIndex:
    """ES 索引管理"""

    INDEX_NAME = f"{settings.elasticsearch.index_prefix}faq"

    @classmethod
    async def create_index(cls) -> bool:
        """创建 FAQ 索引 (包含文本和向量字段)"""
        client = await ESClient.get_client()

        # 检查索引是否存在
        if await client.indices.exists(index=cls.INDEX_NAME):
            return True

        # 构建映射
        mapping = {
            "settings": {
                "number_of_shards": settings.elasticsearch.number_of_shards,
                "number_of_replicas": settings.elasticsearch.number_of_replicas,
                "refresh_interval": settings.elasticsearch.refresh_interval,
                # IK 分词器配置需要根据实际情况调整
            },
            "mappings": {
                "properties": {
                    # FAQ 基本信息
                    "faq_id": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart",
                    },
                    "similar_queries": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                    },
                    "tags": {"type": "keyword"},
                    "category_id": {"type": "integer"},
                    "env": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "is_permanent": {"type": "boolean"},
                    "start_time": {"type": "date"},
                    "end_time": {"type": "date"},
                    # 向量字段 (使用 ES dense_vector)
                    "title_vector": {
                        "type": "dense_vector",
                        "dims": settings.elasticsearch.vector.dimension,
                        "index": True,
                        "similarity": settings.elasticsearch.vector.similarity,
                        "index_options": {
                            "type": "hnsw",
                            "m": settings.elasticsearch.vector.m,
                            "ef_construction": settings.elasticsearch.vector.ef_construction,
                        }
                    },
                    "content_vector": {
                        "type": "dense_vector",
                        "dims": settings.elasticsearch.vector.dimension,
                        "index": True,
                        "similarity": settings.elasticsearch.vector.similarity,
                        "index_options": {
                            "type": "hnsw",
                            "m": settings.elasticsearch.vector.m,
                            "ef_construction": settings.elasticsearch.vector.ef_construction,
                        }
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            }
        }

        await client.indices.create(index=cls.INDEX_NAME, body=mapping)
        return True

    @classmethod
    async def delete_index(cls) -> bool:
        """删除 FAQ 索引"""
        client = await ESClient.get_client()
        if await client.indices.exists(index=cls.INDEX_NAME):
            await client.indices.delete(index=cls.INDEX_NAME)
        return True

    @classmethod
    async def exists(cls) -> bool:
        """检查索引是否存在"""
        client = await ESClient.get_client()
        return await client.indices.exists(index=cls.INDEX_NAME)


# ============================================
# Document Operations
# ============================================

class ESDocument:
    """ES 文档操作"""

    INDEX_NAME = ESIndex.INDEX_NAME

    @classmethod
    async def index_faq(
        cls,
        faq_id: int,
        title: str,
        content: str,
        similar_queries: List[str] = None,
        tags: List[str] = None,
        category_id: int = None,
        env: str = "PROD",
        status: str = "ENABLE",
        title_vector: List[float] = None,
        content_vector: List[float] = None,
        **kwargs
    ) -> dict:
        """索引 FAQ 文档"""
        client = await ESClient.get_client()

        doc = {
            "faq_id": faq_id,
            "title": title,
            "content": content,
            "similar_queries": similar_queries or [],
            "tags": tags or [],
            "category_id": category_id,
            "env": env,
            "status": status,
            "title_vector": title_vector or [0] * settings.elasticsearch.vector.dimension,
            "content_vector": content_vector or [0] * settings.elasticsearch.vector.dimension,
            **kwargs
        }

        result = await client.index(
            index=cls.INDEX_NAME,
            id=faq_id,
            document=doc,
            refresh=True
        )

        return result

    @classmethod
    async def bulk_index(cls, documents: List[dict]) -> dict:
        """批量索引文档"""
        client = await ESClient.get_client()

        actions = []
        for doc in documents:
            action = {
                "_index": cls.INDEX_NAME,
                "_id": doc.get("faq_id"),
                "_source": doc
            }
            actions.append(action)

        success, failed = await async_bulk(client, actions, refresh=True)
        return {"success": success, "failed": failed}

    @classmethod
    async def delete_faq(cls, faq_id: int) -> dict:
        """删除 FAQ 文档"""
        client = await ESClient.get_client()
        result = await client.delete(
            index=cls.INDEX_NAME,
            id=faq_id,
            refresh=True
        )
        return result


# ============================================
# Search Operations
# ============================================

class ESSearch:
    """ES 搜索操作"""

    INDEX_NAME = ESIndex.INDEX_NAME

    @classmethod
    async def search_by_keyword(
        cls,
        query: str,
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None
    ) -> List[dict]:
        """关键词搜索"""
        client = await ESClient.get_client()

        must = [
            {"term": {"env": env}},
            {"term": {"status": status}},
        ]

        if category_id:
            must.append({"term": {"category_id": category_id}})

        # 多字段匹配
        should = [
            {
                "match": {
                    "title": {
                        "query": query,
                        "boost": 3.0
                    }
                }
            },
            {
                "match": {
                    "similar_queries": {
                        "query": query,
                        "boost": 2.0
                    }
                }
            },
            {
                "match": {
                    "content": {
                        "query": query,
                        "boost": 1.0
                    }
                }
            },
        ]

        body = {
            "query": {
                "bool": {
                    "must": must,
                    "should": should,
                    "minimum_should_match": 1
                }
            },
            "size": top_k,
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {},
                }
            }
        }

        result = await client.search(index=cls.INDEX_NAME, body=body)

        hits = result.get("hits", {}).get("hits", [])
        return [
            {
                "faq_id": hit["_source"]["faq_id"],
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "score": hit["_score"],
                "highlight": hit.get("highlight", {}),
            }
            for hit in hits
        ]

    @classmethod
    async def search_by_vector(
        cls,
        query_vector: List[float],
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None
    ) -> List[dict]:
        """向量搜索 (KNN)"""
        client = await ESClient.get_client()

        must = [
            {"term": {"env": env}},
            {"term": {"status": status}},
        ]

        if category_id:
            must.append({"term": {"category_id": category_id}})

        body = {
            "query": {
                "bool": {
                    "must": must
                }
            },
            "knn": {
                "field": "content_vector",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": top_k * 10,
            },
            "size": top_k,
        }

        result = await client.search(index=cls.INDEX_NAME, body=body)

        hits = result.get("hits", {}).get("hits", [])
        return [
            {
                "faq_id": hit["_source"]["faq_id"],
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "score": hit["_score"],
            }
            for hit in hits
        ]

    @classmethod
    async def hybrid_search(
        cls,
        query: str,
        query_vector: List[float],
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None,
        keyword_weight: float = 0.5,
        vector_weight: float = 0.5
    ) -> List[dict]:
        """混合搜索 (关键词 + 向量)"""
        client = await ESClient.get_client()

        must = [
            {"term": {"env": env}},
            {"term": {"status": status}},
        ]

        if category_id:
            must.append({"term": {"category_id": category_id}})

        body = {
            "query": {
                "bool": {
                    "must": must,
                    "should": [
                        # 关键词匹配
                        {
                            "match": {
                                "title": {
                                    "query": query,
                                    "boost": keyword_weight * 10
                                }
                            }
                        },
                        {
                            "match": {
                                "content": {
                                    "query": query,
                                    "boost": keyword_weight * 5
                                }
                            }
                        },
                    ]
                }
            },
            "knn": [
                {
                    "field": "title_vector",
                    "query_vector": query_vector,
                    "k": top_k,
                    "num_candidates": top_k * 10,
                    "boost": vector_weight * 10
                },
                {
                    "field": "content_vector",
                    "query_vector": query_vector,
                    "k": top_k,
                    "num_candidates": top_k * 10,
                    "boost": vector_weight * 5
                }
            ],
            "size": top_k,
            "rank": {
                "rrf": {
                    "window_size": top_k * 2
                }
            },
        }

        result = await client.search(index=cls.INDEX_NAME, body=body)

        hits = result.get("hits", {}).get("hits", [])
        return [
            {
                "faq_id": hit["_source"]["faq_id"],
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "score": hit["_score"],
            }
            for hit in hits
        ]
