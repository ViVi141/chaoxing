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
    UserResponse,
    TaskResponse,
    StatisticsResponse,
    MessageResponse,
    PaginatedResponse,
    UserUpdate,
)
from routes.auth import require_admin
from config import settings
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


def escape_like_pattern(pattern: str) -> str:
    """
    转义LIKE模式中的特殊字符，防止LIKE注入

    Args:
        pattern: 原始搜索模式

    Returns:
        转义后的模式
    """
    if not pattern:
        return pattern
    # 转义反斜杠、百分号和下划线
    return pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("/users", response_model=PaginatedResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="状态过滤"),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有用户列表（分页）

    管理员专用
    """
    query = select(User)

    # 搜索（防止LIKE注入）
    if search:
        escaped_search = escape_like_pattern(search)
        query = query.where(
            (User.username.like(f"%{escaped_search}%", escape="\\"))
            | (User.email.like(f"%{escaped_search}%", escape="\\"))
        )

    # 角色过滤
    if role:
        query = query.where(User.role == role)

    # 状态过滤
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = query.order_by(desc(User.created_at))

    # 优化：使用count()查询总数，而非加载所有数据
    count_query = select(func.count()).select_from(User)

    # 应用相同的过滤条件
    if search:
        escaped_search = escape_like_pattern(search)
        count_query = count_query.where(
            (User.username.like(f"%{escaped_search}%", escape="\\"))
            | (User.email.like(f"%{escaped_search}%", escape="\\"))
        )
    if role:
        count_query = count_query.where(User.role == role)
    if is_active is not None:
        count_query = count_query.where(User.is_active == is_active)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分页查询数据
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    users = result.scalars().all()

    return {
        "items": [user.to_dict() for user in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户详情

    管理员专用
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 预加载配置关系
    await db.refresh(user, ["config"])

    return user.to_dict(include_config=True)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    更新用户信息

    管理员专用
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

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
    db: AsyncSession = Depends(get_db),
):
    """
    删除用户

    管理员专用
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己的账号"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

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
    db: AsyncSession = Depends(get_db),
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

    # 优化：使用count()查询总数
    count_query = select(func.count()).select_from(Task)
    if status:
        count_query = count_query.where(Task.status == status)
    if user_id:
        count_query = count_query.where(Task.user_id == user_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分页查询数据
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
            task_dict["username"] = user.username
        task_dicts.append(task_dict)

    return {
        "items": task_dicts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/tasks/{task_id}/force-stop", response_model=MessageResponse)
async def force_stop_task(
    task_id: int,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    强制停止任务

    管理员专用
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if task.status not in ["running", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="任务未在运行中"
        )

    # 取消Celery任务
    if task.celery_task_id:
        try:
            from celery_app import app as celery_app

            celery_app.control.revoke(task.celery_task_id, terminate=True)
            logger.info(f"已终止Celery任务: {task.celery_task_id}")
        except Exception as e:
            logger.warning(f"无法终止Celery任务 {task.celery_task_id}: {e}")

    task.status = "cancelled"
    from datetime import datetime, timezone

    task.end_time = datetime.now(timezone.utc)
    task.error_msg = f"由管理员{admin_user.username}强制停止"

    await db.commit()

    logger.warning(f"管理员{admin_user.username}强制停止任务{task_id}")

    return {"message": "任务已强制停止"}


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
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

    # 今日统计
    from datetime import datetime, timedelta, timezone

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    today_completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.status == "completed", Task.end_time >= today_start
        )
    )
    today_completed = today_completed_result.scalar()

    today_failed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.status == "failed", Task.end_time >= today_start
        )
    )
    today_failed = today_failed_result.scalar()

    # 计算成功率
    if total_tasks > 0:
        success_rate = round((completed_tasks / total_tasks) * 100, 1)
    else:
        success_rate = 0

    # 返回驼峰命名的字段名（与前端一致）
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalTasks": total_tasks,
        "runningTasks": running_tasks,
        "completedTasks": completed_tasks,
        "failedTasks": failed_tasks,
        "todayCompleted": today_completed,
        "todayFailed": today_failed,
        "successRate": success_rate,
        "warnings": 0,  # 可以根据实际需求实现
    }


@router.get("/logs")
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    获取系统日志

    管理员专用
    """
    query = select(SystemLog)

    if level:
        query = query.where(SystemLog.level == level)

    query = query.order_by(desc(SystemLog.created_at))

    # 优化：使用count()查询总数
    count_query = select(func.count()).select_from(SystemLog)
    if level:
        count_query = count_query.where(SystemLog.level == level)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # 分页查询数据
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    logs = result.scalars().all()

    return {
        "items": [log.to_dict() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/recover-tasks", response_model=MessageResponse)
async def recover_interrupted_tasks_manually(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    手动恢复被中断的任务

    管理员专用 - 重新提交所有running或pending状态的任务
    """
    from datetime import datetime

    try:
        # 查找所有 running 或 pending 状态的任务
        result = await db.execute(
            select(Task).where(Task.status.in_(["running", "pending"]))
        )
        interrupted_tasks = result.scalars().all()

        if not interrupted_tasks:
            return {"message": "没有发现需要恢复的任务"}

        recovered_count = 0
        failed_count = 0

        for task in interrupted_tasks:
            try:
                # 获取用户信息
                user_result = await db.execute(
                    select(User).where(User.id == task.user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user or not user.is_active:
                    # 用户不存在或已禁用，标记任务为失败
                    task.status = "failed"
                    task.error_msg = "任务恢复失败：用户不存在或已被禁用"
                    task.end_time = datetime.now(timezone.utc)
                    failed_count += 1
                    logger.warning(f"任务 {task.id}: 用户不可用，标记为失败")
                    continue

                # 重置任务状态
                task.status = "pending"
                task.progress = 0
                task.celery_task_id = None
                task.error_msg = f"由管理员 {admin_user.username} 手动恢复"
                task.start_time = None

                await db.commit()

                # 重新提交任务到Celery（需要传递task_id和user_id）
                from tasks.study_tasks import start_study_task

                celery_task = start_study_task.delay(task.id, task.user_id)

                # 更新Celery任务ID
                task.celery_task_id = celery_task.id
                task.status = "running"
                task.start_time = datetime.now(timezone.utc)
                await db.commit()

                recovered_count += 1
                logger.info(f"任务 {task.id} 已由管理员 {admin_user.username} 手动恢复")

            except Exception as task_error:
                task.status = "failed"
                task.error_msg = f"任务恢复失败: {str(task_error)}"
                task.end_time = datetime.now(timezone.utc)
                await db.commit()
                failed_count += 1
                logger.error(f"任务 {task.id} 恢复失败: {task_error}")

        message = f"任务恢复完成：成功恢复 {recovered_count} 个任务"
        if failed_count > 0:
            message += f"，{failed_count} 个任务恢复失败"

        logger.info(f"管理员 {admin_user.username} 手动恢复任务: {message}")

        return {"message": message}

    except Exception as e:
        logger.error(f"手动恢复任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复任务失败: {str(e)}",
        )
