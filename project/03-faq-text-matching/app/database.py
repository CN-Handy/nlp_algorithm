"""
Database Module
数据库连接和会话管理 - 使用 pymysql 同步驱动
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.config import settings


# ============================================
# Engine
# ============================================

engine = create_engine(
    settings.database.mysql.url,
    echo=settings.database.mysql.echo,
    pool_size=settings.database.mysql.pool_size,
    max_overflow=settings.database.mysql.max_overflow,
    pool_recycle=settings.database.mysql.pool_recycle,
    pool_pre_ping=settings.database.mysql.pool_pre_ping,
    # 使用 StaticPool 用于简单场景
    poolclass=StaticPool if settings.app.debug else None,
)


# ============================================
# Session Factory
# ============================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================
# Base
# ============================================

Base = declarative_base()


# ============================================
# Session Dependency
# ============================================

def get_db() -> Generator[Session, None, None]:
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================
# Base Repository
# ============================================

class BaseRepository:
    """基础仓储类"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, model):
        """添加记录"""
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return model

    def delete(self, model):
        """删除记录"""
        self.session.delete(model)
        self.session.flush()

    def commit(self):
        """提交事务"""
        self.session.commit()

    def rollback(self):
        """回滚事务"""
        self.session.rollback()
