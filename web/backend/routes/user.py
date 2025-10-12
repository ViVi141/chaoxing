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
import schemas
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


@router.post("/config/test-tiku", response_model=MessageResponse)
async def test_tiku_config(
    tiku_config: schemas.TikuConfig,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    测试题库配置
    
    验证AI题库或硅基流动的API配置是否正确
    """
    from api.answer import AI, SiliconFlow
    
    provider = tiku_config.provider
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未指定题库提供商"
        )
    
    # 仅支持AI和SiliconFlow的验证
    if provider not in ['AI', 'SiliconFlow']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"暂不支持验证{provider}题库，仅支持AI和SiliconFlow"
        )
    
    try:
        # 创建测试题目
        test_question = {
            'title': '中国的首都是哪里？',
            'type': 'single',
            'options': 'A. 北京\nB. 上海\nC. 广州\nD. 深圳'
        }
        
        # 根据提供商创建题库实例
        if provider == 'AI':
            # 验证必填字段
            if not tiku_config.endpoint or not tiku_config.key or not tiku_config.model:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="AI题库配置不完整，需要endpoint、key和model"
                )
            
            tiku = AI()
            config_dict = {
                'endpoint': tiku_config.endpoint,
                'key': tiku_config.key,
                'model': tiku_config.model,
                'min_interval_seconds': str(tiku_config.min_interval_seconds or 3),
                'http_proxy': tiku_config.http_proxy or '',
                'submit': 'false',
                'cover_rate': '0.9',
                'delay': '1.0',
                'true_list': '正确,对,√,是',
                'false_list': '错误,错,×,否,不对,不正确'
            }
            
        elif provider == 'SiliconFlow':
            # 验证必填字段
            if not tiku_config.siliconflow_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="硅基流动配置不完整，需要siliconflow_key"
                )
            
            tiku = SiliconFlow()
            config_dict = {
                'siliconflow_key': tiku_config.siliconflow_key,
                'siliconflow_model': tiku_config.siliconflow_model or 'deepseek-ai/DeepSeek-R1',
                'siliconflow_endpoint': tiku_config.siliconflow_endpoint or 'https://api.siliconflow.cn/v1/chat/completions',
                'min_interval_seconds': str(tiku_config.min_interval_seconds or 3),
                'submit': 'false',
                'cover_rate': '0.9',
                'delay': '1.0',
                'true_list': '正确,对,√,是',
                'false_list': '错误,错,×,否,不对,不正确'
            }
        
        # 配置题库
        tiku.config_set(config_dict)
        tiku._init_tiku()
        
        # 执行测试查询
        logger.info(f"用户{current_user.username}测试{provider}题库配置")
        answer = tiku._query(test_question)
        
        if answer:
            logger.info(f"{provider}题库测试成功，返回答案: {answer}")
            return {
                "message": f"✅ {provider}题库配置验证成功！",
                "detail": f"测试问题：{test_question['title']}\n返回答案：{answer}"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"题库返回空答案，请检查配置或API额度"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"{provider}题库测试失败: {error_msg}", exc_info=True)
        
        # 友好的错误提示
        if "API key" in error_msg or "401" in error_msg:
            detail = "API Key无效或已过期，请检查密钥是否正确"
        elif "timeout" in error_msg.lower():
            detail = "API请求超时，请检查网络连接或代理设置"
        elif "404" in error_msg:
            detail = "API端点不存在，请检查endpoint配置"
        elif "model" in error_msg.lower():
            detail = "模型不存在或不可用，请检查model配置"
        else:
            detail = f"测试失败: {error_msg[:200]}"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
