"""
Request/Response Logging Middleware
请求/响应日志中间件 - 记录请求来源IP、请求内容、响应内容、异常信息
"""
import time
import traceback
import uuid
from functools import wraps
from typing import Optional, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import logger


# ============================================
# Request/Response Logging Middleware
# ============================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求/响应日志中间件"""

    # 最大请求体大小 (1MB)
    MAX_BODY_SIZE = 1024 * 1024

    # 排除不记录日志的路径
    EXCLUDE_PATHS = {
        "/health",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        # 排除路径不记录日志
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 记录请求开始
        request_id = f"{int(time.time() * 1000)}"

        logger.info(
            f"[{request_id}] Incoming request: {request.method} {request.url.path} | "
            f"IP: {client_ip} | "
            f"Params: {request.query_params}"
        )

        # 记录请求体 (如果存在)
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await self._get_request_body(request)
            if request_body:
                # 敏感信息脱敏
                safe_body = self._sanitize_body(request_body)
                logger.debug(
                    f"[{request_id}] Request body: {safe_body}"
                )

        # 记录请求耗时
        start_time = time.time()

        try:
            # 执行请求
            response = await call_next(request)

            # 计算耗时
            duration_ms = (time.time() - start_time) * 1000

            # 记录响应
            logger.info(
                f"[{request_id}] Response: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration_ms:.2f}ms | "
                f"IP: {client_ip}"
            )

            # 添加 request_id 到响应头
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # 计算耗时
            duration_ms = (time.time() - start_time) * 1000

            # 记录异常
            self._log_exception(request_id, request, exc, duration_ms, client_ip)

            # 重新抛出异常
            raise

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """获取客户端真实 IP"""
        # 优先从 X-Forwarded-For 获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个 IP (原始客户端)
            return forwarded_for.split(",")[0].strip()

        # 次优先从 X-Real-IP 获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 获取连接.remote_addr
        if request.client:
            return request.client.host

        return "unknown"

    async def _get_request_body(self, request: Request) -> Optional[str]:
        """获取请求体"""
        try:
            # 读取请求体
            body = await request.body()

            # 检查请求体大小
            if body and len(body) > self.MAX_BODY_SIZE:
                logger.warning(f"Request body too large: {len(body)} bytes (max: {self.MAX_BODY_SIZE})")
                return f"[Body too large: {len(body)} bytes]"

            # 尝试解码
            if body:
                return body.decode("utf-8")

            return None
        except Exception:
            return None

    @staticmethod
    def _sanitize_body(body: str) -> str:
        """敏感信息脱敏"""
        import re

        # 脱敏密码字段
        body = re.sub(
            r'("password":\s*")[^"]*(")',
            r'\1****\2',
            body,
            flags=re.IGNORECASE
        )

        # 脱敏 token 字段
        body = re.sub(
            r'("token":\s*")[^"]*(")',
            r'\1****\2',
            body,
            flags=re.IGNORECASE
        )

        # 脱敏 api_key 字段
        body = re.sub(
            r'("api_?key":\s*")[^"]*(")',
            r'\1****\2',
            body,
            flags=re.IGNORECASE
        )

        # 限制长度
        if len(body) > 500:
            body = body[:500] + "...(truncated)"

        return body

    def _log_exception(
        self,
        request_id: str,
        request: Request,
        exc: Exception,
        duration_ms: float,
        client_ip: str
    ):
        """记录异常日志"""
        # 获取异常类型和消息
        exc_type = type(exc).__name__
        exc_msg = str(exc)

        # 获取堆栈信息
        tb = traceback.format_exc()

        # 根据异常类型选择日志级别
        if "ValidationError" in exc_type or "ValueError" in exc_type:
            # 参数验证错误 - WARNING
            logger.warning(
                f"[{request_id}] Request validation failed: {request.method} {request.url.path} | "
                f"IP: {client_ip} | "
                f"Duration: {duration_ms:.2f}ms | "
                f"Error: {exc_type}: {exc_msg}"
            )
        elif "Permission" in exc_type or "Unauthorized" in exc_type:
            # 权限错误 - WARNING
            logger.warning(
                f"[{request_id}] Request unauthorized: {request.method} {request.url.path} | "
                f"IP: {client_ip} | "
                f"Duration: {duration_ms:.2f}ms | "
                f"Error: {exc_type}: {exc_msg}"
            )
        elif "NotFound" in exc_type:
            # 资源不存在 - INFO
            logger.info(
                f"[{request_id}] Resource not found: {request.method} {request.url.path} | "
                f"IP: {client_ip} | "
                f"Duration: {duration_ms:.2f}ms | "
                f"Error: {exc_type}: {exc_msg}"
            )
        else:
            # 其他异常 - ERROR
            logger.error(
                f"[{request_id}] Request error: {request.method} {request.url.path} | "
                f"IP: {client_ip} | "
                f"Duration: {duration_ms:.2f}ms | "
                f"Error: {exc_type}: {exc_msg}\n"
                f"Traceback:\n{tb}"
            )


# ============================================
# Router-level Logging Decorator
# ============================================

def log_request(func: Callable) -> Callable:
    """路由函数日志装饰器"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 生成请求ID
        request_id = str(uuid.uuid4())[:8]

        # 获取函数参数 (排除 db, current_user 等)
        safe_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in ["db", "current_user", "self"]
        }

        logger.debug(
            f"[{request_id}] Calling {func.__name__} with args: {safe_kwargs}"
        )

        try:
            result = await func(*args, **kwargs)

            logger.debug(
                f"[{request_id}] {func.__name__} returned successfully"
            )

            return result

        except Exception as e:
            logger.error(
                f"[{request_id}] {func.__name__} raised {type(e).__name__}: {str(e)}"
            )
            raise

    return wrapper
