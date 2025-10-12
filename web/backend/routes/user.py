# -*- coding: utf-8 -*-
"""
用户相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, UserConfig
from schemas import (
    UserConfigResponse, UserConfigUpdate, UserUpdate,
    MessageResponse
)
from auth import get_current_active_user
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger
from api.secure_config import SecureConfig

router = APIRouter()


@router.get("/config", response_model=UserConfigResponse)
async def get_user_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户配置
    """
    # 预加载配置关系
    await db.refresh(current_user, ['config'])
    
    # 如果配置不存在，创建默认配置
    if not current_user.config:
        config = UserConfig(user_id=current_user.id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    else:
        await db.refresh(current_user.config)
    
    return current_user.config.to_dict()


@router.put("/config", response_model=UserConfigResponse)
async def update_user_config(
    config_update: UserConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户配置
    
    - 超星账号配置
    - 播放倍速
    - 题库配置
    - 通知配置
    """
    # 预加载配置关系
    await db.refresh(current_user, ['config'])
    
    # 获取或创建配置
    if not current_user.config:
        config = UserConfig(user_id=current_user.id)
        db.add(config)
    else:
        config = current_user.config
    
    # 更新基础配置
    if config_update.cx_username is not None:
        config.cx_username = config_update.cx_username
    
    # 加密存储密码
    if config_update.cx_password is not None:
        secure_config = SecureConfig()
        encrypted_password = secure_config.encrypt_password(config_update.cx_password)
        if encrypted_password:
            config.cx_password_encrypted = encrypted_password
        else:
            logger.warning(f"用户{current_user.id}的密码加密失败，保存明文（不推荐）")
            config.cx_password_encrypted = config_update.cx_password
    
    if config_update.use_cookies is not None:
        config.use_cookies = config_update.use_cookies
    
    if config_update.speed is not None:
        config.speed = config_update.speed
    
    if config_update.notopen_action is not None:
        config.notopen_action = config_update.notopen_action
    
    # 更新题库配置
    if config_update.tiku_config is not None:
        config.set_tiku_config(config_update.tiku_config.dict())
    
    # 更新通知配置
    if config_update.notification_config is not None:
        config.set_notification_config(config_update.notification_config.dict())
    
    await db.commit()
    await db.refresh(config)
    
    logger.info(f"用户{current_user.username}更新了配置")
    
    return config.to_dict()


@router.put("/password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6字符）
    """
    # 验证旧密码
    if not current_user.check_password(old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 验证新密码
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少6个字符"
        )
    
    # 更新密码
    current_user.set_password(new_password)
    await db.commit()
    
    logger.info(f"用户{current_user.username}修改了密码")
    
    return {"message": "密码修改成功"}


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户详细信息（包括统计数据）
    """
    # 预加载配置关系
    await db.refresh(current_user, ['config'])
    
    # 获取任务统计
    from models import Task
    
    # 总任务数
    result = await db.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    all_tasks = result.scalars().all()
    
    task_stats = {
        "total": len(all_tasks),
        "pending": len([t for t in all_tasks if t.status == "pending"]),
        "running": len([t for t in all_tasks if t.status == "running"]),
        "completed": len([t for t in all_tasks if t.status == "completed"]),
        "failed": len([t for t in all_tasks if t.status == "failed"]),
        "cancelled": len([t for t in all_tasks if t.status == "cancelled"]),
    }
    
    return {
        "user": current_user.to_dict(include_config=True),
        "statistics": {
            "tasks": task_stats
        }
    }


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除账号（需要密码确认）
    
    ⚠️ 此操作不可逆，将删除所有相关数据
    """
    # 验证密码
    if not current_user.check_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )
    
    # 删除用户（会级联删除配置和任务）
    await db.delete(current_user)
    await db.commit()
    
    logger.warning(f"用户{current_user.username}删除了账号")
    
    return {"message": "账号已删除"}

