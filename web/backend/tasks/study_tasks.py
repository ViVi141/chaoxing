# -*- coding: utf-8 -*-
"""
学习任务 - 集成超星刷课逻辑（同步版本，用于Celery）
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Callable

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from celery_app import app
from database_sync import get_sync_db
from models import Task, User, UserConfig, TaskLog
from sqlalchemy import select

# 导入刷课核心逻辑
from api.base import Chaoxing, Account
from api.answer import Tiku
from api.notification import Notification
from api.logger import logger
from api.secure_config import SecureConfig
from api.course_processor import CourseProcessor


def log_task_message(task_id: int, level: str, message: str):
    """记录任务日志到数据库（同步版本）"""
    db = get_sync_db()
    try:
        log = TaskLog(
            task_id=task_id,
            level=level,
            message=message
        )
        db.add(log)
        db.commit()
        logger.info(f"[Task {task_id}] {level}: {message}")
    except Exception as e:
        logger.error(f"记录日志失败: {e}")
        db.rollback()
    finally:
        db.close()


def update_task_progress(
    task_id: int, 
    progress: int, 
    status: Optional[str] = None, 
    error_msg: Optional[str] = None,
    current_item: Optional[str] = None,
    item_progress: Optional[int] = None,
    item_current_time: Optional[int] = None,  # 当前时间（秒）
    item_total_time: Optional[int] = None,    # 总时长（秒）
    item_detail: Optional[str] = None         # 额外详情
) -> bool:
    """
    更新任务进度（同步版本）
    
    Args:
        task_id: 任务ID
        progress: 总体进度 (0-100)
        status: 任务状态
        error_msg: 错误消息
        current_item: 当前处理的项目（如视频名称）
        item_progress: 当前项目的进度 (0-100)
        item_current_time: 当前时间（秒，用于视频/音频）
        item_total_time: 总时长（秒，用于视频/音频）
        item_detail: 额外详情（如页数等）
    
    Returns:
        bool: 任务是否应该继续执行（False表示任务已被暂停/取消）
    """
    db = get_sync_db()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if task:
            # ✅ 检查任务是否被暂停或取消
            if task.status in ["paused", "cancelled"]:
                logger.info(f"任务{task_id}状态为{task.status}，停止更新进度")
                return False
            
            task.progress = progress
            if status:
                task.status = status
            if error_msg:
                task.error_msg = error_msg
            if status == "completed":
                task.end_time = datetime.now(timezone.utc)
            
            db.commit()
            
            # 构建详细进度信息
            progress_info = {
                "progress": progress,
                "status": status or task.status,
                "error_msg": error_msg,
                "completed_courses": task.completed_courses or 0,
                "total_courses": task.total_courses or 0,
            }
            
            # 添加当前项目详细信息
            if current_item:
                progress_info["current_item"] = current_item
            if item_progress is not None:
                progress_info["item_progress"] = item_progress
            if item_current_time is not None:
                progress_info["item_current_time"] = item_current_time
            if item_total_time is not None:
                progress_info["item_total_time"] = item_total_time
            if item_detail:
                progress_info["item_detail"] = item_detail
            
            # 格式化时间显示
            def format_time(seconds: int) -> str:
                """格式化秒数为 MM:SS"""
                minutes = seconds // 60
                secs = seconds % 60
                return f"{minutes:02d}:{secs:02d}"
            
            # 记录详细日志并显示在前端
            if current_item:
                if item_current_time is not None and item_total_time is not None:
                    # 视频/音频进度 - 显示时间轴
                    time_display = f"{format_time(item_current_time)}/{format_time(item_total_time)}"
                    logger.info(
                        f"[Task {task_id}] {current_item}: {item_progress}% ({time_display}) | 总进度: {progress}%"
                    )
                    # 记录到数据库日志，前端可实时显示
                    log_task_message(
                        task_id, 
                        "INFO", 
                        f"当前任务: {current_item} | {item_progress}%  {time_display}"
                    )
                elif item_detail:
                    # 其他类型进度（如文档页数）
                    logger.info(
                        f"[Task {task_id}] {current_item}: {item_progress}% ({item_detail}) | 总进度: {progress}%"
                    )
                elif item_progress is not None:
                    # 基本进度
                    logger.info(f"[Task {task_id}] {current_item}: {item_progress}% | 总进度: {progress}%")
            
            # ✅ 通过WebSocket实时推送进度更新到前端
            try:
                push_task_update_sync(task_id, progress_info)
            except Exception as e:
                logger.debug(f"WebSocket推送失败（非致命错误）: {e}")
            
            return True  # 任务可以继续
            
    except Exception as e:
        logger.error(f"更新任务进度失败: {e}")
        db.rollback()
        return True  # 即使出错也允许继续（防止意外中断）
    finally:
        db.close()


def push_task_update_sync(task_id: int, data: dict):
    """
    同步方式推送WebSocket更新（在Celery worker中调用）
    
    由于Celery worker运行在同步环境中，我们需要创建新的事件循环来推送异步消息
    """
    import asyncio
    from routes.websocket import manager
    
    try:
        # 尝试获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建任务
                asyncio.create_task(manager.send_task_update(task_id, data))
            else:
                # 如果循环未运行，直接运行
                loop.run_until_complete(manager.send_task_update(task_id, data))
        except RuntimeError:
            # 如果没有事件循环，创建新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(manager.send_task_update(task_id, data))
            loop.close()
    except Exception as e:
        # WebSocket推送失败不应影响主任务
        logger.debug(f"WebSocket推送异常: {e}")


class DetailedProgressCallback:
    """详细进度回调类"""
    
    def __init__(self, task_id: int, course_idx: int, total_courses: int):
        self.task_id = task_id
        self.course_idx = course_idx
        self.total_courses = total_courses
        self.base_progress = 30 + (course_idx * 65 // total_courses)
        self.course_progress_range = 65 // total_courses
        
    def on_chapter_start(self, chapter_name: str):
        """章节开始"""
        log_task_message(self.task_id, "INFO", f"📚 开始学习章节: {chapter_name}")
        
    def on_point_start(self, point_name: str):
        """知识点开始"""
        log_task_message(self.task_id, "INFO", f"📖 学习知识点: {point_name}")
        
    def on_video_start(self, video_name: str, duration: int):
        """视频开始"""
        log_task_message(self.task_id, "INFO", f"🎬 开始观看视频: {video_name} (时长: {duration}秒)")
        
    def on_video_progress(self, video_name: str, current: int, total: int):
        """视频进度更新"""
        video_progress = int((current / total) * 100) if total > 0 else 0
        overall_progress = self.base_progress + int((video_progress / 100) * self.course_progress_range * 0.8)
        
        update_task_progress(
            self.task_id,
            overall_progress,
            "running",
            current_item=f"🎬 {video_name}",
            item_progress=video_progress
        )
        
        # 每25%记录一次日志
        if video_progress % 25 == 0:
            log_task_message(
                self.task_id, 
                "INFO", 
                f"视频观看进度: {video_name} - {video_progress}% ({current}/{total}秒)"
            )
    
    def on_video_complete(self, video_name: str):
        """视频完成"""
        log_task_message(self.task_id, "INFO", f"✅ 视频观看完成: {video_name}")
        
    def on_document_start(self, doc_name: str, pages: int):
        """文档开始"""
        log_task_message(self.task_id, "INFO", f"📄 开始阅读文档: {doc_name} (共{pages}页)")
        
    def on_document_progress(self, doc_name: str, current_page: int, total_pages: int):
        """文档进度"""
        doc_progress = int((current_page / total_pages) * 100) if total_pages > 0 else 0
        
        update_task_progress(
            self.task_id,
            self.base_progress + int((doc_progress / 100) * self.course_progress_range * 0.5),
            "running",
            current_item=f"📄 {doc_name}",
            item_progress=doc_progress
        )
        
        log_task_message(
            self.task_id,
            "INFO",
            f"文档阅读进度: {doc_name} - {current_page}/{total_pages}页"
        )
    
    def on_task_start(self, task_name: str):
        """任务（作业/测验）开始"""
        log_task_message(self.task_id, "INFO", f"📝 开始答题: {task_name}")
        
    def on_question_answer(self, question_idx: int, total_questions: int, question_type: str):
        """答题进度"""
        task_progress = int((question_idx / total_questions) * 100) if total_questions > 0 else 0
        
        update_task_progress(
            self.task_id,
            self.base_progress + int((task_progress / 100) * self.course_progress_range * 0.3),
            "running",
            current_item=f"📝 答题中 ({question_type})",
            item_progress=task_progress
        )
        
        log_task_message(
            self.task_id,
            "INFO",
            f"答题进度: {question_idx}/{total_questions} - {question_type}"
        )
    
    def on_course_progress(self, completed_points: int, total_points: int):
        """课程整体进度"""
        course_progress = int((completed_points / total_points) * 100) if total_points > 0 else 0
        overall_progress = self.base_progress + int((course_progress / 100) * self.course_progress_range)
        
        update_task_progress(
            self.task_id,
            overall_progress,
            "running",
            current_item=f"课程进度",
            item_progress=course_progress
        )
        
        log_task_message(
            self.task_id,
            "INFO",
            f"课程完成度: {completed_points}/{total_points} 个知识点 ({course_progress}%)"
        )


def execute_study_task(task_id: int, user_id: int):
    """
    执行学习任务的核心逻辑（同步版本）
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
    """
    try:
        # 获取任务和用户信息
        db = get_sync_db()
        try:
            # 获取任务
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                logger.error(f"任务{task_id}不存在")
                return
            
            # 获取用户配置
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                update_task_progress(task_id, 0, "failed", "用户不存在")
                return
            
            # 手动加载config关系
            config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            
            if not config:
                update_task_progress(task_id, 0, "failed", "用户配置不存在")
                return
            
            # 解密密码
            secure_config = SecureConfig()
            cx_password = None
            if config.cx_password_encrypted:
                cx_password = secure_config.decrypt_password(config.cx_password_encrypted)
            
            if not cx_password:
                update_task_progress(task_id, 0, "failed", "无法解密超星密码")
                return
        finally:
            db.close()
        
        # 记录开始
        log_task_message(task_id, "INFO", "🚀 任务开始执行")
        if not update_task_progress(task_id, 5, "running"):
            return  # 任务已被暂停/取消
        
        # 初始化超星API
        account = Account(_username=config.cx_username, _password=cx_password)
        
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
        
        log_task_message(task_id, "INFO", "🔐 正在登录超星...")
        if not update_task_progress(task_id, 10):
            return  # 任务已被暂停/取消
        
        # 登录
        login_result = chaoxing.login(login_with_cookies=config.use_cookies)
        if not login_result["status"]:
            update_task_progress(task_id, 10, "failed", f"登录失败: {login_result['msg']}")
            log_task_message(task_id, "ERROR", f"❌ 登录失败: {login_result['msg']}")
            return
        
        log_task_message(task_id, "INFO", "✅ 登录成功")
        if not update_task_progress(task_id, 20):
            return  # 任务已被暂停/取消
        
        # 获取课程列表
        log_task_message(task_id, "INFO", "📚 获取课程列表...")
        all_courses = chaoxing.get_course_list()
        
        # 过滤课程
        course_ids = task.get_course_ids()
        if course_ids:
            course_task = [c for c in all_courses if c['courseId'] in course_ids]
        else:
            course_task = all_courses
        
        if not course_task:
            update_task_progress(task_id, 20, "failed", "没有找到要学习的课程")
            return
        
        # 更新总课程数
        db = get_sync_db()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.total_courses = len(course_task)
                db.commit()
        finally:
            db.close()
        
        log_task_message(task_id, "INFO", f"📖 找到 {len(course_task)} 门课程")
        if not update_task_progress(task_id, 30):
            return  # 任务已被暂停/取消
        
        # 获取配置参数
        speed = config.video_speed if hasattr(config, 'video_speed') else 1.0
        notopen_action = config.notopen_action if hasattr(config, 'notopen_action') else "continue"
        
        # 开始学习
        completed = 0
        failed = 0
        errors = []
        
        for idx, course in enumerate(course_task):
            # ✅ 检查任务状态（是否被暂停或取消）
            db = get_sync_db()
            try:
                current_task = db.query(Task).filter(Task.id == task_id).first()
                if current_task and current_task.status in ["paused", "cancelled"]:
                    log_task_message(task_id, "WARNING", f"⚠️ 任务被{current_task.status}，停止执行")
                    logger.info(f"任务{task_id}检测到状态为{current_task.status}，主动退出")
                    return  # 主动退出任务
            finally:
                db.close()
            
            log_task_message(task_id, "INFO", f"📚 开始学习课程 ({idx+1}/{len(course_task)}): {course['title']}")
            
            # 创建详细进度回调
            progress_callback = DetailedProgressCallback(task_id, idx, len(course_task))
            
            try:
                # 使用真实的CourseProcessor处理课程
                success = process_course_with_detailed_progress(
                    chaoxing, 
                    course, 
                    speed, 
                    notopen_action, 
                    progress_callback
                )
                
                if success:
                    completed += 1
                    log_task_message(task_id, "INFO", f"✅ 完成课程: {course['title']}")
                else:
                    failed += 1
                    log_task_message(task_id, "WARNING", f"⚠️ 课程 {course['title']} 学习未完全成功")
                    errors.append(f"课程 {course['title']} 处理失败")
                
                # 更新已完成课程数
                db = get_sync_db()
                try:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task.completed_courses = completed
                        db.commit()
                finally:
                    db.close()
            
            except Exception as e:
                failed += 1
                error_msg = f"课程 {course['title']} 出错: {str(e)}"
                errors.append(error_msg)
                log_task_message(task_id, "ERROR", f"❌ {error_msg}")
                logger.error(f"课程{course['title']}学习出错: {e}", exc_info=True)
        
        # 判断最终状态
        if completed == 0:
            # 全部失败
            error_detail = "; ".join(errors[:3])  # 只显示前3个错误
            log_task_message(task_id, "ERROR", f"❌ 所有课程学习失败！")
            update_task_progress(task_id, 100, "failed", f"所有课程失败: {error_detail}")
        elif failed > 0:
            # 部分失败
            error_detail = "; ".join(errors[:3])
            log_task_message(task_id, "WARNING", f"⚠️ 课程学习部分完成！成功 {completed}/{len(course_task)} 门课程，失败 {failed} 门")
            update_task_progress(task_id, 100, "completed", f"部分成功 ({completed}/{len(course_task)}): {error_detail}")
        else:
            # 全部成功
            log_task_message(task_id, "INFO", f"🎉 所有课程学习完成！完成 {completed}/{len(course_task)} 门课程")
            update_task_progress(task_id, 100, "completed")
        
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
        log_task_message(task_id, "ERROR", f"❌ 任务执行失败: {str(e)}")
        update_task_progress(task_id, 0, "failed", str(e))


def process_course_with_detailed_progress(
    chaoxing: Chaoxing,
    course: dict,
    speed: float,
    notopen_action: str,
    progress_callback: DetailedProgressCallback
) -> bool:
    """
    处理课程（使用CourseProcessor，真正的课程学习逻辑）
    
    集成了命令行版本的完整CourseProcessor，包括：
    - 正确的章节遍历和回滚管理
    - 视频、文档、测验等各类任务处理
    - 未开放章节的智能处理
    - 详细的进度回调和日志记录
    
    Args:
        chaoxing: Chaoxing API实例
        course: 课程信息
        speed: 视频播放速度
        notopen_action: 未开放章节处理策略
        progress_callback: 详细进度回调
    
    Returns:
        bool: 是否成功完成课程
    """
    try:
        import re
        
        # 创建日志回调 - 捕获并解析CourseProcessor的详细日志
        def log_callback(level: str, message: str):
            # 记录原始日志
            log_task_message(progress_callback.task_id, level, message)
            
            # 解析视频播放进度（命令行格式）
            # 例如: "当前任务: 5.民歌的创作特征（一）-720p.mp4 |...| 0%  00:03/28:28"
            video_progress_match = re.search(
                r'当前任务:\s*(.+?)\s*\|.*?\|\s*(\d+)%\s+(\d+):(\d+)/(\d+):(\d+)',
                message
            )
            if video_progress_match:
                video_name = video_progress_match.group(1).strip()
                progress_percent = int(video_progress_match.group(2))
                current_min = int(video_progress_match.group(3))
                current_sec = int(video_progress_match.group(4))
                total_min = int(video_progress_match.group(5))
                total_sec = int(video_progress_match.group(6))
                
                current_time = current_min * 60 + current_sec
                total_time = total_min * 60 + total_sec
                
                # 更新任务进度，包含时间信息
                update_task_progress(
                    progress_callback.task_id,
                    progress_callback.base_progress + int((progress_percent / 100) * progress_callback.course_progress_range * 0.8),
                    "running",
                    current_item=f"🎬 {video_name}",
                    item_progress=progress_percent,
                    item_current_time=current_time,
                    item_total_time=total_time
                )
                return
            
            # 解析开始任务日志
            # 例如: "开始任务 5.民歌的创作特征（一）-720p.mp4, 总时长 1708秒"
            start_task_match = re.search(
                r'开始任务\s+(.+?),\s*总时长\s+(\d+)秒',
                message
            )
            if start_task_match:
                task_name = start_task_match.group(1).strip()
                total_seconds = int(start_task_match.group(2))
                log_task_message(
                    progress_callback.task_id,
                    "INFO",
                    f"🎬 开始观看视频: {task_name} (时长: {total_seconds//60}分{total_seconds%60}秒)"
                )
                return
            
            # 解析识别到的任务类型
            if "识别到视频任务" in message:
                match = re.search(r'任务章节:\s*(.+?)\s+任务ID', message)
                if match:
                    chapter_name = match.group(1).strip()
                    log_task_message(progress_callback.task_id, "INFO", f"📚 学习章节: {chapter_name}")
            elif "识别到文档任务" in message:
                log_task_message(progress_callback.task_id, "INFO", "📄 识别到文档任务")
            elif "识别到章节检测任务" in message:
                log_task_message(progress_callback.task_id, "INFO", "📝 识别到章节检测任务")
        
        # 创建进度回调 - 将CourseProcessor的进度转发到详细进度回调  
        def simple_progress_callback(message: str, progress: Optional[int]):
            # 解析消息类型并调用相应的回调
            if "当前章节:" in message:
                chapter_name = message.replace("当前章节:", "").strip()
                progress_callback.on_chapter_start(chapter_name)
            elif progress is not None:
                # 更新整体进度
                pass
        
        # 使用CourseProcessor处理课程（真正的实现）
        processor = CourseProcessor(
            chaoxing=chaoxing,
            speed=speed,
            notopen_action=notopen_action,
            progress_callback=simple_progress_callback,
            log_callback=log_callback
        )
        
        # 处理课程并返回结果
        success = processor.process_course(course)
        
        return success
    
    except Exception as e:
        logger.error(f"课程处理出错: {e}", exc_info=True)
        log_task_message(progress_callback.task_id, "ERROR", f"课程处理异常: {str(e)}")
        return False


@app.task(bind=True, name='tasks.start_study_task')
def start_study_task(self, task_id: int, user_id: int):
    """
    启动学习任务（Celery任务）
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
    """
    logger.info(f"🚀 Celery任务启动: task_id={task_id}, user_id={user_id}")
    
    try:
        execute_study_task(task_id, user_id)
        
        # 检查任务最终状态
        db = get_sync_db()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                final_status = task.status
                if final_status == "failed":
                    return {"status": "failed", "task_id": task_id, "error": task.error_msg}
                elif final_status == "completed":
                    return {"status": "success", "task_id": task_id}
                else:
                    return {"status": "unknown", "task_id": task_id, "current_status": final_status}
            else:
                return {"status": "error", "task_id": task_id, "error": "任务不存在"}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Celery任务失败: {e}", exc_info=True)
        # 确保任务状态更新为失败
        try:
            update_task_progress(task_id, 0, "failed", str(e))
        except:
            pass
        return {"status": "failed", "task_id": task_id, "error": str(e)}
