"""
FastAPI Application
主应用入口
"""
import sys; sys.path.append("./")

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import categories_router, faqs_router, service_router
from app.logging_config import logger
from app.middleware import RequestLoggingMiddleware


# ============================================
# Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info(f"Starting {settings.app.name} v{settings.app.version}")

    # 初始化 Elasticsearch 索引
    try:
        from app.services.elasticsearch import ESIndex
        ESIndex.create_index()
        logger.info("Elasticsearch index initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Elasticsearch index: {e}")

    # 验证 Embedding 模型配置
    try:
        from app.services.embedding import EmbeddingClient
        # 预热模型 (首次调用会加载模型)
        EmbeddingClient.encode_one("test")
        logger.info("Embedding model verified")
    except Exception as e:
        logger.warning(f"Failed to verify Embedding model: {e}")
    print(f"Starting {settings.app.name} v{settings.app.version}")

    yield

    # Shutdown
    logger.info("Application shutting down...")
    # Close ES client
    try:
        from app.services.elasticsearch import ESClient
        ESClient.close()
    except Exception:
        pass
    logger.info("Application shutdown complete")
    print("Application shutdown")


# ============================================
# App
# ============================================

app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.app.version,
    docs_url=settings.api.docs_url,
    redoc_url=settings.api.redoc_url,
    lifespan=lifespan,
)


# ============================================
# Middleware
# ============================================

# 请求/响应日志 (最外层)
app.add_middleware(RequestLoggingMiddleware)

# CORS
if settings.cors.enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )


# ============================================
# Exception Handler
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    # 获取客户端 IP
    client_ip = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", "unknown"))

    logger.error(
        f"Unhandled exception: {request.method} {request.url.path} | "
        f"IP: {client_ip}",
        exc_info=True
    )

    return JSONResponse(
        status_code=200,  # 保持 200，使用业务 code 返回错误
        content={
            "code": 500,
            "msg": "Internal server error",
            "data": None,
            "time": None
        }
    )


# ============================================
# Routers
# ============================================

# Admin APIs
app.include_router(
    categories_router,
    prefix=settings.api.prefix,
)
app.include_router(
    faqs_router,
    prefix=settings.api.prefix,
)

# Service APIs
app.include_router(
    service_router,
    prefix=settings.api.prefix,
)


# ============================================
# Health Check
# ============================================

@app.get("/health")
async def health_check():
    """健康检查"""
    from datetime import datetime
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "status": "ok",
            "version": settings.app.version,
        },
        "time": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """根路径"""
    from datetime import datetime
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "name": settings.app.name,
            "version": settings.app.version,
            "docs": settings.api.docs_url,
        },
        "time": datetime.utcnow().isoformat()
    }


# ============================================
# Run
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
    )
