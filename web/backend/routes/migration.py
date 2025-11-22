# -*- coding: utf-8 -*-
"""
数据库迁移管理路由 - 管理员专用
支持SQLite迁移到PostgreSQL + Redis
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import asyncio
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from pydantic import BaseModel, Field
import redis as redis_client

from models import User
from routes.auth import require_admin
from api.logger import logger
from database_migration import DatabaseMigrator, DatabaseMigrationError

router = APIRouter()

# 迁移状态存储（简单实现，生产环境建议用Redis）
migration_status = {
    "is_running": False,
    "current_step": "",
    "progress": 0,
    "message": "",
    "result": None,
    "error": None,
}


# ============= Schemas =============


class DatabaseConfigTest(BaseModel):
    """数据库配置测试"""

    database_url: str = Field(..., description="数据库URL")

    class Config:
        json_schema_extra = {
            "example": {
                "database_url": "postgresql+asyncpg://user:pass@localhost:5432/chaoxing_db"
            }
        }


class RedisConfigTest(BaseModel):
    """Redis配置测试"""

    redis_url: str = Field(..., description="Redis URL")

    class Config:
        json_schema_extra = {
            "example": {"redis_url": "redis://:password@localhost:6379/0"}
        }


class MigrationRequest(BaseModel):
    """迁移请求"""

    target_database_url: str = Field(..., description="目标PostgreSQL数据库URL")
    redis_url: str = Field(..., description="Redis URL")
    confirm: bool = Field(default=False, description="确认执行迁移")

    class Config:
        json_schema_extra = {
            "example": {
                "target_database_url": "postgresql+asyncpg://chaoxing_user:password@localhost:5432/chaoxing_db",
                "redis_url": "redis://:password@localhost:6379/0",
                "confirm": True,
            }
        }


class MigrationStatus(BaseModel):
    """迁移状态"""

    is_running: bool
    current_step: str
    progress: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None


# ============= Helper Functions =============


async def test_postgresql_connection(database_url: str) -> tuple[bool, str]:
    """测试PostgreSQL连接"""
    try:
        engine = create_async_engine(database_url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            await engine.dispose()
            return True, f"连接成功: {version}"
    except Exception as e:
        return False, f"连接失败: {str(e)}"


def test_redis_connection(redis_url: str) -> tuple[bool, str]:
    """测试Redis连接"""
    try:
        # 解析Redis URL
        r = redis_client.from_url(redis_url, decode_responses=True)

        # 测试连接
        r.ping()

        # 获取Redis版本
        info = r.info()
        version = info.get("redis_version", "unknown")

        r.close()
        return True, f"连接成功: Redis {version}"
    except Exception as e:
        return False, f"连接失败: {str(e)}"


def progress_callback(step: str, progress: int, message: str):
    """进度回调函数"""
    global migration_status
    migration_status["current_step"] = step
    migration_status["progress"] = progress
    migration_status["message"] = message
    logger.info(f"[迁移进度 {progress}%] {step}: {message}")


async def run_migration_task(
    source_db_url: str, target_db_url: str, redis_url: str, admin_user_id: int
):
    """运行迁移任务（后台任务）"""
    global migration_status

    try:
        migration_status["is_running"] = True
        migration_status["error"] = None
        migration_status["result"] = None

        # 创建迁移器
        migrator = DatabaseMigrator(
            source_db_url=source_db_url,
            target_db_url=target_db_url,
            progress_callback=progress_callback,
        )

        # 执行迁移
        env_file_path = Path(__file__).parent.parent / ".env"
        backup_path = Path(__file__).parent.parent / "backups"

        result = await migrator.run_full_migration(
            backup_path=str(backup_path),
            env_file_path=str(env_file_path),
            redis_url=redis_url,
        )

        migration_status["result"] = result
        migration_status["message"] = "迁移成功完成！"
        logger.info(f"✅ 管理员 {admin_user_id} 完成数据库迁移")

    except Exception as e:
        migration_status["error"] = str(e)
        migration_status["message"] = f"迁移失败: {str(e)}"
        logger.error(f"❌ 数据库迁移失败: {e}")

    finally:
        migration_status["is_running"] = False


# ============= API Endpoints =============


@router.post("/test-postgresql")
async def test_postgresql(
    config: DatabaseConfigTest, admin_user: User = Depends(require_admin)
):
    """
    测试PostgreSQL数据库连接

    管理员专用
    """
    logger.info(f"管理员 {admin_user.username} 测试PostgreSQL连接")

    success, message = await test_postgresql_connection(config.database_url)

    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.post("/test-redis")
async def test_redis(
    config: RedisConfigTest, admin_user: User = Depends(require_admin)
):
    """
    测试Redis连接

    管理员专用
    """
    logger.info(f"管理员 {admin_user.username} 测试Redis连接")

    success, message = test_redis_connection(config.redis_url)

    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.get("/status")
async def get_migration_status(admin_user: User = Depends(require_admin)):
    """
    获取迁移状态

    管理员专用
    """
    return migration_status


@router.get("/current-config")
async def get_current_config(admin_user: User = Depends(require_admin)):
    """
    获取当前数据库配置

    管理员专用
    """
    from config import settings

    # 检测当前使用的数据库类型
    db_type = "SQLite" if "sqlite" in settings.DATABASE_URL.lower() else "PostgreSQL"
    broker_type = "文件系统" if "filesystem" in settings.CELERY_BROKER_URL else "Redis"

    return {
        "deploy_mode": settings.DEPLOY_MODE,
        "database_type": db_type,
        "database_url": settings.DATABASE_URL,
        "broker_type": broker_type,
        "celery_broker": settings.CELERY_BROKER_URL,
        "celery_result_backend": settings.CELERY_RESULT_BACKEND,
    }


@router.post("/start")
async def start_migration(
    request: MigrationRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
):
    """
    开始数据库迁移

    管理员专用
    警告：此操作将修改系统配置，完成后需要重启服务
    """
    global migration_status

    # 检查是否已有迁移在运行
    if migration_status["is_running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已有迁移任务在运行中"
        )

    # 确认标志
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请确认执行迁移操作（设置 confirm=true）",
        )

    logger.warning(f"⚠️ 管理员 {admin_user.username} 启动数据库迁移")

    # 获取当前配置
    from config import settings

    source_db_url = settings.DATABASE_URL

    # 先测试连接
    pg_success, pg_message = await test_postgresql_connection(
        request.target_database_url
    )
    if not pg_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PostgreSQL连接失败: {pg_message}",
        )

    redis_success, redis_message = test_redis_connection(request.redis_url)
    if not redis_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Redis连接失败: {redis_message}",
        )

    # 在后台运行迁移任务
    background_tasks.add_task(
        run_migration_task,
        source_db_url,
        request.target_database_url,
        request.redis_url,
        admin_user.id,
    )

    return {
        "message": "迁移任务已启动，请通过 /status 接口查看进度",
        "warning": "迁移完成后需要重启服务才能生效",
    }


@router.post("/reset-status")
async def reset_migration_status(admin_user: User = Depends(require_admin)):
    """
    重置迁移状态（用于清除错误状态）

    管理员专用
    """
    global migration_status

    if migration_status["is_running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="迁移任务正在运行，无法重置"
        )

    migration_status = {
        "is_running": False,
        "current_step": "",
        "progress": 0,
        "message": "",
        "result": None,
        "error": None,
    }

    logger.info(f"管理员 {admin_user.username} 重置迁移状态")

    return {"message": "迁移状态已重置"}


@router.get("/restart-command")
async def get_restart_command(admin_user: User = Depends(require_admin)):
    """
    获取服务重启命令

    管理员专用
    """
    import platform

    system = platform.system()

    if system == "Windows":
        commands = {
            "stop": [
                'taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*"',
                "taskkill /F /IM celery.exe",
            ],
            "start": [
                "cd web/backend && start python app.py",
                "cd web/backend && start celery -A celery_app worker --loglevel=info",
            ],
            "note": "Windows环境建议手动重启服务",
        }
    else:  # Linux/Mac
        commands = {
            "systemd": [
                "sudo systemctl restart chaoxing-backend",
                "sudo systemctl restart chaoxing-celery",
            ],
            "supervisor": [
                "sudo supervisorctl restart chaoxing-backend",
                "sudo supervisorctl restart chaoxing-celery",
            ],
            "docker": ["docker-compose restart backend celery"],
            "manual": [
                "pkill -f 'python app.py'",
                "pkill -f 'celery -A celery_app'",
                "cd web/backend && python app.py &",
                "cd web/backend && celery -A celery_app worker --loglevel=info &",
            ],
        }

    return {
        "system": system,
        "commands": commands,
        "warning": "迁移完成后必须重启服务才能使用新数据库",
    }
