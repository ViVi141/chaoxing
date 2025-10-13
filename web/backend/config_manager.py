# -*- coding: utf-8 -*-
"""
动态配置管理器 - 支持在线修改部分系统参数
优先使用数据库中的配置，如果不存在则使用.env中的默认值
"""
from typing import Optional, Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import SystemConfig
from config import settings
from api.logger import logger


class ConfigManager:
    """配置管理器 - 支持运行时动态配置"""
    
    # 可在线修改的配置项（其他配置仍从.env读取，需要重启才能生效）
    EDITABLE_CONFIGS = {
        'max_concurrent_tasks_per_user': {
            'type': 'int',
            'default': settings.MAX_CONCURRENT_TASKS_PER_USER,
            'description': '每用户最大并发任务数',
            'min': 1,
            'max': 10,
        },
        'task_timeout': {
            'type': 'int',
            'default': settings.TASK_TIMEOUT,
            'description': '任务超时时间（秒）',
            'min': 600,
            'max': 28800,
        },
        'page_size': {
            'type': 'int',
            'default': settings.PAGE_SIZE,
            'description': '默认分页大小',
            'min': 10,
            'max': 100,
        },
        'max_page_size': {
            'type': 'int',
            'default': settings.MAX_PAGE_SIZE,
            'description': '最大分页大小',
            'min': 50,
            'max': 500,
        },
        'jwt_access_token_expire_minutes': {
            'type': 'int',
            'default': settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            'description': 'JWT令牌过期时间（分钟）',
            'min': 60,
            'max': 43200,
        },
        'email_verification_expire_minutes': {
            'type': 'int',
            'default': settings.EMAIL_VERIFICATION_EXPIRE_MINUTES,
            'description': '邮箱验证令牌过期时间（分钟）',
            'min': 10,
            'max': 1440,
        },
        'password_reset_expire_minutes': {
            'type': 'int',
            'default': settings.PASSWORD_RESET_EXPIRE_MINUTES,
            'description': '密码重置令牌过期时间（分钟）',
            'min': 10,
            'max': 1440,
        },
    }
    
    # 只读配置（无法在线修改，需要修改.env并重启）
    READONLY_CONFIGS = {
        'app_name': settings.APP_NAME,
        'version': settings.VERSION,
        'debug': settings.DEBUG,
        'host': settings.HOST,
        'port': settings.PORT,
        'deploy_mode': settings.DEPLOY_MODE,
        'database_url': '***已配置***' if settings.DATABASE_URL else '未配置',
        'default_admin_username': settings.DEFAULT_ADMIN_USERNAME,
    }
    
    @staticmethod
    async def get_config(db: AsyncSession, key: str, default: Any = None) -> Any:
        """
        获取配置值（优先从数据库读取）
        
        Args:
            db: 数据库会话
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            # 先从数据库查询
            result = await db.execute(
                select(SystemConfig).where(SystemConfig.config_key == key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                return config.get_value()
            
            # 如果数据库中没有，返回默认值
            return default
            
        except Exception as e:
            logger.warning(f"获取配置 {key} 失败: {e}")
            return default
    
    @staticmethod
    async def set_config(
        db: AsyncSession,
        key: str,
        value: Any,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> SystemConfig:
        """
        设置配置值
        
        Args:
            db: 数据库会话
            key: 配置键
            value: 配置值
            user_id: 修改者用户ID
            description: 配置描述
            
        Returns:
            SystemConfig对象
        """
        # 检查是否是可编辑配置
        if key not in ConfigManager.EDITABLE_CONFIGS:
            raise ValueError(f"配置项 {key} 不可在线修改")
        
        config_meta = ConfigManager.EDITABLE_CONFIGS[key]
        
        # 类型验证
        config_type = config_meta['type']
        if config_type == 'int':
            value = int(value)
            # 范围验证
            if 'min' in config_meta and value < config_meta['min']:
                raise ValueError(f"{key} 不能小于 {config_meta['min']}")
            if 'max' in config_meta and value > config_meta['max']:
                raise ValueError(f"{key} 不能大于 {config_meta['max']}")
        elif config_type == 'float':
            value = float(value)
        elif config_type == 'bool':
            value = bool(value)
        
        # 查询是否已存在
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key)
        )
        config = result.scalar_one_or_none()
        
        if config:
            # 更新现有配置
            config.set_value(value)
            config.updated_by = user_id
        else:
            # 创建新配置
            config = SystemConfig(
                config_key=key,
                config_type=config_type,
                description=description or config_meta.get('description'),
                updated_by=user_id
            )
            config.set_value(value)
            db.add(config)
        
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"配置 {key} 已更新为 {value} (by user_id={user_id})")
        
        return config
    
    @staticmethod
    async def get_all_editable_configs(db: AsyncSession) -> Dict[str, Any]:
        """
        获取所有可编辑的配置（当前值）
        
        Returns:
            配置字典
        """
        configs = {}
        
        for key, meta in ConfigManager.EDITABLE_CONFIGS.items():
            value = await ConfigManager.get_config(db, key, meta['default'])
            configs[key] = {
                'value': value,
                'type': meta['type'],
                'default': meta['default'],
                'description': meta['description'],
                'min': meta.get('min'),
                'max': meta.get('max'),
            }
        
        return configs
    
    @staticmethod
    async def init_default_configs(db: AsyncSession, user_id: Optional[int] = None):
        """
        初始化默认配置（如果数据库中不存在）
        
        Args:
            db: 数据库会话
            user_id: 操作用户ID
        """
        count = 0
        
        for key, meta in ConfigManager.EDITABLE_CONFIGS.items():
            result = await db.execute(
                select(SystemConfig).where(SystemConfig.config_key == key)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                config = SystemConfig(
                    config_key=key,
                    config_type=meta['type'],
                    description=meta['description'],
                    updated_by=user_id
                )
                config.set_value(meta['default'])
                db.add(config)
                count += 1
        
        if count > 0:
            await db.commit()
            logger.info(f"初始化了 {count} 个默认配置")
        
        return count


# 全局配置管理器实例
config_manager = ConfigManager()

