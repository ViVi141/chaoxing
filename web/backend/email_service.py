# -*- coding: utf-8 -*-
"""
邮件服务模块 - 完整的SMTP邮件发送功能
"""
import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import settings
from api.logger import logger


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.enabled = settings.SMTP_ENABLED
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> MIMEMultipart:
        """创建邮件消息"""
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((self.from_name, self.from_email))
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加纯文本部分（可选）
        if text_content:
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part1)
        
        # 添加HTML部分
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)
        
        return msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）
        
        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.warning("SMTP未启用，邮件发送跳过")
            return False
        
        if not self.username or not self.password:
            logger.error("SMTP配置不完整，无法发送邮件")
            return False
        
        try:
            # 创建邮件
            msg = self._create_message(to_email, subject, html_content, text_content)
            
            # 连接SMTP服务器
            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=10)
            
            # 登录
            server.login(self.username, self.password)
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功: {to_email} - {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP认证失败: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误: {e}")
            return False
        except Exception as e:
            logger.error(f"发送邮件失败: {e}", exc_info=True)
            return False
    
    def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_url: str
    ) -> bool:
        """
        发送邮箱验证邮件
        
        Args:
            to_email: 收件人邮箱
            username: 用户名
            verification_url: 验证链接
        
        Returns:
            是否发送成功
        """
        subject = "【超星学习通】邮箱验证"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✉️ 邮箱验证</h1>
                </div>
                <div class="content">
                    <p>您好，<strong>{username}</strong>！</p>
                    <p>感谢您注册超星学习通多用户管理平台。</p>
                    <p>请点击下面的按钮验证您的邮箱地址：</p>
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">验证邮箱</a>
                    </div>
                    <p>或复制以下链接到浏览器：</p>
                    <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {verification_url}
                    </p>
                    <p><strong>此链接将在30分钟后过期。</strong></p>
                    <p>如果您没有注册此账号，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>超星学习通多用户管理平台 v2.0</p>
                    <p>此邮件为系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        邮箱验证
        
        您好，{username}！
        
        感谢您注册超星学习通多用户管理平台。
        
        请访问以下链接验证您的邮箱地址：
        {verification_url}
        
        此链接将在30分钟后过期。
        
        如果您没有注册此账号，请忽略此邮件。
        
        ---
        超星学习通多用户管理平台 v2.0
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_url: str
    ) -> bool:
        """
        发送密码重置邮件
        
        Args:
            to_email: 收件人邮箱
            username: 用户名
            reset_url: 重置链接
        
        Returns:
            是否发送成功
        """
        subject = "【超星学习通】密码重置"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 密码重置</h1>
                </div>
                <div class="content">
                    <p>您好，<strong>{username}</strong>！</p>
                    <p>我们收到了您的密码重置请求。</p>
                    <p>请点击下面的按钮重置您的密码：</p>
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码</a>
                    </div>
                    <p>或复制以下链接到浏览器：</p>
                    <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_url}
                    </p>
                    <div class="warning">
                        <p><strong>⚠️ 安全提示：</strong></p>
                        <ul>
                            <li>此链接将在30分钟后过期</li>
                            <li>每个重置链接只能使用一次</li>
                            <li>如果您没有请求重置密码，请忽略此邮件</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>超星学习通多用户管理平台 v2.0</p>
                    <p>此邮件为系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        密码重置
        
        您好，{username}！
        
        我们收到了您的密码重置请求。
        
        请访问以下链接重置您的密码：
        {reset_url}
        
        安全提示：
        - 此链接将在30分钟后过期
        - 每个重置链接只能使用一次
        - 如果您没有请求重置密码，请忽略此邮件
        
        ---
        超星学习通多用户管理平台 v2.0
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """
        发送欢迎邮件
        
        Args:
            to_email: 收件人邮箱
            username: 用户名
        
        Returns:
            是否发送成功
        """
        subject = "【超星学习通】欢迎加入！"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 欢迎加入！</h1>
                </div>
                <div class="content">
                    <p>您好，<strong>{username}</strong>！</p>
                    <p>欢迎使用超星学习通多用户管理平台！</p>
                    
                    <h3>🌟 平台功能：</h3>
                    <div class="feature">
                        <strong>📚 自动学习</strong><br>
                        支持视频、音频、文档、测验等多种任务类型自动完成
                    </div>
                    <div class="feature">
                        <strong>🎯 智能题库</strong><br>
                        集成多个题库，自动答题，可配置覆盖率
                    </div>
                    <div class="feature">
                        <strong>⚡ 实时进度</strong><br>
                        WebSocket实时推送任务进度，随时掌握学习状态
                    </div>
                    <div class="feature">
                        <strong>📊 数据统计</strong><br>
                        完整的任务历史记录和统计数据
                    </div>
                    
                    <h3>📝 快速开始：</h3>
                    <ol>
                        <li>登录系统</li>
                        <li>配置超星账号（个人中心 → 配置管理）</li>
                        <li>创建学习任务</li>
                        <li>启动任务并查看实时进度</li>
                    </ol>
                    
                    <p>如有任何问题，请联系管理员。</p>
                    <p>祝您学习愉快！</p>
                </div>
                <div class="footer">
                    <p>超星学习通多用户管理平台 v2.0</p>
                    <p>此邮件为系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        欢迎加入！
        
        您好，{username}！
        
        欢迎使用超星学习通多用户管理平台！
        
        平台功能：
        - 自动学习：支持视频、音频、文档、测验等
        - 智能题库：自动答题，可配置覆盖率
        - 实时进度：WebSocket实时推送
        - 数据统计：完整的历史记录
        
        快速开始：
        1. 登录系统
        2. 配置超星账号
        3. 创建学习任务
        4. 启动并查看进度
        
        如有任何问题，请联系管理员。
        
        ---
        超星学习通多用户管理平台 v2.0
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_task_notification(
        self,
        to_email: str,
        username: str,
        task_name: str,
        status: str,
        message: str
    ) -> bool:
        """
        发送任务通知邮件
        
        Args:
            to_email: 收件人邮箱
            username: 用户名
            task_name: 任务名称
            status: 任务状态
            message: 通知消息
        
        Returns:
            是否发送成功
        """
        status_emoji = {
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⚠️"
        }
        emoji = status_emoji.get(status, "ℹ️")
        
        subject = f"【超星学习通】{emoji} 任务{status}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .task-info {{ background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{emoji} 任务通知</h1>
                </div>
                <div class="content">
                    <p>您好，<strong>{username}</strong>！</p>
                    <div class="task-info">
                        <p><strong>任务名称：</strong>{task_name}</p>
                        <p><strong>任务状态：</strong>{status}</p>
                        <p><strong>详细信息：</strong>{message}</p>
                        <p><strong>时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <p>您可以登录系统查看详细信息。</p>
                </div>
                <div class="footer">
                    <p>超星学习通多用户管理平台 v2.0</p>
                    <p>此邮件为系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        任务通知
        
        您好，{username}！
        
        任务名称：{task_name}
        任务状态：{status}
        详细信息：{message}
        时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        您可以登录系统查看详细信息。
        
        ---
        超星学习通多用户管理平台 v2.0
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    @staticmethod
    def generate_verification_token() -> str:
        """生成验证令牌"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_code() -> str:
        """生成6位验证码"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


