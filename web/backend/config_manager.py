# -*- coding: utf-8 -*-
"""
配置管理器 - 支持Web界面配置
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from api.logger import logger


class ConfigManager:
    """配置管理器，用于保存和加载Web界面配置"""
    
    CONFIG_FILE = "web_config.json"
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            
        Returns:
            是否成功
        """
        try:
            config_path = Path(cls.CONFIG_FILE)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到 {config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    @classmethod
    def load_config(cls) -> Optional[Dict[str, Any]]:
        """
        从文件加载配置
        
        Returns:
            配置字典，失败返回None
        """
        try:
            config_path = Path(cls.CONFIG_FILE)
            if not config_path.exists():
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载配置从 {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return None
    
    @classmethod
    def config_exists(cls) -> bool:
        """检查配置文件是否存在"""
        return Path(cls.CONFIG_FILE).exists()
    
    @classmethod
    def apply_config(cls, config: Dict[str, Any]) -> None:
        """
        应用配置到环境变量
        
        Args:
            config: 配置字典
        """
        # 部署模式
        if 'deploy_mode' in config:
            os.environ['DEPLOY_MODE'] = config['deploy_mode']
        
        # 数据库配置
        if config.get('deploy_mode') == 'simple':
            os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./chaoxing_web.db'
            os.environ['CELERY_BROKER_URL'] = 'filesystem://'
            os.environ['CELERY_RESULT_BACKEND'] = 'file://./celery_results'
        elif 'database_url' in config:
            os.environ['DATABASE_URL'] = config['database_url']
            if 'redis_url' in config:
                os.environ['REDIS_URL'] = config['redis_url']
                os.environ['CELERY_BROKER_URL'] = config['redis_url']
                os.environ['CELERY_RESULT_BACKEND'] = config['redis_url']
        
        # 安全密钥
        if 'secret_key' in config and config['secret_key']:
            os.environ['SECRET_KEY'] = config['secret_key']
        if 'jwt_secret_key' in config and config['jwt_secret_key']:
            os.environ['JWT_SECRET_KEY'] = config['jwt_secret_key']
        
        # 系统配置
        if 'max_tasks_per_user' in config:
            os.environ['MAX_CONCURRENT_TASKS_PER_USER'] = str(config['max_tasks_per_user'])
        if 'task_timeout' in config:
            os.environ['TASK_TIMEOUT'] = str(config['task_timeout'] * 60)  # 转换为秒
        
        logger.info("配置已应用到环境变量")
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'deploy_mode': 'simple',
            'platform_name': '超星学习通管理平台',
            'max_tasks_per_user': 3,
            'task_timeout': 120,  # 分钟
            'enable_register': True,
            'enable_email_notification': False,
            'log_retention_days': 30,
            'secret_key': '',  # 由用户设置或自动生成
            'jwt_secret_key': '',  # 由用户设置或自动生成
        }
    
    @classmethod
    def generate_secret_keys(cls) -> Dict[str, str]:
        """生成安全密钥"""
        import secrets
        return {
            'secret_key': secrets.token_urlsafe(32),
            'jwt_secret_key': secrets.token_urlsafe(32)
        }
    
    @classmethod
    def init_config(cls) -> Dict[str, Any]:
        """
        初始化配置
        如果配置文件不存在，创建默认配置并生成密钥
        """
        config = cls.load_config()
        if config is None:
            config = cls.get_default_config()
            # 生成安全密钥
            keys = cls.generate_secret_keys()
            config.update(keys)
            # 保存配置
            cls.save_config(config)
            logger.info("已创建默认配置文件")
        
        # 应用配置到环境变量
        cls.apply_config(config)
        return config


# 在应用启动时加载配置
def load_and_apply_config():
    """加载并应用配置"""
    manager = ConfigManager()
    return manager.init_config()

