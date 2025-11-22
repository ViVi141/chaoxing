# -*- coding: utf-8 -*-
"""
系统配置管理路由 - 管理员可在前端配置SMTP等系统参数
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from database import get_db
from models import User, SystemConfig
from routes.auth import require_admin
from config import settings
from config_manager import config_manager
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


# ============= Schemas =============


class SystemConfigItem(BaseModel):
    """系统配置项"""

    config_key: str
    config_value: Optional[str]
    config_type: str = "string"
    description: Optional[str] = None
    is_sensitive: bool = False


class SystemConfigUpdate(BaseModel):
    """系统配置更新"""

    configs: List[SystemConfigItem]


class SMTPConfigResponse(BaseModel):
    """SMTP配置响应"""

    smtp_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_from_email: str
    smtp_from_name: str
    smtp_use_tls: bool


class SMTPConfigUpdate(BaseModel):
    """SMTP配置更新"""

    smtp_enabled: bool = Field(..., description="是否启用SMTP")
    smtp_host: str = Field(..., description="SMTP服务器")
    smtp_port: int = Field(..., description="SMTP端口")
    smtp_username: str = Field(..., description="SMTP用户名")
    smtp_password: Optional[str] = Field(None, description="SMTP密码（留空则不修改）")
    smtp_from_email: str = Field(..., description="发件人邮箱")
    smtp_from_name: str = Field(default="超星学习通", description="发件人名称")
    smtp_use_tls: bool = Field(default=True, description="使用TLS")


# ============= Helper Functions =============


async def get_or_create_config(
    db: AsyncSession,
    key: str,
    default_value: str = "",
    config_type: str = "string",
    description: str = "",
    is_sensitive: bool = False,
) -> SystemConfig:
    """获取或创建配置项"""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == key)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = SystemConfig(
            config_key=key,
            config_value=default_value,
            config_type=config_type,
            description=description,
            is_sensitive=is_sensitive,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return config


async def apply_smtp_config_to_settings(db: AsyncSession):
    """从数据库加载SMTP配置到settings"""
    smtp_configs = {
        "smtp_enabled": "SMTP_ENABLED",
        "smtp_host": "SMTP_HOST",
        "smtp_port": "SMTP_PORT",
        "smtp_username": "SMTP_USERNAME",
        "smtp_password": "SMTP_PASSWORD",
        "smtp_from_email": "SMTP_FROM_EMAIL",
        "smtp_from_name": "SMTP_FROM_NAME",
        "smtp_use_tls": "SMTP_USE_TLS",
    }

    for db_key, settings_key in smtp_configs.items():
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == db_key)
        )
        config = result.scalar_one_or_none()

        if config:
            value = config.get_value()
            if value is not None:
                setattr(settings, settings_key, value)
                logger.debug(
                    f"应用系统配置: {settings_key} = {value if not config.is_sensitive else '***'}"
                )


# ============= API Endpoints =============


@router.get("/smtp")
async def get_smtp_config(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    获取SMTP配置

    管理员专用
    """
    # 从数据库加载配置（如果有）
    await apply_smtp_config_to_settings(db)

    return {
        "smtp_enabled": settings.SMTP_ENABLED,
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_username": settings.SMTP_USERNAME,
        "smtp_password": "***" if settings.SMTP_PASSWORD else "",  # 不返回实际密码
        "smtp_from_email": settings.SMTP_FROM_EMAIL,
        "smtp_from_name": settings.SMTP_FROM_NAME,
        "smtp_use_tls": settings.SMTP_USE_TLS,
    }


