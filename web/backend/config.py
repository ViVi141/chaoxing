# -*- coding: utf-8 -*-
"""
简化的配置管理 - 只从 .env 读取，不再支持动态修改
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置 - 从 .env 文件读取"""
    
    # 密钥配置（固定，不再变更）
    SECRET_KEY: str = Field(..., description="应用密钥")
    JWT_SECRET_KEY: str = Field(..., description="JWT密钥")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="JWT过期时间（分钟）")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///data/chaoxing.db", description="数据库URL")
    
    # 部署模式
    DEPLOY_MODE: str = Field(default="simple", description="部署模式")
    
    # Celery配置
    CELERY_BROKER_URL: str = Field(default="filesystem://localhost/", description="Celery Broker")
    CELERY_RESULT_BACKEND: str = Field(default="file://data/celery_results", description="Celery结果后端")
    CELERY_BROKER_TRANSPORT_OPTIONS: dict = Field(
        default_factory=lambda: {
            'data_folder_in': 'data/celery_broker/out',
            'data_folder_out': 'data/celery_broker/out',
            'data_folder_processed': 'data/celery_broker/processed'
        }
    )
    
    # 应用配置
    APP_NAME: str = Field(default="超星学习通多用户管理平台", description="应用名称")
    VERSION: str = Field(default="2.2.3", description="版本号")
    DEBUG: bool = Field(default=False, description="调试模式")
    HOST: str = Field(default="0.0.0.0", description="监听地址")
    PORT: int = Field(default=8000, description="监听端口")
    
    # CORS配置（注意：从.env读取时会自动处理逗号分隔的字符串）
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175",
        description="允许的CORS源（逗号分隔）"
    )
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS源列表"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS
    
    # 默认管理员
    DEFAULT_ADMIN_USERNAME: str = Field(default="admin", description="默认管理员用户名")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="Admin@123", description="默认管理员密码")
    DEFAULT_ADMIN_EMAIL: str = Field(default="admin@example.com", description="默认管理员邮箱")
    
    # SMTP邮件配置
    SMTP_ENABLED: bool = Field(default=False, description="是否启用SMTP")
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP服务器地址")
    SMTP_PORT: int = Field(default=587, description="SMTP端口")
    SMTP_USERNAME: str = Field(default="", description="SMTP用户名")
    SMTP_PASSWORD: str = Field(default="", description="SMTP密码")
    SMTP_FROM_EMAIL: str = Field(default="", description="发件人邮箱")
    SMTP_FROM_NAME: str = Field(default="超星学习通", description="发件人名称")
    SMTP_USE_TLS: bool = Field(default=True, description="是否使用TLS")
    
    # 邮箱验证配置
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = Field(default=30, description="邮箱验证令牌过期时间（分钟）")
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(default=30, description="密码重置令牌过期时间（分钟）")
    
    # 任务配置
    MAX_CONCURRENT_TASKS_PER_USER: int = Field(default=3, description="每用户最大并发任务数")
    TASK_TIMEOUT: int = Field(default=7200, description="任务超时时间（秒）")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="logs/app.log", description="日志文件")
    
    # 分页配置
    PAGE_SIZE: int = Field(default=20, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")
    
    class Config:
        # .env 文件路径（相对于 config.py 所在目录）
        from pathlib import Path
        _backend_dir = Path(__file__).parent
        env_file = str(_backend_dir / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True
        # 允许从环境变量读取
        extra = "allow"


# 创建全局配置实例
settings = Settings()


# 在模块加载时输出配置状态
def get_config_info():
    """获取配置信息用于调试"""
    return {
        "database": settings.DATABASE_URL,
        "deploy_mode": settings.DEPLOY_MODE,
        "admin_username": settings.DEFAULT_ADMIN_USERNAME,
        "jwt_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    }

