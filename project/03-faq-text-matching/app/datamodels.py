"""
Data Models
数据模型 - 使用 Pydantic 定义项目核心数据结构
"""
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================
# Enums
# ============================================

class EnvEnum(str, Enum):
    """环境枚举"""
    TEST = "TEST"
    PROD = "PROD"


class FAQStatusEnum(str, Enum):
    """FAQ 状态枚举"""
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"


class AnswerTypeEnum(str, Enum):
    """答案类型枚举"""
    TEXT = "TEXT"
    RICH = "RICH"
    CARD = "CARD"


class SyncTypeEnum(str, Enum):
    """同步类型枚举"""
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"


class SyncStatusEnum(str, Enum):
    """同步状态枚举"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


# ============================================
# Category Data Models
# ============================================

class CategoryBase(BaseModel):
    """类目基础模型"""
    name: str = Field(..., max_length=64, description="类目名称")
    level: int = Field(..., ge=1, le=2, description="层级：1-一级，2-二级")
    parent_id: Optional[int] = Field(None, description="父类目ID")


class CategoryCreate(CategoryBase):
    """创建类目"""
    env: EnvEnum = Field(..., description="环境标识")
    creator: str = Field(..., max_length=64, description="创建人")

    @field_validator('parent_id')
    @classmethod
    def validate_parent_id(cls, v, info):
        if v is not None and 'level' in info.data:
            if info.data['level'] == 1 and v is not None:
                raise ValueError("一级类目不能有父类目")
            if info.data['level'] == 2 and v is None:
                raise ValueError("二级类目必须有父类目")
        return v


class CategoryUpdate(BaseModel):
    """更新类目"""
    name: Optional[str] = Field(None, max_length=64)
    modifier: Optional[str] = Field(None, max_length=64)


class Category(CategoryBase):
    """类目完整模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="类目ID")
    env: EnvEnum
    original_id: Optional[int] = Field(None, description="溯源ID")
    creator: str
    modifier: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class CategoryTreeNode(BaseModel):
    """类目树节点"""
    id: int
    name: str
    level: int
    children: List["CategoryTreeNode"] = Field(default_factory=list)


# ============================================
# FAQ Data Models
# ============================================

class FAQBase(BaseModel):
    """FAQ 基础模型"""
    title: str = Field(..., max_length=255, description="标准问标题")
    category_id: int = Field(..., description="关联类目ID")
    similar_queries: Optional[List[str]] = Field(default_factory=list, description="相似问列表")
    related_ids: Optional[List[int]] = Field(default_factory=list, description="关联问题ID列表")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    is_permanent: bool = Field(default=True, description="是否永久生效")


class FAQCreate(FAQBase):
    """创建 FAQ"""
    env: EnvEnum
    status: FAQStatusEnum = FAQStatusEnum.ENABLE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    creator: str = Field(..., max_length=64)
    answer_type: AnswerTypeEnum = AnswerTypeEnum.TEXT
    content: str = Field(..., description="答案内容")


class FAQUpdate(BaseModel):
    """更新 FAQ"""
    title: Optional[str] = Field(None, max_length=255)
    category_id: Optional[int] = None
    similar_queries: Optional[List[str]] = None
    related_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    is_permanent: Optional[bool] = None
    answer_type: AnswerTypeEnum = AnswerTypeEnum.TEXT
    content: str = Field(..., description="答案内容")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    modifier: Optional[str] = Field(None, max_length=64)
    model_config = ConfigDict(from_attributes=True)

    id: int
    env: EnvEnum
    status: FAQStatusEnum
    original_id: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    creator: str
    modifier: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


# ============================================
# FAQ Solution Data Models
# ============================================

class FAQSolutionBase(BaseModel):
    """FAQ 答案基础模型"""
    perspective: str = Field(..., max_length=50, description="视角：default, wechat, app, web")
    answer_type: AnswerTypeEnum
    content: str = Field(..., description="答案内容")
    is_default: bool = Field(default=False, description="是否为默认答案")
    sort: int = Field(default=0, description="排序权重")


# ============================================
# Search Data Models
# ============================================


class AskRequest(BaseModel):
    """智能问答请求"""
    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)
    env: EnvEnum


class AskResponse(BaseModel):
    """智能问答响应"""
    answers: List[FAQSolutionBase]
    session_id: Optional[str] = None


# ============================================
# Pagination
# ============================================

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    page: int
    page_size: int
    total: int
    total_pages: int


