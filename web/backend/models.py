# -*- coding: utf-8 -*-
"""
数据库模型定义（SQLAlchemy 2.0异步版本）
"""
from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import String, Integer, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from database import Base


class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)  # ✅ 改为必填
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # ✅ 新增邮箱验证状态
    role: Mapped[str] = mapped_column(String(20), default='user', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    config: Mapped[Optional["UserConfig"]] = relationship(
        "UserConfig",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == 'admin'

    def to_dict(self, include_config: bool = False) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,  # ✅ 新增
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        if include_config and self.config:
            data['config'] = self.config.to_dict()
        return data


class UserConfig(Base):
    """用户配置模型"""
    __tablename__ = 'user_configs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    # 超星账号配置
    cx_username: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    cx_password_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    use_cookies: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cookies_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 播放配置
    speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    notopen_action: Mapped[str] = mapped_column(String(20), default='retry', nullable=False)

    # JSON配置
    tiku_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notification_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="config")

    def get_tiku_config(self) -> dict:
        """获取题库配置"""
        if self.tiku_config:
            try:
                return json.loads(self.tiku_config)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_tiku_config(self, config: dict) -> None:
        """设置题库配置"""
        self.tiku_config = json.dumps(config, ensure_ascii=False)

    def get_notification_config(self) -> dict:
        """获取通知配置"""
        if self.notification_config:
            try:
                return json.loads(self.notification_config)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_notification_config(self, config: dict) -> None:
        """设置通知配置"""
        self.notification_config = json.dumps(config, ensure_ascii=False)

    def get_cookies(self) -> dict:
        """获取cookies"""
        if self.cookies_data:
            try:
                return json.loads(self.cookies_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_cookies(self, cookies: dict) -> None:
        """设置cookies"""
        self.cookies_data = json.dumps(cookies, ensure_ascii=False)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'cx_username': self.cx_username,
            'use_cookies': self.use_cookies,
            'speed': self.speed,
            'notopen_action': self.notopen_action,
            'tiku_config': self.get_tiku_config(),
            'notification_config': self.get_notification_config(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(Base):
    """任务模型"""
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # 任务信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 状态
    status: Mapped[str] = mapped_column(
        String(20),
        default='pending',
        nullable=False,
        index=True
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Celery任务ID
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 结果
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_courses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_courses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    logs: Mapped[List["TaskLog"]] = relationship(
        "TaskLog",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    def get_course_ids(self) -> List[str]:
        """获取课程ID列表"""
        if self.course_ids:
            try:
                return json.loads(self.course_ids)
            except json.JSONDecodeError:
                return []
        return []

    def set_course_ids(self, course_ids: List[str]) -> None:
        """设置课程ID列表"""
        self.course_ids = json.dumps(course_ids)

    def to_dict(self, include_logs: bool = False) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'course_ids': self.get_course_ids(),
            'status': self.status,
            'progress': self.progress,
            'celery_task_id': self.celery_task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_msg': self.error_msg,
            'completed_courses': self.completed_courses,
            'total_courses': self.total_courses,
        }
        if include_logs:
            # 按创建时间倒序排序，最新的日志在前面
            sorted_logs = sorted(self.logs, key=lambda x: x.created_at, reverse=True)
            data['logs'] = [log.to_dict() for log in sorted_logs[:200]]  # 最多200条
        return data


class TaskLog(Base):
    """任务日志模型"""
    __tablename__ = 'task_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)

    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    task: Mapped["Task"] = relationship("Task", back_populates="logs")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'level': self.level,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SystemLog(Base):
    """系统日志模型"""
    __tablename__ = 'system_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class EmailVerification(Base):
    """邮箱验证令牌模型"""
    __tablename__ = 'email_verifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    token_type: Mapped[str] = mapped_column(String(20), nullable=False)  # verify_email, reset_password
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def is_expired(self) -> bool:
        """是否已过期"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SystemConfig(Base):
    """系统配置模型 - 管理员可在前端修改"""
    __tablename__ = 'system_configs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    config_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_type: Mapped[str] = mapped_column(String(20), nullable=False)  # string, int, bool, float
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 敏感信息（如密码）
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    def get_value(self):
        """获取配置值（自动类型转换）"""
        if self.config_value is None:
            return None
        
        if self.config_type == 'int':
            return int(self.config_value)
        elif self.config_type == 'float':
            return float(self.config_value)
        elif self.config_type == 'bool':
            return self.config_value.lower() in ('true', '1', 'yes', 'on')
        else:
            return self.config_value

    def set_value(self, value):
        """设置配置值（自动转换为字符串）"""
        if value is None:
            self.config_value = None
        else:
            self.config_value = str(value)

    def to_dict(self, hide_sensitive: bool = True) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value if not (hide_sensitive and self.is_sensitive) else '***',
            'config_type': self.config_type,
            'description': self.description,
            'is_sensitive': self.is_sensitive,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }
        return data
