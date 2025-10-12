# -*- coding: utf-8 -*-
"""
API路由模块
"""
from .auth import router as auth_router
from .user import router as user_router
from .task import router as task_router
from .admin import router as admin_router
from .websocket import router as websocket_router
from .system_config import router as system_config_router
from .course import router as course_router

__all__ = [
    "auth_router",
    "user_router",
    "task_router",
    "admin_router",
    "websocket_router",
    "system_config_router",
    "course_router"
]

