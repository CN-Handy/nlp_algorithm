"""
Database Models
数据库模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ============================================
# Base
# ============================================

class Base(DeclarativeBase):
    """数据库基类"""
    pass


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


# ============================================
# Models
# ============================================

class Category(Base):
    """类目管理表"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env: Mapped[EnvEnum] = mapped_column(SQLEnum(EnvEnum), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-一级, 2-二级
    original_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 溯源 ID
    creator: Mapped[str] = mapped_column(String(64), nullable=False)
    modifier: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FAQ(Base):
    """FAQ 主表"""
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    env: Mapped[EnvEnum] = mapped_column(SQLEnum(EnvEnum), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    similar_queries: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    related_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[FAQStatusEnum] = mapped_column(SQLEnum(FAQStatusEnum), default=FAQStatusEnum.DISABLE)
    is_permanent: Mapped[bool] = mapped_column(Boolean, default=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    creator: Mapped[str] = mapped_column(String(64), nullable=False)
    modifier: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
