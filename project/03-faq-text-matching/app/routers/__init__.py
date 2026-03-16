"""
API Routers
路由模块
"""
from app.routers.categories import router as categories_router
from app.routers.faqs import router as faqs_router
from app.routers.service import router as service_router

__all__ = [
    "categories_router",
    "faqs_router",
    "service_router"
]
