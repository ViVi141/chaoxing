# -*- coding: utf-8 -*-
"""
同步数据库连接（用于Celery任务）
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

# 将异步数据库URL转换为同步URL
sync_database_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace(
    "+asyncpg", "+psycopg2"
)

# 创建同步引擎
if settings.DEPLOY_MODE == "simple":
    # SQLite
    sync_engine = create_engine(
        sync_database_url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL
    sync_engine = create_engine(
        sync_database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# 创建同步会话工厂
SyncSessionLocal = sessionmaker(
    bind=sync_engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def get_sync_db() -> Session:
    """获取同步数据库会话"""
    db = SyncSessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise
