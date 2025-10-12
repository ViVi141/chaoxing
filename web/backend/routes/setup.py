# -*- coding: utf-8 -*-
"""
安装向导路由
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from database import get_db
from models import User
from config_manager import ConfigManager
from api.logger import logger

router = APIRouter(prefix="/api/setup", tags=["setup"])


class SetupCheckResponse(BaseModel):
    """安装检查响应"""
    is_setup: bool
    has_admin: bool
    config_exists: bool


class SetupConfigRequest(BaseModel):
    """安装配置请求"""
    # 部署模式
    deploy_mode: str = Field(..., description="部署模式: simple/standard")
    
    # 系统配置
    platform_name: str = Field(default="超星学习通管理平台", description="平台名称")
    max_tasks_per_user: int = Field(default=3, ge=1, le=10, description="每用户最大并发任务数")
    task_timeout: int = Field(default=120, ge=30, le=360, description="任务超时时间(分钟)")
    enable_register: bool = Field(default=True, description="是否允许用户注册")
    
    # 数据库配置(标准模式)
    database_url: Optional[str] = Field(default=None, description="数据库URL")
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    
    # 管理员账号
    admin_username: Optional[str] = Field(default=None, description="管理员用户名")
    admin_password: Optional[str] = Field(default=None, description="管理员密码")
    admin_email: Optional[str] = Field(default=None, description="管理员邮箱")
    
    # 是否使用默认管理员
    use_default_admin: bool = Field(default=True, description="使用默认管理员账号")


class SetupConfigResponse(BaseModel):
    """安装配置响应"""
    success: bool
    message: str


@router.get("/check", response_model=SetupCheckResponse)
async def check_setup(db: AsyncSession = Depends(get_db)):
    """
    检查是否已完成安装
    """
    try:
        # 检查是否存在管理员
        result = await db.execute(
            select(User).where(User.is_admin == True).limit(1)
        )
        admin = result.scalar_one_or_none()
        
        # 检查配置文件
        config_exists = ConfigManager.config_exists()
        
        return SetupCheckResponse(
            is_setup=admin is not None and config_exists,
            has_admin=admin is not None,
            config_exists=config_exists
        )
    except Exception as e:
        logger.error(f"检查安装状态失败: {e}")
        raise HTTPException(status_code=500, detail="检查安装状态失败")


@router.post("/configure", response_model=SetupConfigResponse)
async def configure_setup(
    setup_data: SetupConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    配置系统并完成安装
    """
    try:
        # 1. 验证配置
        if setup_data.deploy_mode == "standard":
            if not setup_data.database_url or not setup_data.redis_url:
                raise HTTPException(
                    status_code=400,
                    detail="标准模式需要配置数据库和Redis"
                )
        
        # 2. 创建管理员账号(如果需要)
        if not setup_data.use_default_admin:
            if not setup_data.admin_username or not setup_data.admin_password:
                raise HTTPException(
                    status_code=400,
                    detail="请提供管理员用户名和密码"
                )
            
            # 检查管理员是否已存在
            result = await db.execute(
                select(User).where(User.username == setup_data.admin_username)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                raise HTTPException(
                    status_code=400,
                    detail=f"管理员用户名 '{setup_data.admin_username}' 已存在"
                )
            
            # 创建管理员
            from auth import get_password_hash
            admin = User(
                username=setup_data.admin_username,
                email=setup_data.admin_email,
                hashed_password=get_password_hash(setup_data.admin_password),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            await db.commit()
            logger.info(f"已创建管理员账号: {setup_data.admin_username}")
        
        # 3. 保存配置
        config = {
            'deploy_mode': setup_data.deploy_mode,
            'platform_name': setup_data.platform_name,
            'max_tasks_per_user': setup_data.max_tasks_per_user,
            'task_timeout': setup_data.task_timeout,
            'enable_register': setup_data.enable_register,
            'log_retention_days': 30,
            'enable_email_notification': False,
        }
        
        # 添加数据库配置(标准模式)
        if setup_data.deploy_mode == "standard":
            config['database_url'] = setup_data.database_url
            config['redis_url'] = setup_data.redis_url
        
        # 生成密钥
        keys = ConfigManager.generate_secret_keys()
        config.update(keys)
        
        # 保存配置文件
        if not ConfigManager.save_config(config):
            raise HTTPException(
                status_code=500,
                detail="保存配置失败"
            )
        
        # 应用配置
        ConfigManager.apply_config(config)
        
        logger.info("系统配置完成")
        
        return SetupConfigResponse(
            success=True,
            message="系统配置完成，正在跳转..."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"配置系统失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置系统失败: {str(e)}")


@router.get("/config")
async def get_config():
    """获取当前配置"""
    try:
        config = ConfigManager.load_config()
        if config is None:
            config = ConfigManager.get_default_config()
        
        # 移除敏感信息
        safe_config = {k: v for k, v in config.items() 
                      if k not in ['secret_key', 'jwt_secret_key', 'database_url', 'redis_url']}
        
        return safe_config
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败")

