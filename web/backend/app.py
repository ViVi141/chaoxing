# -*- coding: utf-8 -*-
"""
FastAPI主应用
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from database import engine, Base, init_db
from auth import init_default_admin
from config import settings
# 移除config_manager - 不再需要动态配置
# from config_manager import load_and_apply_config
from api.logger import logger

# 导入路由
from routes import auth_router, user_router, task_router, admin_router, websocket_router, system_config_router, course_router
# 移除安装向导路由 - 不再需要
# from routes.setup import router as setup_router


async def recover_interrupted_tasks():
    """恢复被中断的任务
    
    在应用启动时检查数据库中状态为 running 的任务，
    将它们标记为 failed，以便用户可以手动重试。
    """
    from sqlalchemy import select, update
    from models import Task
    from database import AsyncSessionLocal
    
    try:
        logger.info("🔍 检查被中断的任务...")
        
        # 使用异步会话
        async with AsyncSessionLocal() as session:
            # 查找所有 running 状态的任务
            result = await session.execute(
                select(Task).where(Task.status == "running")
            )
            interrupted_tasks = result.scalars().all()
            
            if interrupted_tasks:
                logger.warning(f"发现 {len(interrupted_tasks)} 个被中断的任务")
                
                # 使用update语句批量更新
                task_ids = [task.id for task in interrupted_tasks]
                
                # 记录任务信息
                for task in interrupted_tasks:
                    logger.info(f"  - 任务 {task.id} (用户 {task.user_id}) 将被标记为失败")
                
                # 批量更新任务状态
                await session.execute(
                    update(Task)
                    .where(Task.id.in_(task_ids))
                    .values(
                        status="failed",
                        error_msg="任务被意外中断（服务器重启或崩溃）",
                        end_time=datetime.utcnow()
                    )
                )
                
                await session.commit()
                logger.info(f"✅ 已处理 {len(interrupted_tasks)} 个被中断的任务")
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
    lifespan=lifespan
)

# 配置CORS（允许所有本地开发端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（移除安装向导）
# app.include_router(setup_router, tags=["安装向导"])  # 已移除
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/user", tags=["用户"])
app.include_router(task_router, prefix="/api/tasks", tags=["任务"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理员"])
app.include_router(system_config_router, prefix="/api/system-config", tags=["系统配置"])
app.include_router(course_router, prefix="/api/courses", tags=["课程"])
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
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "connected"
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