# ============================================
# Health Check
# ============================================

class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """组件健康状态"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: HealthStatus
    version: str
    timestamp: datetime
    components: List[ComponentHealth]


# ============================================
# Common Response
# ============================================

class ResponseCode(int, Enum):
    """响应状态码"""
    SUCCESS = 200  # 成功
    CREATED = 201  # 创建成功
    NO_CONTENT = 204  # 无内容
    BAD_REQUEST = 400  # 请求参数错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    CONFLICT = 409  # 资源冲突
    SERVER_ERROR = 500  # 服务器内部错误


class ResponseModel(BaseModel):
    """
    统一响应模型

    字段说明:
    - code: 状态码 (200=成功, 400=参数错误, 401=未授权, 404=不存在, 500=服务器错误)
    - msg: 提示信息
    - data: 响应数据
    - time: 时间戳
    """
    model_config = ConfigDict(from_attributes=True)

    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="提示信息")
    data: Any = Field(default=None, description="响应数据")
    time: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    @classmethod
    def success(cls, data: Any = None, msg: str = "success") -> "ResponseModel":
        """成功响应"""
        return cls(code=ResponseCode.SUCCESS, msg=msg, data=data)

    @classmethod
    def created(cls, data: Any = None, msg: str = "创建成功") -> "ResponseModel":
        """创建成功响应"""
        return cls(code=ResponseCode.CREATED, msg=msg, data=data)

    @classmethod
    def no_content(cls, msg: str = "操作成功") -> "ResponseModel":
        """无内容响应 (用于删除操作)"""
        return cls(code=ResponseCode.NO_CONTENT, msg=msg)

    @classmethod
    def fail(cls, msg: str = "操作失败", code: int = ResponseCode.SERVER_ERROR) -> "ResponseModel":
        """失败响应"""
        return cls(code=code, msg=msg, data=None)

    @classmethod
    def bad_request(cls, msg: str = "请求参数错误") -> "ResponseModel":
        """参数错误响应"""
        return cls(code=ResponseCode.BAD_REQUEST, msg=msg)

    @classmethod
    def unauthorized(cls, msg: str = "未授权") -> "ResponseModel":
        """未授权响应"""
        return cls(code=ResponseCode.UNAUTHORIZED, msg=msg)

    @classmethod
    def forbidden(cls, msg: str = "禁止访问") -> "ResponseModel":
        """禁止访问响应"""
        return cls(code=ResponseCode.FORBIDDEN, msg=msg)

    @classmethod
    def not_found(cls, msg: str = "资源不存在") -> "ResponseModel":
        """资源不存在响应"""
        return cls(code=ResponseCode.NOT_FOUND, msg=msg)

    @classmethod
    def conflict(cls, msg: str = "资源冲突") -> "ResponseModel":
        """资源冲突响应"""
        return cls(code=ResponseCode.CONFLICT, msg=msg)

    @classmethod
    def server_error(cls, msg: str = "服务器内部错误") -> "ResponseModel":
        """服务器错误响应"""
        return cls(code=ResponseCode.SERVER_ERROR, msg=msg)


class PageResponse(BaseModel):
    """分页响应"""
    model_config = ConfigDict(from_attributes=True)

    items: List[Any] = Field(default_factory=list, description="数据列表")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total: int = Field(default=0, description="总数量")
    total_pages: int = Field(default=0, description="总页数")


class ListResponse(BaseModel):
    """列表响应 (不带分页)"""
    items: List[Any] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")


# ============================================
# Additional Request/Response Models (from schemas.py)
# ============================================

class FAQStatusUpdate(BaseModel):
    """更新 FAQ 状态请求"""
    faq_ids: List[int] = Field(..., min_length=1, description="FAQ ID列表")
    status: FAQStatusEnum
    modifier: str = Field(..., max_length=64, description="修改人")


class AskAnswer(BaseModel):
    """问答答案"""
    faq_id: int
    title: str
    score: float
    content: Optional[str] = None
    solution: Optional[dict] = None
    highlight: Optional[dict] = None


class AskAnswerResponse(BaseModel):
    """智能问答响应 (兼容旧版)"""
    answers: List[AskAnswer]
    total: int = 0


class PageInfo(BaseModel):
    """分页信息"""
    page: int
    page_size: int
    total: int
    total_pages: int


class APIResponse(BaseModel):
    """通用 API 响应 (兼容旧版)"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[str] = None
