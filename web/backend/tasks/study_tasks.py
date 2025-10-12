# -*- coding: utf-8 -*-
"""
学习任务 - 集成超星刷课逻辑
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from celery_app import app
from database import AsyncSessionLocal
from models import Task, User, UserConfig, TaskLog
from sqlalchemy import select
import asyncio

# 导入刷课核心逻辑
from api.base import Chaoxing, Account
from api.answer import Tiku
from api.notification import Notification
from api.logger import logger
from api.secure_config import SecureConfig
from api.course_processor import CourseProcessor


async def log_task_message(task_id: int, level: str, message: str):
    """记录任务日志到数据库"""
    async with AsyncSessionLocal() as db:
        log = TaskLog(
            task_id=task_id,
            level=level,
            message=message
        )
        db.add(log)
        await db.commit()


async def update_task_progress(task_id: int, progress: int, status: str = None, error_msg: str = None):
    """更新任务进度"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if task:
            task.progress = progress
            if status:
                task.status = status
            if error_msg:
                task.error_msg = error_msg
            if status == "completed":
                task.end_time = datetime.utcnow()
            await db.commit()
            
            # TODO: 通过WebSocket推送进度
            # from routes.websocket import push_task_progress
            # await push_task_progress(task_id, progress, status or task.status)


async def execute_study_task(task_id: int, user_id: int):
    """
    执行学习任务的核心逻辑
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
    """
    try:
        # 获取任务和用户信息
        async with AsyncSessionLocal() as db:
            # 获取任务
            task_result = await db.execute(select(Task).where(Task.id == task_id))
            task = task_result.scalar_one_or_none()
            
            if not task:
                logger.error(f"任务{task_id}不存在")
                return
            
            # 获取用户配置
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user or not user.config:
                await update_task_progress(task_id, 0, "failed", "用户配置不存在")
                return
            
            config = user.config
            
            # 解密密码
            secure_config = SecureConfig()
            cx_password = None
            if config.cx_password_encrypted:
                cx_password = secure_config.decrypt_password(config.cx_password_encrypted)
            
            if not cx_password:
                await update_task_progress(task_id, 0, "failed", "无法解密超星密码")
                return
        
        # 记录开始
        await log_task_message(task_id, "INFO", "任务开始执行")
        await update_task_progress(task_id, 5, "running")
        
        # 初始化超星API
        account = Account(config.cx_username, cx_password)
        
        # 初始化题库
        tiku = Tiku()
        tiku_config = config.get_tiku_config()
        tiku.config_set(tiku_config)
        tiku = tiku.get_tiku_from_config()
        tiku.init_tiku()
        
        # 获取查询延迟
        query_delay = tiku_config.get("delay", 0)
        
        # 实例化超星API
        chaoxing = Chaoxing(account=account, tiku=tiku, query_delay=query_delay)
        
        await log_task_message(task_id, "INFO", "正在登录超星...")
        await update_task_progress(task_id, 10)
        
        # 登录
        login_result = chaoxing.login(login_with_cookies=config.use_cookies)
        if not login_result["status"]:
            await update_task_progress(task_id, 10, "failed", f"登录失败: {login_result['msg']}")
            await log_task_message(task_id, "ERROR", f"登录失败: {login_result['msg']}")
            return
        
        await log_task_message(task_id, "INFO", "登录成功")
        await update_task_progress(task_id, 20)
        
        # 获取课程列表
        await log_task_message(task_id, "INFO", "获取课程列表...")
        all_courses = chaoxing.get_course_list()
        
        # 过滤课程
        course_ids = task.get_course_ids()
        if course_ids:
            course_task = [c for c in all_courses if c['courseId'] in course_ids]
        else:
            course_task = all_courses
        
        if not course_task:
            await update_task_progress(task_id, 20, "failed", "没有找到要学习的课程")
            return
        
        # 更新总课程数
        async with AsyncSessionLocal() as db:
            task_result = await db.execute(select(Task).where(Task.id == task_id))
            task = task_result.scalar_one_or_none()
            if task:
                task.total_courses = len(course_task)
                await db.commit()
        
        await log_task_message(task_id, "INFO", f"找到{len(course_task)}门课程")
        await update_task_progress(task_id, 30)
        
        # 获取配置参数
        speed = config.video_speed if hasattr(config, 'video_speed') else 1.0
        notopen_action = config.notopen_action if hasattr(config, 'notopen_action') else "continue"
        
        # 定义进度回调函数
        def progress_callback(message: str, progress: int):
            """进度回调（同步函数转异步）"""
            # 这里使用一个包装函数来处理异步调用
            pass  # 进度更新由主逻辑处理
        
        # 定义日志回调函数
        def log_callback(level: str, message: str):
            """日志回调（同步函数转异步）"""
            # 使用asyncio创建任务
            asyncio.create_task(log_task_message(task_id, level, message))
        
        # 创建课程处理器
        processor = CourseProcessor(
            chaoxing=chaoxing,
            speed=speed,
            notopen_action=notopen_action,
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        
        # 开始学习（使用CourseProcessor）
        completed = 0
        base_progress = 30
        progress_per_course = 65 / len(course_task)  # 30-95%用于课程学习
        
        for idx, course in enumerate(course_task):
            await log_task_message(task_id, "INFO", f"开始学习课程: {course['title']}")
            
            try:
                # ✅ 使用CourseProcessor处理课程（完整逻辑）
                success = processor.process_course(course)
                
                if success:
                    completed += 1
                    await log_task_message(task_id, "INFO", f"完成课程: {course['title']}")
                else:
                    await log_task_message(task_id, "WARNING", f"课程 {course['title']} 学习未完全成功")
                
                # 更新进度
                current_progress = int(base_progress + (idx + 1) * progress_per_course)
                await update_task_progress(task_id, current_progress)
                
                # 更新已完成课程数
                async with AsyncSessionLocal() as db:
                    task_result = await db.execute(select(Task).where(Task.id == task_id))
                    task = task_result.scalar_one_or_none()
                    if task:
                        task.completed_courses = completed
                        await db.commit()
            
            except Exception as e:
                await log_task_message(task_id, "ERROR", f"课程学习出错: {str(e)}")
                logger.error(f"课程{course['title']}学习出错: {e}", exc_info=True)
        
        # 完成
        await log_task_message(task_id, "INFO", "所有课程学习完成!")
        await update_task_progress(task_id, 100, "completed")
        
        # 发送通知
        try:
            notification = Notification()
            notification_config = config.get_notification_config()
            notification.config_set(notification_config)
            notification = notification.get_notification_from_config()
            notification.init_notification()
            notification.send(f"超星学习任务完成！完成{completed}/{len(course_task)}门课程")
        except Exception as e:
            logger.warning(f"发送通知失败: {e}")
    
    except Exception as e:
        logger.error(f"任务{task_id}执行失败: {e}", exc_info=True)
        await log_task_message(task_id, "ERROR", f"任务执行失败: {str(e)}")
        await update_task_progress(task_id, 0, "failed", str(e))


@app.task(bind=True, name='tasks.start_study_task')
def start_study_task(self, task_id: int, user_id: int):
    """
    启动学习任务（Celery任务）
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
    """
    logger.info(f"Celery任务启动: task_id={task_id}, user_id={user_id}")
    
    # 运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(execute_study_task(task_id, user_id))
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        logger.error(f"Celery任务失败: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}
    finally:
        loop.close()

