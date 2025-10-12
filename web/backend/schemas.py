# -*- coding: utf-8 -*-
"""
Pydantic数据验证模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


# ============= 用户相关 =============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=80, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= 配置相关 =============

class TikuConfig(BaseModel):
    """题库配置"""
    provider: Optional[str] = Field(None, description="题库提供商")
    tokens: Optional[str] = Field(None, description="题库Token")
    submit: bool = Field(False, description="是否提交")
    cover_rate: float = Field(0.9, description="覆盖率")
    delay: float = Field(1.0, description="查询延迟")


class NotificationConfig(BaseModel):
    """通知配置"""
    provider: Optional[str] = Field(None, description="通知提供商")
    url: Optional[str] = Field(None, description="通知URL")


class UserConfigBase(BaseModel):
    """用户配置基础模型"""
    cx_username: Optional[str] = Field(None, max_length=11, description="超星手机号")
    cx_password: Optional[str] = Field(None, description="超星密码")
    use_cookies: bool = Field(False, description="使用Cookies登录")
    speed: float = Field(1.0, ge=1.0, le=2.0, description="播放倍速")
    notopen_action: str = Field("retry", description="未开放章节处理方式")


class UserConfigUpdate(UserConfigBase):
    """用户配置更新模型"""
    tiku_config: Optional[TikuConfig] = None
    notification_config: Optional[NotificationConfig] = None


class UserConfigResponse(UserConfigBase):
    """用户配置响应模型"""
    id: int
    user_id: int
    tiku_config: dict = {}
    notification_config: dict = {}
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= 任务相关 =============

class TaskCreate(BaseModel):
    """任务创建模型"""
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    course_ids: Optional[List[str]] = Field(None, description="课程ID列表")


class TaskUpdate(BaseModel):
    """任务更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, description="任务状态")


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    user_id: int
    name: str
    course_ids: List[str] = []
    status: str
    progress: int
    celery_task_id: Optional[str] = None
    created_at: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_msg: Optional[str] = None
    completed_courses: int = 0
    total_courses: int = 0
    
    class Config:
        from_attributes = True


class TaskLogResponse(BaseModel):
    """任务日志响应模型"""
    id: int
    task_id: int
    level: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 通用响应 =============

class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[dict] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_users: int = 0
    active_users: int = 0
    total_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0


# ============= WebSocket消息 =============

class WSMessage(BaseModel):
    """WebSocket消息"""
    type: str = Field(..., description="消息类型")
    data: dict = Field(default_factory=dict, description="消息数据")


class TaskProgressMessage(BaseModel):
    """任务进度消息"""
    task_id: int
    progress: int
    status: str
    message: Optional[str] = None