# 创建全局邮件服务实例
email_service = EmailService()


async def create_email_verification(
    user_id: int,
    email: str,
    token_type: str = "verify_email"
) -> tuple[str, datetime]:
    """
    创建邮箱验证令牌
    
    Args:
        user_id: 用户ID
        email: 邮箱地址
        token_type: 令牌类型（verify_email, reset_password）
    
    Returns:
        (token, expires_at)
    """
    from database import AsyncSessionLocal
    from models import EmailVerification
    
    token = EmailService.generate_verification_token()
    
    # 设置过期时间
    if token_type == "reset_password":
        expires_minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES
    else:
        expires_minutes = settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
    
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    
    # 保存到数据库
    async with AsyncSessionLocal() as db:
        verification = EmailVerification(
            user_id=user_id,
            email=email,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
        db.add(verification)
        await db.commit()
    
    logger.info(f"创建邮箱验证令牌: user_id={user_id}, type={token_type}")
    return token, expires_at


async def verify_email_token(token: str, token_type: str = "verify_email") -> Optional[int]:
    """
    验证邮箱令牌
    
    Args:
        token: 验证令牌
        token_type: 令牌类型
    
    Returns:
        用户ID，失败返回None
    """
    from database import AsyncSessionLocal
    from models import EmailVerification, User
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        # 查询令牌
        result = await db.execute(
            select(EmailVerification).where(
                EmailVerification.token == token,
                EmailVerification.token_type == token_type,
                EmailVerification.is_used == False
            )
        )
        verification = result.scalar_one_or_none()
        
        if not verification:
            logger.warning(f"无效的验证令牌: {token[:10]}...")
            return None
        
        if verification.is_expired():
            logger.warning(f"验证令牌已过期: {token[:10]}...")
            return None
        
        # 标记为已使用
        verification.is_used = True
        
        # 如果是邮箱验证，更新用户的邮箱验证状态
        if token_type == "verify_email":
            user_result = await db.execute(
                select(User).where(User.id == verification.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user.email_verified = True
                logger.info(f"用户{user.username}邮箱验证成功")
        
        await db.commit()
        
        return verification.user_id


# 导出
__all__ = [
    'EmailService',
    'email_service',
    'create_email_verification',
    'verify_email_token'
]

