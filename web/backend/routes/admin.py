# -*- coding: utf-8 -*-
"""
管理员路由
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, Task, SystemLog, TaskLog
from schemas import (
    UserResponse, TaskResponse, StatisticsResponse,
    MessageResponse, PaginatedResponse, UserUpdate
)
from auth import require_admin
from config import settings
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


@router.get("/users", response_model=PaginatedResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="状态过滤"),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有用户列表（分页）
    
    管理员专用
    """
    query = select(User)
    
    # 搜索
    if search:
        query = query.where(
            (User.username.like(f"%{search}%")) |
            (User.email.like(f"%{search}%"))
        )
    
    # 角色过滤
    if role:
        query = query.where(User.role == role)
    
    # 状态过滤
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    query = query.order_by(desc(User.created_at))
    
    # 获取总数
    count_result = await db.execute(query)
    all_users = count_result.scalars().all()
    total = len(all_users)
    
    # 分页
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    users = result.scalars().all()
    
    return {
        "items": [user.to_dict() for user in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户详情
    
    管理员专用
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 预加载配置关系
    await db.refresh(user, ['config'])
    
    return user.to_dict(include_config=True)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息
    
    管理员专用
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新字段
    if user_update.email is not None:
        user.email = user_update.email
    
    if user_update.password is not None:
        user.set_password(user_update.password)
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"管理员{admin_user.username}更新用户{user.username}的信息")
    
    return user.to_dict()


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户
    
    管理员专用
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    username = user.username
    await db.delete(user)
    await db.commit()
    
    logger.warning(f"管理员{admin_user.username}删除了用户{username}")
    
    return {"message": f"用户{username}已删除"}


@router.get("/tasks", response_model=PaginatedResponse)
async def get_all_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有任务列表（分页）
    
    管理员专用
    """
    query = select(Task)
    
    if status:
        query = query.where(Task.status == status)
    
    if user_id:
        query = query.where(Task.user_id == user_id)
    
    query = query.order_by(desc(Task.created_at))
    
    # 获取总数
    count_result = await db.execute(query)
    all_tasks = count_result.scalars().all()
    total = len(all_tasks)
    
    # 分页
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    tasks = result.scalars().all()
    
    # 关联用户信息
    task_dicts = []
    for task in tasks:
        task_dict = task.to_dict()
        # 获取用户信息
        user_result = await db.execute(select(User).where(User.id == task.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            task_dict['username'] = user.username
        task_dicts.append(task_dict)
    
    return {
        "items": task_dicts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("/tasks/{task_id}/force-stop", response_model=MessageResponse)
async def force_stop_task(
    task_id: int,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    强制停止任务
    
    管理员专用
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status not in ["running", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务未在运行中"
        )
    
    # 取消Celery任务
    # if task.celery_task_id:
    #     from celery_app import app as celery_app
    #     celery_app.control.revoke(task.celery_task_id, terminate=True)
    
    task.status = "cancelled"
    from datetime import datetime
    task.end_time = datetime.utcnow()
    task.error_msg = f"由管理员{admin_user.username}强制停止"
    
    await db.commit()
    
    logger.warning(f"管理员{admin_user.username}强制停止任务{task_id}")
    
    return {"message": "任务已强制停止"}


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取统计数据
    
    管理员专用
    """
    # 用户统计
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar()
    
    # 任务统计
    total_tasks_result = await db.execute(select(func.count(Task.id)))
    total_tasks = total_tasks_result.scalar()
    
    running_tasks_result = await db.execute(
        select(func.count(Task.id)).where(Task.status == "running")
    )
    running_tasks = running_tasks_result.scalar()
    
    completed_tasks_result = await db.execute(
        select(func.count(Task.id)).where(Task.status == "completed")
    )
    completed_tasks = completed_tasks_result.scalar()
    
    failed_tasks_result = await db.execute(
        select(func.count(Task.id)).where(Task.status == "failed")
    )
    failed_tasks = failed_tasks_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_tasks": total_tasks,
        "running_tasks": running_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks
    }


@router.get("/logs")
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统日志
    
    管理员专用
    """
    query = select(SystemLog)
    
    if level:
        query = query.where(SystemLog.level == level)
    
    query = query.order_by(desc(SystemLog.created_at))
    
    # 获取总数
    count_result = await db.execute(query)
    all_logs = count_result.scalars().all()
    total = len(all_logs)
    
    # 分页
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    logs = result.scalars().all()
    
    return {
        "items": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

