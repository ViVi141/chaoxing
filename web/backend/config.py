# -*- coding: utf-8 -*-
"""
应用配置（使用Pydantic Settings）
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "超星学习通多用户管理平台"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="调试模式")
    HOST: str = Field(default="0.0.0.0", description="服务器地址")
    PORT: int = Field(default=8000, description="服务器端口")
    
    # 安全配置
    SECRET_KEY: str = Field(
        default="your-secret-key-please-change-in-production",
        description="密钥（生产环境必须修改）"
    )
    JWT_SECRET_KEY: str = Field(default="", description="JWT密钥")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30天
    
    # 部署模式（simple: SQLite+文件队列, standard: PostgreSQL+Redis）
    DEPLOY_MODE: str = Field(
        default="simple",
        description="部署模式：simple(简单模式) 或 standard(标准模式)"
    )
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./chaoxing_web.db",
        description="数据库连接URL"
    )
    # 简单模式: sqlite+aiosqlite:///./chaoxing_web.db
    # 标准模式: postgresql+asyncpg://user:password@localhost/dbname
    
    # Redis配置（仅标准模式需要）
    REDIS_URL: str = Field(
        default="",
        description="Redis连接URL（可选，简单模式不需要）"
    )
    
    # Celery配置
    CELERY_BROKER_URL: str = Field(
        default="filesystem://",
        description="Celery消息代理URL"
    )
    # 简单模式: filesystem:// (使用文件系统)
    # 标准模式: redis://localhost:6379/0
    
    CELERY_RESULT_BACKEND: str = Field(
        default="file://./celery_results",
        description="Celery结果后端URL"
    )
    # 简单模式: file://./celery_results
    # 标准模式: redis://localhost:6379/0
    
    # Celery文件系统broker配置（简单模式）
    CELERY_BROKER_TRANSPORT_OPTIONS: dict = Field(
        default_factory=lambda: {
            'data_folder_in': './celery_broker/out',
            'data_folder_out': './celery_broker/out',
            'data_folder_processed': './celery_broker/processed'
        }
    )
    
    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="允许的CORS源"
    )
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="logs/web_app.log", description="日志文件路径")
    
    # 分页配置
    PAGE_SIZE: int = Field(default=20, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")
    
    # 任务配置
    MAX_CONCURRENT_TASKS_PER_USER: int = Field(
        default=3,
        description="每个用户最大并发任务数"
    )
    TASK_TIMEOUT: int = Field(default=7200, description="任务超时时间（秒）")
    
    # 默认管理员配置
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "Admin@123"  # 生产环境首次登录后立即修改
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小（字节）")
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, description="WebSocket心跳间隔（秒）")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果未单独设置JWT密钥，使用SECRET_KEY
        if not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = self.SECRET_KEY


# 创建全局配置实例
settings = Settings()


# 环境配置
class DevelopmentSettings(Settings):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 生产环境验证
        if self.SECRET_KEY == "your-secret-key-please-change-in-production":
            raise ValueError("⚠️ 生产环境必须修改SECRET_KEY！")
        if self.DEFAULT_ADMIN_PASSWORD == "Admin@123":
            print("⚠️ 警告：使用默认管理员密码，请在首次登录后立即修改！")


class TestingSettings(Settings):
    """测试环境配置"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    LOG_LEVEL: str = "ERROR"


def get_settings(env: str = "development") -> Settings:
    """
    根据环境获取配置
    
    Args:
        env: 环境名称 (development/production/testing)
    
    Returns:
        配置实例
    """
    config_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    config_class = config_map.get(env, DevelopmentSettings)
    return config_class()
