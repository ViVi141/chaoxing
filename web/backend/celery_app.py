# -*- coding: utf-8 -*-
"""
Celery应用配置
支持简单模式（文件系统）和标准模式（Redis）
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
from celery import Celery
from config import settings

# 创建Celery应用
app = Celery(
    "chaoxing_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 基础配置
config_dict = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "Asia/Shanghai",
    "enable_utc": False,
    "task_track_started": True,
    "task_time_limit": settings.TASK_TIMEOUT,
    "task_soft_time_limit": settings.TASK_TIMEOUT - 300,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 1000,
    "result_expires": 3600,
    # Celery 6.0兼容性配置
    "broker_connection_retry_on_startup": True,
}

# 如果使用文件系统broker（简单模式）
if settings.CELERY_BROKER_URL.startswith("filesystem://"):
    # 创建必要的目录
    for folder in settings.CELERY_BROKER_TRANSPORT_OPTIONS.values():
        os.makedirs(folder, exist_ok=True)

    config_dict["broker_transport_options"] = settings.CELERY_BROKER_TRANSPORT_OPTIONS

# 如果使用文件系统结果后端（简单模式）
if settings.CELERY_RESULT_BACKEND.startswith("file://"):
    # 从 file://./celery_results 中提取路径
    result_dir = settings.CELERY_RESULT_BACKEND.replace("file://", "")
    # 处理相对路径
    if result_dir.startswith("./"):
        result_dir = result_dir[2:]
    os.makedirs(result_dir, exist_ok=True)

# 应用配置
app.conf.update(config_dict)

# 自动发现任务
# 注意：由于已经设置了PYTHONPATH，直接使用tasks模块
app.autodiscover_tasks()

# 手动注册任务模块
from tasks import study_tasks

if __name__ == "__main__":
    app.start()
