"""
通知服务模块，用于向外部服务发送通知消息。
支持多种通知服务，如ServerChan、Qmsg和Bark。
"""

import configparser
import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from api.logger import logger


class NotificationService(ABC):
    """
    通知服务基类，定义通知服务的公共接口和实现。
    所有具体的通知服务类应继承此类并实现必要的方法。
    """

    CONFIG_PATH = "config.ini"
    
    def __init__(self):
        """初始化通知服务"""
        self.name = self.__class__.__name__
        self.url = ""
        self._conf = None
        self.disabled = False
        
    def config_set(self, config: Dict[str, str]) -> None:
        """
        设置通知服务的配置
        
        Args:
            config: 包含配置参数的字典
        """
        self._conf = config
        
    def _load_config_from_file(self) -> Optional[Dict[str, str]]:
        """
        从配置文件中加载通知服务的配置
        
        Returns:
            成功返回配置字典，失败返回None
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.CONFIG_PATH, encoding="utf8")
            return config['notification']
        except (KeyError, FileNotFoundError):
            logger.info("未找到notification配置，已忽略外部通知功能")
            self.disabled = True
            return None
    
    def init_notification(self) -> None:
        """初始化通知服务，加载配置并进行必要的设置"""
        if not self._conf:
            self._conf = self._load_config_from_file()
        
        if not self.disabled and self._conf:
            self._init_service()
    
    @abstractmethod
    def _init_service(self) -> None:
        """
        初始化特定的通知服务，由子类实现
        """
        pass
    
    @abstractmethod
    def _send(self, message: str) -> None:
        """
        发送通知消息，由子类实现
        
        Args:
            message: 要发送的消息内容
        """
        pass
    
    def send(self, message: str) -> None:
        """
        发送通知消息的公共接口
        
        Args:
            message: 要发送的消息内容
        """
        if not self.disabled:
            self._send(message)


class NotificationFactory:
    """
    通知服务工厂类，用于创建和获取通知服务实例
    """
    
    @staticmethod
    def create_service(config: Optional[Dict[str, str]] = None) -> NotificationService:
        """
        根据配置创建通知服务实例
        
        Args:
            config: 通知服务的配置，如果为None则从配置文件加载
            
        Returns:
            通知服务实例
        """
        service = DefaultNotification()
        
        if config:
            service.config_set(config)
        
        # 尝试获取具体的通知服务
        service = service.get_notification_from_config()
        service.init_notification()
        
        return service


class DefaultNotification(NotificationService):
    """
    默认通知服务，当未配置任何通知服务时使用
    """
    
    def _init_service(self) -> None:
        pass
    
    def _send(self, message: str) -> None:
        pass
    
    def get_notification_from_config(self) -> NotificationService:
        """
        根据配置创建具体的通知服务实例
        
        Returns:
            通知服务实例
        """
        if not self._conf:
            self._conf = self._load_config_from_file()
            
        if self.disabled:
            return self
            
        try:
            provider_name = self._conf['provider']
            if not provider_name:
                raise KeyError("未指定通知服务提供商")
                
            # 获取对应的通知服务类
            provider_class = globals().get(provider_name)
            if not provider_class:
                logger.error(f"未找到名为 {provider_name} 的通知服务提供商")
                self.disabled = True
                return self
                
            # 创建通知服务实例
            service = provider_class()
            service.config_set(self._conf)
            return service
            
        except KeyError:
            self.disabled = True
            logger.info("未找到外部通知配置，已忽略外部通知功能")
            return self


class ServerChan(NotificationService):
    """
    Server酱通知服务
    """
    
    def _init_service(self) -> None:
        """初始化Server酱服务"""
        if not self._conf or not self._conf.get('url'):
            self.disabled = True
            logger.info("未找到Server酱url配置，已忽略该通知服务")
            return
            
        self.url = self._conf['url']
        logger.info(f"已初始化Server酱通知服务，URL: {self.url}")
    
    def _send(self, message: str) -> None:
        """
        通过Server酱发送通知
        
        Args:
            message: 要发送的消息内容
        """
        params = {
            'text': message,  # 兼容两个版本的Server酱
            'desp': message,
        }
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        try:
            response = requests.post(self.url, json=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Server酱通知发送成功: {result}")
        except requests.RequestException as e:
            logger.error(f"Server酱通知发送失败: {e}")
        except ValueError as e:
            logger.error(f"Server酱返回数据解析失败: {e}")


class Qmsg(NotificationService):
    """
    Qmsg酱通知服务
    """
    
    def _init_service(self) -> None:
        """初始化Qmsg酱服务"""
        if not self._conf or not self._conf.get('url'):
            self.disabled = True
            logger.info("未找到Qmsg酱url配置，已忽略该通知服务")
            return
            
        self.url = self._conf['url']
        logger.info(f"已初始化Qmsg酱通知服务，URL: {self.url}")
    
    def _send(self, message: str) -> None:
        """
        通过Qmsg酱发送通知
        
        Args:
            message: 要发送的消息内容
        """
        params = {'msg': message}
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        
        try:
            response = requests.post(self.url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Qmsg酱通知发送成功: {result}")
        except requests.RequestException as e:
            logger.error(f"Qmsg酱通知发送失败: {e}")
        except ValueError as e:
            logger.error(f"Qmsg酱返回数据解析失败: {e}")


class Bark(NotificationService):
    """
    Bark通知服务
    """
    
    def _init_service(self) -> None:
        """初始化Bark服务"""
        if not self._conf or not self._conf.get('url'):
            self.disabled = True
            logger.info("未找到Bark的url配置，已忽略该通知服务")
            return
            
        self.url = self._conf['url']
        logger.info(f"已初始化Bark通知服务，URL: {self.url}")
    
    def _send(self, message: str) -> None:
        """
        通过Bark发送通知
        
        Args:
            message: 要发送的消息内容
        """
        params = {'body': message}
        
        try:
            response = requests.post(self.url, params=params)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Bark通知发送成功: {result}")
        except requests.RequestException as e:
            logger.error(f"Bark通知发送失败: {e}")
        except ValueError as e:
            logger.error(f"Bark返回数据解析失败: {e}")


class SMTP(NotificationService):
    """
    SMTP邮件通知服务
    """
    
    def _init_service(self) -> None:
        """初始化SMTP服务"""
        required_fields = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_to_email']
        
        # 检查必填字段
        for field in required_fields:
            if not self._conf or not self._conf.get(field):
                self.disabled = True
                logger.info(f"SMTP配置不完整（缺少{field}），已忽略SMTP通知服务")
                return
        
        self.smtp_host = self._conf['smtp_host']
        self.smtp_port = int(self._conf.get('smtp_port', 587))
        self.smtp_username = self._conf['smtp_username']
        self.smtp_password = self._conf['smtp_password']
        self.smtp_to_email = self._conf['smtp_to_email']
        self.smtp_from_name = self._conf.get('smtp_from_name', '超星学习通')
        self.smtp_use_tls = self._conf.get('smtp_use_tls', 'true').lower() in ['true', '1', 'yes']
        
        logger.info(f"已初始化SMTP通知服务，服务器: {self.smtp_host}:{self.smtp_port}")
    
    def _send(self, message: str) -> None:
        """
        通过SMTP发送邮件通知
        
        Args:
            message: 要发送的消息内容
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.utils import formataddr
        from datetime import datetime
        
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.smtp_from_name, self.smtp_username))
            msg['To'] = self.smtp_to_email
            msg['Subject'] = f'【超星学习通】任务通知 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            
            # 纯文本内容
            text_content = message
            
            # HTML内容（更美观）
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #1890ff; border-bottom: 2px solid #1890ff; padding-bottom: 10px;">
                        📚 超星学习通任务通知
                    </h2>
                    <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px; margin: 20px 0;">
                        <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: 'Courier New', monospace; font-size: 14px;">{message}</pre>
                    </div>
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        <p>此邮件由超星学习通自动化系统发送，请勿直接回复。</p>
                        <p style="color: #999;">发送时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 添加内容
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # 连接SMTP服务器并发送
            if self.smtp_use_tls:
                # 使用TLS加密（587端口）
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()
            else:
                # 使用SSL加密（465端口）
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, [self.smtp_to_email], msg.as_string())
            server.quit()
            
            logger.info(f"SMTP邮件通知发送成功: {self.smtp_to_email}")
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP邮件发送失败: {e}")
        except Exception as e:
            logger.error(f"SMTP邮件发送异常: {e}")


# 为了向后兼容，保留原来的Notification类
Notification = DefaultNotification