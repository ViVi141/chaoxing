# -*- coding: utf-8 -*-
"""
数据库连接和会话管理（异步）
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import settings

# 确保DATABASE_URL使用异步驱动
def ensure_async_driver(database_url: str) -> str:
    """确保数据库URL使用异步驱动"""
    # 如果是PostgreSQL URL但没有指定异步驱动，使用asyncpg
    if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("postgresql+psycopg2://"):
        # 如果使用了psycopg2（同步驱动），替换为asyncpg
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    
    # 如果是SQLite URL但没有指定异步驱动，使用aiosqlite
    if database_url.startswith("sqlite://") and "+aiosqlite" not in database_url:
        database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
    
    return database_url

# 获取数据库URL（优先使用环境变量，用于测试）
database_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
database_url = ensure_async_driver(database_url)

# 根据部署模式创建异步引擎
if settings.DEPLOY_MODE == "simple":
    # 简单模式：SQLite（不需要连接池）
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False},  # SQLite特定配置
    )
else:
    # 标准模式：PostgreSQL（使用连接池）
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,  # 连接池健康检查
        pool_size=10,
        max_overflow=20,
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（依赖注入）

    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """删除所有表（仅用于测试）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
