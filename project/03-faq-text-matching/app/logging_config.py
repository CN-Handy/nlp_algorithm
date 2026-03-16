"""
Logging Configuration
日志配置 - 按级别分离、时间滚动、14天保留
"""
import sys
from pathlib import Path
from datetime import datetime

from loguru import logger

from app.config import settings


# ============================================
# Log Directory
# ============================================

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)


# ============================================
# Remove Default Handler
# ============================================

logger.remove()


# ============================================
# Console Handler (DEBUG, INFO, WARNING, ERROR)
# ============================================

logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
    backtrace=True,
    diagnose=True,
)


# ============================================
# Debug Log Handler
# ============================================

logger.add(
    LOG_DIR / "debug_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="1 day",           # 每天滚动
    retention="14 days",        # 保留14天
    compression="gz",           # 压缩旧日志
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)


# ============================================
# Info Log Handler
# ============================================

logger.add(
    LOG_DIR / "info_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="INFO",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
)


# ============================================
# Warning Log Handler
# ============================================

logger.add(
    LOG_DIR / "warning_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="WARNING",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
    backtrace=True,
)


# ============================================
# Error Log Handler
# ============================================

logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)


# ============================================
# Critical Log Handler
# ============================================

logger.add(
    LOG_DIR / "critical_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="CRITICAL",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)


# ============================================
# Access Log Handler (HTTP)
# ============================================

logger.add(
    LOG_DIR / "access_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    level="INFO",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
    filter=lambda record: "access" in record["extra"],
)


# ============================================
# Database Log Handler
# ============================================

logger.add(
    LOG_DIR / "database_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="1 day",
    retention="14 days",
    compression="gz",
    encoding="utf-8",
    filter=lambda record: "database" in record["extra"],
)


# ============================================
# Set Level
# ============================================

logger.level("DEBUG", color="<cyan>")
logger.level("INFO", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<red><bold>")


# ============================================
# Convenience Methods
# ============================================

def get_logger(name: str = None):
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Export logger
__all__ = ["logger", "get_logger"]


# ============================================
# Usage Examples
# ============================================

if __name__ == "__main__":
    # Test logging
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # With context
    logger.bind(access=True).info("GET /api/v1/health")
    logger.bind(database=True).info("SELECT * FROM users")
