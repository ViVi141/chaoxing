# -*- coding: utf-8 -*-
"""
课程处理器 - 可复用的核心学习逻辑
用于命令行版本和Web版本的共享逻辑
"""
import random
import time
from typing import Dict, Any, List, Tuple, Optional, Callable
from api.logger import logger
from api.exceptions import MaxRollBackExceeded


class RollBackManager:
    """课程回滚管理器，避免无限回滚"""
    def __init__(self):
        self.rollback_times = 0
        self.rollback_id = ""

    def add_times(self, id: str):
        """增加回滚次数"""
        if id == self.rollback_id and self.rollback_times == 3:
            raise MaxRollBackExceeded("回滚次数已达3次, 请手动检查学习通任务点完成情况")
        else:
            self.rollback_times += 1

    def new_job(self, id: str):
        """设置新任务，重置回滚次数"""
        if id != self.rollback_id:
            self.rollback_id = id
            self.rollback_times = 0


class CourseProcessor:
    """课程处理器 - 封装核心学习逻辑"""
    
    def __init__(
        self,
        chaoxing,
        speed: float = 1.0,
        notopen_action: str = "retry",
        progress_callback: Optional[Callable[[str, int], None]] = None,
        log_callback: Optional[Callable[[str, str], None]] = None
    ):
        """
        初始化课程处理器
        
        Args:
            chaoxing: Chaoxing API实例
            speed: 视频播放速度
            notopen_action: 未开放章节处理策略 (retry/ask/continue)
            progress_callback: 进度回调函数(message, progress)
            log_callback: 日志回调函数(level, message)
        """
        self.chaoxing = chaoxing
        self.speed = min(2.0, max(1.0, speed))
        self.notopen_action = notopen_action
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.auto_skip_notopen = False
        
        # 将 log_callback 设置到 chaoxing 实例，以便 show_progress 可以使用
        if self.chaoxing and self.log_callback:
            self.chaoxing.log_callback = self.log_callback
        
    def _log(self, level: str, message: str):
        """记录日志"""
        # 调用日志回调
        if self.log_callback:
            self.log_callback(level, message)
        # 同时记录到logger
        getattr(logger, level.lower(), logger.info)(message)
    
    def _update_progress(self, message: str, progress: int = None):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    def handle_not_open_chapter(
        self,
        point: Dict[str, Any],
        RB: RollBackManager,
        auto_skip_notopen: bool = False
    ) -> Tuple[int, bool]:
        """
        处理未开放章节
        
        Returns:
            (action, auto_skip_notopen)
            action: -1退出, 0重试上一章, 1继续下一章
        """
        if self.notopen_action == "retry":
            # 默认处理方式：重试
            if not self.chaoxing.tiku or self.chaoxing.tiku.DISABLE or not self.chaoxing.tiku.SUBMIT:
                self._log("ERROR", 
                    "章节未开启, 可能由于上一章节的章节检测未完成, 也可能由于该章节因为时效已关闭，"
                    "请手动检查完成并提交再重试。或者在配置中配置(自动跳过关闭章节/开启题库并启用提交)"
                )
                return -1, auto_skip_notopen  # 退出标记
            RB.add_times(point["id"])
            return 0, auto_skip_notopen  # 重试上一章节
            
        elif self.notopen_action == "ask":
            # 询问模式
            if not auto_skip_notopen:
                self._log("WARNING", f"章节 {point['title']} 未开放")
                # Web版本无法询问用户，默认跳过
                self._log("INFO", "Web版本自动跳过未开放章节")
                auto_skip_notopen = True
            else:
                self._log("INFO", f"章节 {point['title']} 未开放，自动跳过")
            return 1, auto_skip_notopen  # 继续下一章节
            
        else:  # notopen_action == "continue"
            # 继续模式，直接跳过当前章节
            self._log("INFO", f"章节 {point['title']} 未开放，根据配置跳过此章节")
            return 1, auto_skip_notopen  # 继续下一章节
    
    def process_job(
        self,
        course: Dict[str, Any],
        job: Dict[str, Any],
        job_info: Dict[str, Any]
    ) -> bool:
        """
        处理单个任务点
        
        Returns:
            是否成功
        """
        try:
            # 视频任务
            if job["type"] == "video":
                self._log("INFO", f"识别到视频任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                # 超星的接口没有返回当前任务是否为Audio音频任务
                video_result = self.chaoxing.study_video(
                    course, job, job_info, _speed=self.speed, _type="Video"
                )
                if self.chaoxing.StudyResult.is_failure(video_result):
                    self._log("WARNING", "当前任务非视频任务, 正在尝试音频任务解码")
                    video_result = self.chaoxing.study_video(
                        course, job, job_info, _speed=self.speed, _type="Audio"
                    )
                if self.chaoxing.StudyResult.is_failure(video_result):
                    self._log("WARNING",
                        f"出现异常任务 -> 任务章节: {course['title']} 任务ID: {job['jobid']}, 已跳过"
                    )
                    return False
                return True
                
            # 文档任务
            elif job["type"] == "document":
                self._log("INFO", f"识别到文档任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                self.chaoxing.study_document(course, job)
                return True
                
            # 测验任务
            elif job["type"] == "workid":
                self._log("INFO", f"识别到章节检测任务, 任务章节: {course['title']}")
                self.chaoxing.study_work(course, job, job_info)
                return True
                
            # 阅读任务
            elif job["type"] == "read":
                self._log("INFO", f"识别到阅读任务, 任务章节: {course['title']}")
                self.chaoxing.strdy_read(course, job, job_info)
                return True
            
            else:
                self._log("WARNING", f"未知任务类型: {job['type']}")
                return False
                
        except Exception as e:
            self._log("ERROR", f"处理任务点失败: {str(e)}")
            logger.error(f"任务点处理异常", exc_info=True)
            return False
    
    def process_chapter(
        self,
        course: Dict[str, Any],
        point: Dict[str, Any],
        RB: RollBackManager,
        auto_skip_notopen: bool = False
    ) -> Tuple[int, bool]:
        """
        处理单个章节
        
        Returns:
            (action, auto_skip_notopen)
            action: -1退出, 0重试上一章, 1继续下一章
        """
        self._log("INFO", f'当前章节: {point["title"]}')
        self._update_progress(f'当前章节: {point["title"]}', None)
        
        if point["has_finished"]:
            self._log("INFO", f'章节：{point["title"]} 已完成所有任务点')
            return 1, auto_skip_notopen  # 继续下一章节
        
        # 随机等待，避免请求过快
        sleep_duration = random.uniform(1, 3)
        logger.debug(f"本次随机等待时间: {sleep_duration:.3f}s")
        time.sleep(sleep_duration)
        
        # 获取当前章节的所有任务点
        try:
            jobs, job_info = self.chaoxing.get_job_list(
                course["clazzId"], course["courseId"], course["cpi"], point["id"]
            )
        except Exception as e:
            self._log("ERROR", f"获取章节任务点失败: {str(e)}")
            return 1, auto_skip_notopen  # 跳过该章节
        
        # 发现未开放章节, 根据配置处理
        try:
            if job_info.get("notOpen", False):
                result, auto_skip_notopen = self.handle_not_open_chapter(
                    point, RB, auto_skip_notopen
                )
                return result, auto_skip_notopen
            
            # 遇到开放的章节，重置自动跳过状态
            auto_skip_notopen = False
            RB.new_job(point["id"])
            
        except MaxRollBackExceeded as e:
            self._log("ERROR", "回滚次数已达3次, 请手动检查学习通任务点完成情况")
            return -1, auto_skip_notopen  # 退出标记
        
        self.chaoxing.rollback_times = RB.rollback_times
        
        # 可能存在章节无任何内容的情况
        if not jobs:
            if RB.rollback_times > 0:
                logger.trace(f"回滚中 尝试空页面任务, 任务章节: {course['title']}")
                self.chaoxing.study_emptypage(course, point)
            return 1, auto_skip_notopen  # 继续下一章节
        
        # 遍历所有任务点
        for job in jobs:
            self.process_job(course, job, job_info)
        
        return 1, auto_skip_notopen  # 继续下一章节
    
    def process_course(self, course: Dict[str, Any]) -> bool:
        """
        处理单个课程
        
        Returns:
            是否成功完成
        """
        try:
            self._log("INFO", f"开始学习课程: {course['title']}")
            self._update_progress(f"开始学习课程: {course['title']}", None)
            
            # 获取当前课程的所有章节
            point_list = self.chaoxing.get_course_point(
                course["courseId"], course["clazzId"], course["cpi"]
            )
            
            if not point_list or "points" not in point_list:
                self._log("WARNING", f"课程 {course['title']} 没有章节")
                return True
            
            points = point_list["points"]
            total_points = len(points)
            self._log("INFO", f"课程共有 {total_points} 个章节")
            
            # 为了支持课程任务回滚, 采用下标方式遍历任务点
            __point_index = 0
            auto_skip_notopen = False
            RB = RollBackManager()
            
            while __point_index < total_points:
                point = points[__point_index]
                logger.debug(f"当前章节 __point_index: {__point_index}")
                
                # 计算进度百分比
                progress = int((__point_index / total_points) * 100)
                self._update_progress(
                    f"处理章节 {__point_index + 1}/{total_points}", 
                    progress
                )
                
                result, auto_skip_notopen = self.process_chapter(
                    course, point, RB, auto_skip_notopen
                )
                
                if result == -1:  # 退出当前课程
                    self._log("WARNING", f"课程 {course['title']} 学习中断")
                    return False
                elif result == 0:  # 重试前一章节
                    __point_index = max(0, __point_index - 1)
                else:  # 继续下一章节
                    __point_index += 1
            
            self._log("INFO", f"课程 {course['title']} 学习完成")
            self._update_progress(f"课程 {course['title']} 学习完成", 100)
            return True
            
        except Exception as e:
            self._log("ERROR", f"课程 {course['title']} 处理失败: {str(e)}")
            logger.error(f"课程处理异常", exc_info=True)
            return False
    
    def process_courses(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量处理课程
        
        Returns:
            处理结果统计
        """
        total = len(courses)
        completed = 0
        failed = 0
        
        self._log("INFO", f"开始处理 {total} 门课程")
        
        for idx, course in enumerate(courses):
            self._update_progress(
                f"处理课程 {idx + 1}/{total}: {course['title']}", 
                int((idx / total) * 100)
            )
            
            if self.process_course(course):
                completed += 1
            else:
                failed += 1
        
        result = {
            "total": total,
            "completed": completed,
            "failed": failed
        }
        
        self._log("INFO", f"课程处理完成: 总计{total}门, 成功{completed}门, 失败{failed}门")
        self._update_progress("所有课程处理完成", 100)
        
        return result

