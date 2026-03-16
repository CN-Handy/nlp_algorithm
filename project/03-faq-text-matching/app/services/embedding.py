"""
Embedding Service
文本向量转换服务 - 同步版本
"""
from typing import List, Optional
import numpy as np

from app.config import settings


# ============================================
# Embedding Client
# ============================================

class EmbeddingClient:
    """Embedding 客户端"""

    _model = None

    @classmethod
    def get_model(cls):
        """获取 embedding 模型"""
        if cls._model is None:
            if settings.embedding.provider == "local":
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(
                    settings.embedding.local.model_name,
                    device=settings.embedding.local.device
                )
            elif settings.embedding.provider == "openai":
                import openai
                openai.api_key = settings.embedding.openai.api_key
                cls._model = "openai"
            else:
                raise ValueError(f"Unsupported embedding provider: {settings.embedding.provider}")
        return cls._model

    @classmethod
    def encode(cls, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """
        将文本转换为向量

        Args:
            texts: 文本列表
            batch_size: 批处理大小

        Returns:
            向量列表
        """
        if not texts:
            return []

        if settings.embedding.provider == "local":
            model = cls.get_model()
            if batch_size is None:
                batch_size = settings.embedding.local.batch_size

            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=settings.embedding.local.normalize_embeddings,
                show_progress_bar=False
            )

            # 转换为列表
            return embeddings.tolist()

        elif settings.embedding.provider == "openai":
            import openai
            model = cls.get_model()

            embeddings = []
            for text in texts:
                response = openai.Embedding.create(
                    model=settings.embedding.openai.model,
                    input=text
                )
                embeddings.append(response["data"][0]["embedding"])

            return embeddings

        else:
            raise ValueError(f"Unsupported embedding provider: {settings.embedding.provider}")

    @classmethod
    def encode_one(cls, text: str) -> List[float]:
        """
        将单个文本转换为向量

        Args:
            text: 文本

        Returns:
            向量
        """
        vectors = cls.encode([text])
        return vectors[0] if vectors else []

    @classmethod
    def close(cls):
        """关闭模型"""
        cls._model = None