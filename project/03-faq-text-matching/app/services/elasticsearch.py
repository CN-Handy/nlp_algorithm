"""
Elasticsearch Service
Elasticsearch 服务 - 全文检索和向量搜索 - 同步版本
"""
from typing import List, Dict, Any, Optional
import hashlib

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.config import settings


# ============================================
# ES Client
# ============================================

class ESClient:
    """Elasticsearch 客户端"""

    _client: Optional[Elasticsearch] = None

    @classmethod
    def get_client(cls) -> Elasticsearch:
        """获取 ES 客户端"""
        if cls._client is None:
            cls._client = Elasticsearch(
                hosts=settings.elasticsearch.hosts,
                timeout=settings.elasticsearch.timeout,
                max_retries=settings.elasticsearch.max_retries,
                retry_on_timeout=settings.elasticsearch.retry_on_timeout,
            )
        return cls._client

    @classmethod
    def close(cls):
        """关闭 ES 连接"""
        if cls._client:
            cls._client.close()
            cls._client = None


# ============================================
# Index Management
# ============================================

class ESIndex:
    """ES 索引管理"""

    INDEX_NAME = f"{settings.elasticsearch.index_prefix}faq"

    @classmethod
    def create_index(cls) -> bool:
        """创建 FAQ 索引 (包含文本和向量字段)"""
        client = ESClient.get_client()

        # 检查索引是否存在
        if client.indices.exists(index=cls.INDEX_NAME):
            return True

        # 构建映射
        mapping = {
            "settings": {
                "number_of_shards": settings.elasticsearch.number_of_shards,
                "number_of_replicas": settings.elasticsearch.number_of_replicas,
                "refresh_interval": settings.elasticsearch.refresh_interval,
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

        client.indices.create(index=cls.INDEX_NAME, body=mapping)
        return True

    @classmethod
    def delete_index(cls) -> bool:
        """删除 FAQ 索引"""
        client = ESClient.get_client()
        if client.indices.exists(index=cls.INDEX_NAME):
            client.indices.delete(index=cls.INDEX_NAME)
        return True

    @classmethod
    def exists(cls) -> bool:
        """检查索引是否存在"""
        client = ESClient.get_client()
        return client.indices.exists(index=cls.INDEX_NAME)


# ============================================
# Document Operations
# ============================================

class ESDocument:
    """ES 文档操作"""

    INDEX_NAME = ESIndex.INDEX_NAME

    @classmethod
    def index_faq(
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
        client = ESClient.get_client()

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

        result = client.index(
            index=cls.INDEX_NAME,
            id=faq_id,
            document=doc,
            refresh=True
        )

        return result

    @classmethod
    def bulk_index(cls, documents: List[dict]) -> dict:
        """批量索引文档"""
        client = ESClient.get_client()

        actions = []
        for doc in documents:
            action = {
                "_index": cls.INDEX_NAME,
                "_id": doc.get("faq_id"),
                "_source": doc
            }
            actions.append(action)

        success, failed = bulk(client, actions, refresh=True)
        return {"success": success, "failed": failed}

    @classmethod
    def delete_faq(cls, faq_id: int, env: str) -> dict:
        """删除 FAQ 文档"""
        client = ESClient.get_client()
        result = client.delete_by_query(
            index=cls.INDEX_NAME,
            body={
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"_id": faq_id}},
                            {"term": {"env": env}}
                        ]
                    }
                }
            },
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
    def search_by_keyword(
        cls,
        query: str,
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None
    ) -> List[dict]:
        """关键词搜索"""
        client = ESClient.get_client()

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

        result = client.search(index=cls.INDEX_NAME, body=body)

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
    def search_by_vector(
        cls,
        query_vector: List[float],
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None
    ) -> List[dict]:
        """向量搜索 (KNN)"""
        client = ESClient.get_client()

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

        result = client.search(index=cls.INDEX_NAME, body=body)

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
    def hybrid_search(
        cls,
        query: str,
        query_vector: List[float],
        env: str = "PROD",
        status: str = "ENABLE",
        top_k: int = 10,
        category_id: int = None,
        keyword_weight: float = 0.5,
        vector_weight: float = 0.5,
        rrf_k: int = 60
    ) -> List[dict]:
        """混合搜索 (关键词 + 向量) - 手动实现 RRF"""
        # 分别执行关键词搜索和向量搜索
        keyword_results = cls.search_by_keyword(
            query=query,
            env=env,
            status=status,
            top_k=top_k * 2,
            category_id=category_id
        )
        print(keyword_results)


        vector_results = cls.search_by_vector(
            query_vector=query_vector,
            env=env,
            status=status,
            top_k=top_k * 2,
            category_id=category_id
        )
        print(vector_results)

        # 手动实现 RRF (Reciprocal Rank Fusion)
        # RRF_score(d) = Σ 1/(rank(d) + k), k 默认 60
        rrf_scores: Dict[int, float] = {}

        # 处理关键词搜索结果
        for rank, hit in enumerate(keyword_results, start=1):
            faq_id = hit["faq_id"]
            # 对关键词分数做归一化处理，加上权重
            normalized_score = hit["score"] if hit["score"] else 0
            rrf_scores[faq_id] = rrf_scores.get(faq_id, 0) + keyword_weight * (1 / (rank + rrf_k))

        # 处理向量搜索结果
        for rank, hit in enumerate(vector_results, start=1):
            faq_id = hit["faq_id"]
            normalized_score = hit["score"] if hit["score"] else 0
            rrf_scores[faq_id] = rrf_scores.get(faq_id, 0) + vector_weight * (1 / (rank + rrf_k))

        # 按 RRF 分数排序，取 top_k
        sorted_faq_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # 构建最终结果
        # 创建 faq_id -> 结果的映射
        all_results = {hit["faq_id"]: hit for hit in keyword_results + vector_results}

        final_results = []
        for faq_id, rrf_score in sorted_faq_ids:
            if faq_id in all_results:
                hit = all_results[faq_id]
                final_results.append({
                    "faq_id": hit["faq_id"],
                    "title": hit["title"],
                    "content": hit["content"],
                    "score": round(rrf_score, 4),
                })

        print(final_results)
        return final_results
