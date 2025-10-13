# -*- coding: utf-8 -*-
"""
安全工具模块 - 额外的安全检查和辅助函数
"""
from typing import Optional
from fastapi import HTTPException, status
from models import User, Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from api.logger import logger


async def verify_task_ownership(
    task_id: int, user: User, db: AsyncSession, allow_admin: bool = False
) -> Task:
    """
    验证任务所有权

    Args:
        task_id: 任务ID
        user: 当前用户
        db: 数据库会话
        allow_admin: 是否允许管理员访问所有任务

    Returns:
        Task: 任务对象

    Raises:
        HTTPException: 任务不存在或无权访问
    """
    # 构建查询
    query = select(Task).where(Task.id == task_id)

    # 如果不是管理员或不允许管理员特权，则必须是任务所有者
    if not (allow_admin and user.role == "admin"):
        query = query.where(Task.user_id == user.id)

    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        # ✅ 不泄露任务是否存在
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    # 记录访问日志（可选）
    logger.debug(f"用户{user.id}访问任务{task_id}")

    return task


async def verify_user_ownership(
    target_user_id: int, current_user: User, db: AsyncSession
) -> User:
    """
    验证用户身份（确保只能操作自己，除非是管理员）

    Args:
        target_user_id: 目标用户ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        User: 目标用户对象

    Raises:
        HTTPException: 权限不足
    """
    # 如果是管理员，可以操作任何用户
    if current_user.role == "admin":
        result = await db.execute(select(User).where(User.id == target_user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "用户不存在")
        return user

    # 如果不是管理员，只能操作自己
    if target_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    return current_user


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    清理用户输入，防止XSS和注入

    Args:
        text: 输入文本
        max_length: 最大长度

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 限制长度
    text = text[:max_length]

    # 移除潜在危险字符
    dangerous_chars = ["<", ">", '"', "'", "&", "\x00"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    return text.strip()


def validate_course_ids(course_ids: list) -> bool:
    """
    验证课程ID格式

    Args:
        course_ids: 课程ID列表

    Returns:
        bool: 是否有效
    """
    if not isinstance(course_ids, list):
        return False

    for course_id in course_ids:
        # 课程ID应该是字符串或数字
        if not isinstance(course_id, (str, int)):
            return False

        # 转为字符串检查
        course_id_str = str(course_id)

        # 课程ID不应包含特殊字符
        if not course_id_str.replace("_", "").replace("-", "").isalnum():
            return False

    return True


class SecurityLog:
    """安全日志记录器"""

    @staticmethod
    def log_suspicious_activity(user_id: int, activity: str, details: str = ""):
        """
        记录可疑活动

        Args:
            user_id: 用户ID
            activity: 活动类型
            details: 详细信息
        """
        logger.warning(
            f"🚨 可疑活动 - 用户{user_id}: {activity}", extra={"details": details}
        )

    @staticmethod
    def log_access_denied(user_id: int, resource: str, reason: str = ""):
        """
        记录访问拒绝

        Args:
            user_id: 用户ID
            resource: 资源类型
            reason: 拒绝原因
        """
        logger.info(
            f"🚫 访问拒绝 - 用户{user_id}尝试访问{resource}", extra={"reason": reason}
        )

    @staticmethod
    def log_privileged_operation(user_id: int, operation: str):
        """
        记录特权操作（管理员操作）

        Args:
            user_id: 用户ID
            operation: 操作描述
        """
        logger.info(f"👑 管理员操作 - 用户{user_id}: {operation}")


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    检查密码强度

    Args:
        password: 密码

    Returns:
        (是否有效, 错误信息)
    """
    if len(password) < 6:
        return False, "密码长度至少6个字符"

    if len(password) > 128:
        return False, "密码长度不能超过128个字符"

    # 可选：添加更强的密码策略
    # has_digit = any(c.isdigit() for c in password)
    # has_letter = any(c.isalpha() for c in password)
    # if not (has_digit and has_letter):
    #     return False, "密码必须包含字母和数字"

    return True, ""


def is_valid_email_domain(email: str, allowed_domains: Optional[list] = None) -> bool:
    """
    验证邮箱域名（可选功能）

    Args:
        email: 邮箱地址
        allowed_domains: 允许的域名列表（None表示允许所有）

    Returns:
        bool: 是否有效
    """
    if allowed_domains is None:
        return True

    if "@" not in email:
        return False

    domain = email.split("@")[1].lower()
    return domain in allowed_domains


class RateLimiter:
    """简单的内存速率限制器（生产环境建议使用Redis）"""

    def __init__(self):
        self._records = {}  # {key: [(timestamp, count), ...]}

    def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> bool:
        """
        检查是否超过速率限制

        Args:
            key: 限制键（如用户ID或IP）
            max_requests: 最大请求数
            window_seconds: 时间窗口（秒）

        Returns:
            bool: 是否允许（True=允许，False=超限）
        """
        import time

        now = time.time()

        # 清理过期记录
        if key in self._records:
            self._records[key] = [
                (ts, count)
                for ts, count in self._records[key]
                if now - ts < window_seconds
            ]
        else:
            self._records[key] = []

        # 计算当前窗口内的请求数
        total = sum(count for ts, count in self._records[key])

        if total >= max_requests:
            return False

        # 记录本次请求
        self._records[key].append((now, 1))
        return True


# 全局速率限制器实例（可选使用）
rate_limiter = RateLimiter()
