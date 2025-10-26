# -*- coding: utf-8 -*-
"""
FastAPI主应用
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from routes.auth import init_default_admin
from config import settings

# 移除config_manager - 不再需要动态配置
# from config_manager import load_and_apply_config
from api.logger import logger

# 导入路由
from routes import (
    auth_router,
    user_router,
    task_router,
    admin_router,
    websocket_router,
    system_config_router,
    course_router,
)
from routes.migration import router as migration_router

# 移除安装向导路由 - 不再需要
# from routes.setup import router as setup_router


async def recover_interrupted_tasks():
    """恢复被中断的任务

    在应用启动时检查数据库中状态为 running 或 pending 的任务，
    自动重新提交这些任务到Celery队列继续执行。
    """
    from sqlalchemy import select
    from models import Task, User
    from database import AsyncSessionLocal

    try:
        logger.info("🔍 检查被中断的任务...")

        # 使用异步会话
        async with AsyncSessionLocal() as session:
            # 查找所有 running 或 pending 状态的任务（这些任务可能因系统崩溃而中断）
            result = await session.execute(
                select(Task).where(Task.status.in_(["running", "pending"]))
            )
            interrupted_tasks = result.scalars().all()

            if interrupted_tasks:
                logger.warning(
                    f"发现 {len(interrupted_tasks)} 个被中断的任务，准备自动恢复"
                )

                recovered_count = 0
                failed_count = 0

                for task in interrupted_tasks:
                    try:
                        # 获取用户信息
                        user_result = await session.execute(
                            select(User).where(User.id == task.user_id)
                        )
                        user = user_result.scalar_one_or_none()

                        if not user or not user.is_active:
                            # 用户不存在或已禁用，标记任务为失败
                            task.status = "failed"
                            task.error_msg = "任务恢复失败：用户不存在或已被禁用"
                            task.end_time = datetime.now(timezone.utc)
                            failed_count += 1
                            logger.warning(
                                f"  - 任务 {task.id} (用户 {task.user_id}): 用户不可用，标记为失败"
                            )
                            continue

                        # 重置任务状态为pending，准备重新执行
                        task.status = "pending"
                        task.progress = 0
                        task.celery_task_id = None  # 清除旧的Celery任务ID
                        task.error_msg = "系统重启后自动恢复任务"
                        task.start_time = None  # 清除开始时间，等待重新开始

                        await session.commit()

                        # 重新提交任务到Celery（需要传递task_id和user_id）
                        from tasks.study_tasks import start_study_task

                        celery_task = start_study_task.delay(task.id, task.user_id)

                        # 更新Celery任务ID
                        task.celery_task_id = celery_task.id
                        task.status = "running"
                        task.start_time = datetime.now(timezone.utc)
                        await session.commit()

                        recovered_count += 1
                        logger.info(
                            f"  ✅ 任务 {task.id} (用户 {user.username}): 已自动恢复并重新提交"
                        )

                    except Exception as task_error:
                        # 单个任务恢复失败，标记为失败状态
                        task.status = "failed"
                        task.error_msg = f"任务恢复失败: {str(task_error)}"
                        task.end_time = datetime.now(timezone.utc)
                        await session.commit()
                        failed_count += 1
                        logger.error(f"  ❌ 任务 {task.id}: 恢复失败 - {task_error}")

                logger.info(
                    f"✅ 任务恢复完成: 成功 {recovered_count} 个, 失败 {failed_count} 个"
                )
            else:
                logger.info("✅ 没有发现被中断的任务")

    except Exception as e:
        logger.error(f"❌ 恢复被中断任务时出错: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 应用启动中...")

    # 确保 data 目录存在
    from pathlib import Path

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ 数据目录已就绪: {data_dir.absolute()}")

    # 配置已从 .env 加载（不再需要动态加载）
    logger.info(f"✅ 配置已从 .env 加载")
    logger.info(f"   数据库: {settings.DATABASE_URL}")
    logger.info(f"   部署模式: {settings.DEPLOY_MODE}")

    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 初始化默认管理员
    await init_default_admin()

    # 恢复被中断的任务
    await recover_interrupted_tasks()

    logger.info("✅ 应用启动完成")

    yield

    # 关闭时
    logger.info("👋 应用关闭中...")
    await engine.dispose()
    logger.info("✅ 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="超星学习通多用户管理平台",
    description="支持多用户同时注册登录并管理刷课任务的Web平台",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# 配置CORS（根据环境动态设置）
cors_origins = ["*"] if settings.DEBUG else settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # 生产环境限制源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

logger.info(
    f"CORS配置: DEBUG={settings.DEBUG}, Origins={cors_origins if settings.DEBUG else '已配置'}"
)

# 注册路由（移除安装向导）
# app.include_router(setup_router, tags=["安装向导"])  # 已移除
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/user", tags=["用户"])
app.include_router(task_router, prefix="/api/tasks", tags=["任务"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理员"])
app.include_router(system_config_router, prefix="/api/system-config", tags=["系统配置"])
app.include_router(course_router, prefix="/api/courses", tags=["课程"])
app.include_router(migration_router, prefix="/api/migration", tags=["数据库迁移"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

# 静态文件服务（前端构建文件）
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "超星学习通多用户管理平台 API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "database": "connected"}


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"error": "服务器内部错误", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("🚀 超星学习通Web平台启动中...")
    logger.info(f"📍 监听: {settings.HOST}:{settings.PORT}")
    logger.info(f"🗄️  模式: {settings.DEPLOY_MODE}")
    logger.info("=" * 60)
    logger.info("🎁 本项目是开源免费软件 (GPL-3.0)")
    logger.info("⚠️  请勿用于强制收费或商业化运营")
    logger.info("💡 GitHub: https://github.com/ViVi141/chaoxing")
    logger.info("=" * 60)

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