@router.put("/smtp")
async def update_smtp_config(
    config_data: SMTPConfigUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    更新SMTP配置

    管理员专用
    """
    configs_to_update = {
        "smtp_enabled": (str(config_data.smtp_enabled), "bool", "是否启用SMTP", False),
        "smtp_host": (config_data.smtp_host, "string", "SMTP服务器地址", False),
        "smtp_port": (str(config_data.smtp_port), "int", "SMTP端口", False),
        "smtp_username": (config_data.smtp_username, "string", "SMTP用户名", False),
        "smtp_from_email": (config_data.smtp_from_email, "string", "发件人邮箱", False),
        "smtp_from_name": (config_data.smtp_from_name, "string", "发件人名称", False),
        "smtp_use_tls": (str(config_data.smtp_use_tls), "bool", "使用TLS", False),
    }

    # 如果提供了密码，也更新密码
    if config_data.smtp_password:
        configs_to_update["smtp_password"] = (
            config_data.smtp_password,
            "string",
            "SMTP密码",
            True,
        )

    # 更新所有配置
    for key, (value, config_type, desc, sensitive) in configs_to_update.items():
        config = await get_or_create_config(
            db, key, value, config_type, desc, sensitive
        )
        config.set_value(value)
        config.updated_by = admin_user.id
        await db.commit()

    # 应用到当前settings
    await apply_smtp_config_to_settings(db)

    logger.info(f"管理员{admin_user.username}更新了SMTP配置")

    return {"message": "SMTP配置已更新"}


class SMTPTestRequest(BaseModel):
    """SMTP测试请求"""

    to_email: Optional[str] = Field(
        None, description="接收测试邮件的邮箱（留空则发送到管理员邮箱）"
    )


@router.post("/smtp/test")
async def test_smtp(
    test_request: SMTPTestRequest = None,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    测试SMTP配置

    发送测试邮件到指定邮箱或管理员邮箱
    """
    # 加载最新配置
    await apply_smtp_config_to_settings(db)

    if not settings.SMTP_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SMTP未启用"
        )

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SMTP配置不完整"
        )

    # 确定收件邮箱
    to_email = (
        test_request.to_email
        if test_request and test_request.to_email
        else admin_user.email
    )

    try:
        from email_service import EmailService

        email_service = EmailService()

        # 发送测试邮件
        success = email_service.send_email(
            to_email=to_email,
            subject="【超星学习通】SMTP测试成功",
            html_content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #52c41a; border-bottom: 2px solid #52c41a; padding-bottom: 10px;">
                        ✅ SMTP测试成功
                    </h2>
                    <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px; margin: 20px 0;">
                        <p><strong>恭喜！</strong>您的SMTP配置正确，邮件服务工作正常。</p>
                        <p><strong>服务器信息：</strong></p>
                        <ul>
                            <li>SMTP服务器: {settings.SMTP_HOST}</li>
                            <li>端口: {settings.SMTP_PORT}</li>
                            <li>发件人: {settings.SMTP_USERNAME}</li>
                            <li>收件人: {to_email}</li>
                        </ul>
                        <p><strong>测试时间：</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        <p>此邮件由超星学习通自动化系统发送，用于测试SMTP配置。</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_content=f"SMTP测试成功！服务器: {settings.SMTP_HOST}:{settings.SMTP_PORT}",
        )

        if success:
            logger.info(f"SMTP测试邮件已发送至: {to_email}")
            return {
                "message": "测试邮件已发送成功",
                "detail": f"邮件已发送至: {to_email}，请检查收件箱（可能在垃圾邮件中）",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="邮件发送失败，请检查SMTP配置和网络连接",
            )

    except Exception as e:
        logger.error(f"SMTP测试失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SMTP测试失败: {str(e)}",
        )


