# -*- coding: utf-8 -*-
"""
认证相关路由
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, UserConfig
from schemas import UserCreate, UserLogin, UserResponse, Token, MessageResponse
from auth import AuthService, get_current_active_user
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名（3-80字符）
    - **password**: 密码（至少6字符）
    - **email**: 邮箱（可选）
    """
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        role="user"
    )
    user.set_password(user_data.password)
    
    # 创建用户配置
    config = UserConfig(user=user)
    
    db.add(user)
    db.add(config)
    await db.commit()
    await db.refresh(user)
    
    # 生成令牌
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "role": user.role}
    )
    
    logger.info(f"新用户注册: {user.username} (ID: {user.id})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    使用OAuth2密码模式，Content-Type: application/x-www-form-urlencoded
    
    - **username**: 用户名
    - **password**: 密码
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # 生成令牌
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "role": user.role}
    )
    
    logger.info(f"用户登录: {user.username} (ID: {user.id})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    用户登出
    
    注意：JWT是无状态的，实际的登出需要在客户端删除令牌
    """
    logger.info(f"用户登出: {current_user.username}")
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息
    """
    # 预加载配置
    await db.refresh(current_user, ['config'])
    return current_user.to_dict(include_config=True)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    刷新访问令牌
    """
    access_token = AuthService.create_access_token(
        data={"sub": current_user.id, "role": current_user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": current_user.to_dict()
    }

