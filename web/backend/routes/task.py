# -*- coding: utf-8 -*-
"""
任务管理路由
"""
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import User, Task, TaskLog
from schemas import (
    TaskCreate, TaskResponse, TaskUpdate,
    MessageResponse, PaginatedResponse, TaskLogResponse
)
from auth import get_current_active_user
from config import settings
from config_manager import config_manager
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(settings.PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="每页数量"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务列表（分页）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量
    - **status**: 状态过滤（可选）
    """
    # 构建查询
    query = select(Task).where(Task.user_id == current_user.id)
    
    if status:
        query = query.where(Task.status == status)
    
    # 按创建时间倒序
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
    
    return {
        "items": [task.to_dict() for task in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新任务
    
    - **name**: 任务名称
    - **course_ids**: 课程ID列表（可选，为空则学习所有课程）
    """
    # 检查并发任务数限制（优先使用数据库配置）
    max_tasks = await config_manager.get_config(
        db,
        'max_concurrent_tasks_per_user',
        settings.MAX_CONCURRENT_TASKS_PER_USER
    )
    
    result = await db.execute(
        select(Task).where(
            Task.user_id == current_user.id,
            Task.status.in_(["pending", "running"])
        )
    )
    active_tasks = result.scalars().all()
    
    if len(active_tasks) >= max_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"同时运行的任务数已达上限({max_tasks})"
        )
    
    # 创建任务
    task = Task(
        user_id=current_user.id,
        name=task_data.name,
        status="pending"
    )
    
    if task_data.course_ids:
        task.set_course_ids(task_data.course_ids)
        task.total_courses = len(task_data.course_ids)
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"用户{current_user.username}创建任务: {task.name} (ID: {task.id})")
    
    return task.to_dict()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务详情（包含日志）
    """
    # 使用selectinload预加载日志关系
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.logs))
        .where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    logger.debug(f"任务{task_id}包含{len(task.logs)}条日志")
    
    return task.to_dict(include_logs=True)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新任务信息
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 更新字段
    if task_update.name is not None:
        task.name = task_update.name
    
    if task_update.status is not None:
        task.status = task_update.status
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"用户{current_user.username}更新任务{task_id}")
    
    return task.to_dict()


@router.post("/{task_id}/start", response_model=MessageResponse)
async def start_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    启动任务
    
    将任务提交到Celery队列执行
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status not in ["pending", "paused", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法启动"
        )
    
    # 检查用户配置
    await db.refresh(current_user, ['config'])
    if not current_user.config or not current_user.config.cx_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置超星账号"
        )
    
    # 提交到Celery
    from tasks.study_tasks import start_study_task
    celery_task = start_study_task.delay(task.id, current_user.id)
    task.celery_task_id = celery_task.id
    
    task.status = "running"
    task.start_time = datetime.now(timezone.utc)
    
    await db.commit()
    
    logger.info(f"用户{current_user.username}启动任务{task_id}")
    
    return {"message": "任务已启动", "detail": f"任务ID: {task.id}"}


@router.post("/{task_id}/pause", response_model=MessageResponse)
async def pause_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    暂停任务
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能暂停运行中的任务"
        )
    
    # 取消Celery任务
    if task.celery_task_id:
        try:
            from celery_app import app as celery_app
            celery_app.control.revoke(task.celery_task_id, terminate=True)
            logger.info(f"已终止Celery任务: {task.celery_task_id}")
        except Exception as e:
            logger.warning(f"无法终止Celery任务 {task.celery_task_id}: {e}")
    
    task.status = "paused"
    await db.commit()
    
    logger.info(f"用户{current_user.username}暂停任务{task_id}")
    
    return {"message": "任务已暂停"}


@router.post("/{task_id}/retry", response_model=MessageResponse)
async def retry_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    重试失败的任务
    
    重置任务状态并重新提交到Celery队列
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status not in ["failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，无法重试"
        )
    
    # 检查用户配置
    await db.refresh(current_user, ['config'])
    if not current_user.config or not current_user.config.cx_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置超星账号"
        )
    
    # 重置任务状态
    task.status = "pending"
    task.progress = 0
    task.error_msg = None
    task.start_time = None
    task.end_time = None
    
    # 提交到Celery
    from tasks.study_tasks import start_study_task
    celery_task = start_study_task.delay(task.id, current_user.id)
    task.celery_task_id = celery_task.id
    task.status = "running"
    task.start_time = datetime.now(timezone.utc)
    
    await db.commit()
    
    logger.info(f"用户{current_user.username}重试任务{task_id}")
    
    return {"message": "任务已重新启动", "detail": f"任务ID: {task.id}"}


@router.post("/{task_id}/resume", response_model=MessageResponse)
async def resume_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    恢复暂停的任务
    
    将暂停的任务重新提交到Celery队列执行
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态为{task.status}，只能恢复暂停的任务"
        )
    
    # 检查用户配置
    await db.refresh(current_user, ['config'])
    if not current_user.config or not current_user.config.cx_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置超星账号"
        )
    
    # 提交到Celery
    from tasks.study_tasks import start_study_task
    celery_task = start_study_task.delay(task.id, current_user.id)
    task.celery_task_id = celery_task.id
    
    task.status = "running"
    # 不重置start_time，保留原来的开始时间
    
    await db.commit()
    
    logger.info(f"用户{current_user.username}恢复任务{task_id}")
    
    return {"message": "任务已恢复", "detail": f"任务ID: {task.id}"}


@router.post("/{task_id}/cancel", response_model=MessageResponse)
async def cancel_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消任务
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已完成或已取消"
        )
    
    # 取消Celery任务
    if task.celery_task_id:
        try:
            from celery_app import celery_app
            celery_app.control.revoke(task.celery_task_id, terminate=True)
            logger.info(f"已终止Celery任务: {task.celery_task_id}")
        except Exception as e:
            logger.warning(f"无法终止Celery任务 {task.celery_task_id}: {e}")
    
    task.status = "cancelled"
    task.end_time = datetime.now(timezone.utc)
    await db.commit()
    
    logger.info(f"用户{current_user.username}取消任务{task_id}")
    
    return {"message": "任务已取消"}


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除任务
    
    只能删除已完成、已取消或失败的任务
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status in ["running", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除运行中或等待中的任务，请先取消"
        )
    
    await db.delete(task)
    await db.commit()
    
    logger.info(f"用户{current_user.username}删除任务{task_id}")
    
    return {"message": "任务已删除"}


@router.get("/{task_id}/logs", response_model=List[TaskLogResponse])
async def get_task_logs(
    task_id: int,
    limit: int = Query(100, ge=1, le=1000, description="日志数量限制"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务日志
    """
    # 验证任务所有权
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 获取日志
    logs_result = await db.execute(
        select(TaskLog)
        .where(TaskLog.task_id == task_id)
        .order_by(desc(TaskLog.created_at))
        .limit(limit)
    )
    logs = logs_result.scalars().all()
    
    return [log.to_dict() for log in logs]

