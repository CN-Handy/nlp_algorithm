"""
Configuration module
配置加载模块
"""
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# ============================================
# Pydantic Models
# ============================================

class AppConfig(BaseModel):
    """应用配置"""
    name: str = "FAQ智能问答系统"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class AppAPIConfig(BaseModel):
    """API 配置"""
    prefix: str = "/api/v1"
    title: str = "FAQ智能问答系统API"
    description: str = "客服工作台与智能问答系统"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"


class AppCorsConfig(BaseModel):
    """CORS 配置"""
    enabled: bool = True
    allow_origins: List[str] = ["http://localhost:3000"]
    allow_methods: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    allow_headers: List[str] = ["*"]
    allow_credentials: bool = True


class JWTConfig(BaseModel):
    """JWT 配置"""
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


class AppSettings(BaseModel):
    """应用设置"""
    app: AppConfig
    api: AppAPIConfig = Field(default_factory=AppAPIConfig)
    cors: AppCorsConfig = Field(default_factory=AppCorsConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)


class MySQLConfig(BaseModel):
    """MySQL 配置"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "faq_db"
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False

    @property
    def url(self) -> str:
        """构建数据库 URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )


class DatabaseConfig(BaseModel):
    """数据库配置"""
    mysql: MySQLConfig = Field(default_factory=MySQLConfig)


class ESVectorConfig(BaseModel):
    """Elasticsearch 向量搜索配置"""
    enabled: bool = True
    dimension: int = 384  # all-MiniLM-L6-v2 向量维度
    similarity: str = "cosine"  # cosine, dot_product, euclidean
    m: int = 16  # HNSW M 参数
    ef_construction: int = 256  # HNSW ef_construction 参数
    ef: int = 128  # HNSW 搜索时的 ef 参数


class ElasticsearchConfig(BaseModel):
    """Elasticsearch 配置 (支持全文检索和向量搜索)"""
    hosts: List[str] = Field(default_factory=lambda: ["http://localhost:9200"])
    index_prefix: str = "faq_"
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True
    number_of_shards: int = 1
    number_of_replicas: int = 0
    refresh_interval: str = "1s"
    vector: ESVectorConfig = Field(default_factory=ESVectorConfig)


class LocalEmbeddingConfig(BaseModel):
    """本地 Embedding 模型配置"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    normalize_embeddings: bool = True
    batch_size: int = 32


class OpenAIEmbeddingConfig(BaseModel):
    """OpenAI Embedding 配置"""
    api_key: str = ""
    model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536


class EmbeddingConfig(BaseModel):
    """Embedding 模型配置"""
    provider: str = "local"  # local, openai, azure
    local: LocalEmbeddingConfig = Field(default_factory=LocalEmbeddingConfig)
    openai: OpenAIEmbeddingConfig = Field(default_factory=OpenAIEmbeddingConfig)


class SearchConfig(BaseModel):
    """搜索配置"""
    semantic_weight: float = 0.4
    keyword_weight: float = 0.3
    exact_match_weight: float = 0.3
    vector_top_k: int = 5
    vector_score_threshold: float = 0.5
    keyword_top_k: int = 10
    keyword_fuzziness: str = "AUTO"


class FAQPaginationConfig(BaseModel):
    """FAQ 分页配置"""
    default_page_size: int = 20
    max_page_size: int = 100


class FAQBatchConfig(BaseModel):
    """FAQ 批量操作配置"""
    import_limit: int = 3000
    export_limit: int = 50000


class ChannelConfig(BaseModel):
    """渠道配置"""
    code: str
    name: str
    is_active: bool = True


class EnvironmentConfig(BaseModel):
    """环境配置"""
    code: str
    name: str


class FAQConfig(BaseModel):
    """FAQ 配置"""
    pagination: FAQPaginationConfig = Field(default_factory=FAQPaginationConfig)
    batch: FAQBatchConfig = Field(default_factory=FAQBatchConfig)
    answer_types: List[str] = ["TEXT", "RICH", "CARD"]
    channels: List[ChannelConfig] = Field(default_factory=list)
    environments: List[EnvironmentConfig] = Field(
        default_factory=lambda: [
            EnvironmentConfig(code="TEST", name="测试环境"),
            EnvironmentConfig(code="PROD", name="正式环境"),
        ]
    )
    status: List[str] = ["ENABLE", "DISABLE"]


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "./logs/app.log"
    max_bytes: int = 10485760
    backup_count: int = 5
    console: bool = True


class PrometheusConfig(BaseModel):
    """Prometheus 配置"""
    enabled: bool = False
    port: int = 9090


class MonitoringConfig(BaseModel):
    """监控配置"""
    enabled: bool = False
    prometheus: PrometheusConfig = Field(default_factory=PrometheusConfig)


class GlobalCacheConfig(BaseModel):
    """全局缓存配置"""
    enabled: bool = True
    ttl: int = 3600
    prefix: str = "faq:"


# ============================================
# Main Config
# ============================================

class Settings(BaseSettings):
    """主配置类"""

    # App
    app: AppConfig = Field(default_factory=AppConfig)
    api: AppAPIConfig = Field(default_factory=AppAPIConfig)
    cors: AppCorsConfig = Field(default_factory=AppCorsConfig)

    # Database
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # Search
    elasticsearch: ElasticsearchConfig = Field(default_factory=ElasticsearchConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)

    # FAQ
    faq: FAQConfig = Field(default_factory=FAQConfig)

    # Other
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Monitoring & Cache (top-level config.yaml sections)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    cache: GlobalCacheConfig = Field(default_factory=GlobalCacheConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

    @classmethod
    def from_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """从 YAML 文件加载配置"""
        path = Path(config_path)
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)


# ============================================
# Global instance
# ============================================

def get_settings() -> Settings:
    """获取配置实例"""
    return Settings.from_yaml("config.yaml")


# 全局配置实例
settings = get_settings()