@router.get("/all")
async def get_all_configs(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    获取所有系统配置

    管理员专用
    """
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()

    return {"configs": [config.to_dict(hide_sensitive=True) for config in configs]}


@router.put("/batch")
async def update_configs_batch(
    config_update: SystemConfigUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    批量更新系统配置

    管理员专用
    """
    updated_keys = []

    for item in config_update.configs:
        config = await get_or_create_config(
            db,
            item.config_key,
            item.config_value or "",
            item.config_type,
            item.description or "",
            item.is_sensitive,
        )
        config.set_value(item.config_value)
        config.updated_by = admin_user.id
        updated_keys.append(item.config_key)

    await db.commit()

    # 应用SMTP配置
    if any("smtp" in key for key in updated_keys):
        await apply_smtp_config_to_settings(db)

    logger.info(
        f"管理员{admin_user.username}批量更新了系统配置: {', '.join(updated_keys)}"
    )

    return {"message": f"已更新{len(updated_keys)}项配置", "updated_keys": updated_keys}


@router.post("/init-defaults")
async def init_default_configs(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    初始化默认系统配置

    从.env读取当前配置并写入数据库
    """
    default_configs = [
        # SMTP配置
        ("smtp_enabled", str(settings.SMTP_ENABLED), "bool", "是否启用SMTP", False),
        ("smtp_host", settings.SMTP_HOST, "string", "SMTP服务器地址", False),
        ("smtp_port", str(settings.SMTP_PORT), "int", "SMTP端口", False),
        ("smtp_username", settings.SMTP_USERNAME, "string", "SMTP用户名", False),
        ("smtp_password", settings.SMTP_PASSWORD, "string", "SMTP密码", True),
        ("smtp_from_email", settings.SMTP_FROM_EMAIL, "string", "发件人邮箱", False),
        ("smtp_from_name", settings.SMTP_FROM_NAME, "string", "发件人名称", False),
        ("smtp_use_tls", str(settings.SMTP_USE_TLS), "bool", "使用TLS", False),
        # 任务配置
        (
            "max_concurrent_tasks",
            str(settings.MAX_CONCURRENT_TASKS_PER_USER),
            "int",
            "每用户最大并发任务数",
            False,
        ),
        (
            "task_timeout",
            str(settings.TASK_TIMEOUT),
            "int",
            "任务超时时间（秒）",
            False,
        ),
        # 邮箱验证配置
        (
            "email_verification_expire",
            str(settings.EMAIL_VERIFICATION_EXPIRE_MINUTES),
            "int",
            "邮箱验证过期时间（分钟）",
            False,
        ),
        (
            "password_reset_expire",
            str(settings.PASSWORD_RESET_EXPIRE_MINUTES),
            "int",
            "密码重置过期时间（分钟）",
            False,
        ),
    ]

    created_count = 0
    updated_count = 0

    for key, value, config_type, desc, sensitive in default_configs:
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key)
        )
        config = result.scalar_one_or_none()

        if config:
            # 更新现有配置
            config.set_value(value)
            config.config_type = config_type
            config.description = desc
            config.is_sensitive = sensitive
            config.updated_by = admin_user.id
            updated_count += 1
        else:
            # 创建新配置
            config = SystemConfig(
                config_key=key,
                config_value=value,
                config_type=config_type,
                description=desc,
                is_sensitive=sensitive,
                updated_by=admin_user.id,
            )
            db.add(config)
            created_count += 1

    await db.commit()

    logger.info(
        f"管理员{admin_user.username}初始化系统配置: 创建{created_count}项, 更新{updated_count}项"
    )

    return {
        "message": "系统配置初始化成功",
        "created": created_count,
        "updated": updated_count,
    }


@router.get("/system-params")
async def get_system_params(admin_user: User = Depends(require_admin)):
    """
    获取系统参数（只读，从.env读取）

    这些参数不能通过API修改，需要修改.env文件并重启服务
    """
    return {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT,
        },
        "deploy": {
            "mode": settings.DEPLOY_MODE,
        },
        "task": {
            "max_concurrent_tasks_per_user": settings.MAX_CONCURRENT_TASKS_PER_USER,
            "task_timeout": settings.TASK_TIMEOUT,
        },
        "pagination": {
            "default_page_size": settings.PAGE_SIZE,
            "max_page_size": settings.MAX_PAGE_SIZE,
        },
        "security": {
            "jwt_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "email_verification_expire_minutes": settings.EMAIL_VERIFICATION_EXPIRE_MINUTES,
            "password_reset_expire_minutes": settings.PASSWORD_RESET_EXPIRE_MINUTES,
        },
        "database": {
            "url": "***已配置***" if settings.DATABASE_URL else "未配置",
        },
        "cors": {
            "origins": settings.get_cors_origins(),
        },
    }


@router.get("/editable-configs")
async def get_editable_configs(
    db: AsyncSession = Depends(get_db), admin_user: User = Depends(require_admin)
):
    """
    获取所有可在线编辑的配置项

    管理员专用
    """
    try:
        configs = await config_manager.get_all_editable_configs(db)
        return {"configs": configs, "readonly_configs": config_manager.READONLY_CONFIGS}
    except Exception as e:
        logger.error(f"获取可编辑配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配置失败: {str(e)}",
        )


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""

    key: str
    value: Any


@router.put("/editable-config")
async def update_editable_config(
    request: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """
    更新单个可编辑配置项

    管理员专用
    """
    try:
        config = await config_manager.set_config(
            db, request.key, request.value, user_id=admin_user.id
        )

        return {
            "message": f"配置 {request.key} 已更新",
            "config": {
                "key": config.config_key,
                "value": config.get_value(),
                "description": config.description,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新配置失败: {str(e)}",
        )


@router.post("/init-editable-configs")
async def init_editable_configs(
    db: AsyncSession = Depends(get_db), admin_user: User = Depends(require_admin)
):
    """
    初始化可编辑配置的默认值

    管理员专用
    """
    try:
        count = await config_manager.init_default_configs(db, admin_user.id)
        return {"message": f"已初始化 {count} 个配置项", "count": count}
    except Exception as e:
        logger.error(f"初始化配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化配置失败: {str(e)}",
        )


@router.get("/smtp-templates")
async def get_smtp_templates(admin_user: User = Depends(require_admin)):
    """
    获取常用SMTP配置模板

    管理员专用
    """
    return {
        "templates": [
            {
                "name": "Gmail",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_use_tls": True,
                "note": "需要使用应用专用密码: https://myaccount.google.com/apppasswords",
            },
            {
                "name": "QQ邮箱",
                "smtp_host": "smtp.qq.com",
                "smtp_port": 587,
                "smtp_use_tls": True,
                "note": "需要开启SMTP服务并获取授权码",
            },
            {
                "name": "163邮箱",
                "smtp_host": "smtp.163.com",
                "smtp_port": 465,
                "smtp_use_tls": False,
                "note": "需要开启SMTP服务并获取授权密码",
            },
            {
                "name": "Outlook",
                "smtp_host": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "smtp_use_tls": True,
                "note": "使用Microsoft账号密码",
            },
            {
                "name": "腾讯企业邮箱",
                "smtp_host": "smtp.exmail.qq.com",
                "smtp_port": 465,
                "smtp_use_tls": False,
                "note": "企业邮箱账号密码",
            },
        ]
    }
