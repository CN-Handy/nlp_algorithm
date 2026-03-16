"""
Response Utilities
统一响应工具
"""
from typing import Any, List, TypeVar

from app.datamodels import ResponseModel, ResponseCode, PageResponse, ListResponse

T = TypeVar("T")


# ============================================
# Response Helpers
# ============================================

def success(data: Any = None, msg: str = "success") -> dict:
    """
    成功响应

    Args:
        data: 响应数据
        msg: 提示信息

    Returns:
        dict: 统一响应格式
    """
    return ResponseModel.success(data=data, msg=msg).model_dump()


def created(data: Any = None, msg: str = "创建成功") -> dict:
    """创建成功响应"""
    return ResponseModel.created(data=data, msg=msg).model_dump()


def no_content(msg: str = "操作成功") -> dict:
    """无内容响应"""
    return ResponseModel.no_content(msg=msg).model_dump()


def fail(msg: str = "操作失败", code: int = ResponseCode.SERVER_ERROR) -> dict:
    """失败响应"""
    return ResponseModel.fail(msg=msg, code=code).model_dump()


def bad_request(msg: str = "请求参数错误") -> dict:
    """参数错误响应"""
    return ResponseModel.bad_request(msg=msg).model_dump()


def unauthorized(msg: str = "未授权") -> dict:
    """未授权响应"""
    return ResponseModel.unauthorized(msg=msg).model_dump()


def forbidden(msg: str = "禁止访问") -> dict:
    """禁止访问响应"""
    return ResponseModel.forbidden(msg=msg).model_dump()


def not_found(msg: str = "资源不存在") -> dict:
    """资源不存在响应"""
    return ResponseModel.not_found(msg=msg).model_dump()


def conflict(msg: str = "资源冲突") -> dict:
    """资源冲突响应"""
    return ResponseModel.conflict(msg=msg).model_dump()


def server_error(msg: str = "服务器内部错误") -> dict:
    """服务器错误响应"""
    return ResponseModel.server_error(msg=msg).model_dump()


# ============================================
# Page Response Helpers
# ============================================

def page(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    total: int = 0
) -> dict:
    """
    分页响应

    Args:
        items: 数据列表
        page: 当前页码
        page_size: 每页数量
        total: 总数量

    Returns:
        dict: 带分页的响应
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    page_data = PageResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )
    return success(data=page_data.model_dump())


def list_response(items: List[Any], total: int = 0) -> dict:
    """
    列表响应 (不分页)

    Args:
        items: 数据列表
        total: 总数量

    Returns:
        dict: 列表响应
    """
    return success(data=ListResponse(items=items, total=total).model_dump())


# ============================================
# Data Response Helpers
# ============================================

def data(data: Any, msg: str = "success") -> dict:
    """数据响应"""
    return success(data=data, msg=msg)


def msg(msg: str) -> dict:
    """仅消息响应"""
    return success(data=None, msg=msg)


# ============================================
# Error Response Helpers
# ============================================

def error(msg: str, code: int = ResponseCode.SERVER_ERROR) -> dict:
    """错误响应"""
    return fail(msg=msg, code=code)


def validation_error(msg: str = "数据验证失败") -> dict:
    """验证错误"""
    return bad_request(msg=msg)


# ============================================
# FastAPI Response Model Helper
# ============================================

def get_response_model(schema: Any = None):
    """
    获取 FastAPI 响应模型

    Usage:
        @app.get("/items", response_model=get_response_model(Item))
        async def get_items():
            ...
    """
    if schema:
        return {200: {"model": schema}}
    return {200: {"model": dict}}
