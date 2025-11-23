# -*- coding: utf-8 -*-
"""
认证相关路由
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, UserConfig
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    MessageResponse,
    EmailVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    VerifyEmailToken,
)
from security import AuthService, get_current_active_user
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册（邮箱必填）

    - **username**: 用户名（3-80字符）
    - **email**: 邮箱（必填）
    - **password**: 密码（至少6字符）

    注册后会发送验证邮件到您的邮箱
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 检查邮箱是否已存在（必填）
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        role="user",
        email_verified=False,  # ✅ 默认未验证
    )
    user.set_password(user_data.password)

    # 创建用户配置
    config = UserConfig(user=user)

    db.add(user)
    db.add(config)
    await db.commit()
    await db.refresh(user)

    # ✅ 发送验证邮件
    try:
        from email_service import email_service, create_email_verification
        from config import settings

        # 创建验证令牌
        token, expires_at = await create_email_verification(
            user_id=user.id, email=user.email, token_type="verify_email"
        )

        # 生成验证链接
        verification_url = f"http://localhost:5173/verify-email?token={token}"

        # 发送验证邮件
        if settings.SMTP_ENABLED:
            email_service.send_verification_email(
                to_email=user.email,
                username=user.username,
                verification_url=verification_url,
            )
            logger.info(f"验证邮件已发送至: {user.email}")
        else:
            logger.warning("SMTP未启用，验证邮件未发送")

    except Exception as e:
        logger.error(f"发送验证邮件失败: {e}")
        # 注册仍然成功，只是邮件发送失败

    # 生成JWT令牌
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "username": user.username}
    )

    logger.info(f"新用户注册: {user.username} (ID: {user.id}, Email: {user.email})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    用户登录（支持用户名或邮箱登录）

    使用OAuth2密码模式，Content-Type: application/x-www-form-urlencoded

    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    # ✅ 支持用户名或邮箱登录
    # 先尝试用户名
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    # 如果用户名找不到，尝试邮箱
    if not user:
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()

    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用"
        )

    # 更新最后登录时间
    from datetime import datetime

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # 生成令牌（sub必须是字符串）
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "username": user.username}
    )

    logger.info(f"用户登录: {user.username} (ID: {user.id})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出

    注意：JWT是无状态的，实际的登出需要在客户端删除令牌
    """
    logger.info(f"用户登出: {current_user.username}")
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户信息
    """
    # 预加载配置
    await db.refresh(current_user, ["config"])
    return current_user.to_dict(include_config=True)


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """
    刷新访问令牌
    """
    access_token = AuthService.create_access_token(
        data={
            "sub": str(current_user.id),
            "role": current_user.role,
            "username": current_user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": current_user.to_dict(),
    }


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailToken, db: AsyncSession = Depends(get_db)):
    """
    验证邮箱

    - **token**: 验证令牌（从邮件中获取）
    """
    from email_service import verify_email_token

    user_id = await verify_email_token(data.token, "verify_email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证令牌无效或已过期"
        )

    return {"message": "邮箱验证成功"}


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    重新发送验证邮件

    需要登录后调用
    """
    if current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已验证，无需重复验证"
        )

    try:
        from email_service import email_service, create_email_verification
        from config import settings

        # 创建新的验证令牌
        token, expires_at = await create_email_verification(
            user_id=current_user.id, email=current_user.email, token_type="verify_email"
        )

        # 生成验证链接
        verification_url = f"http://localhost:5173/verify-email?token={token}"

        # 发送验证邮件
        if settings.SMTP_ENABLED:
            success = email_service.send_verification_email(
                to_email=current_user.email,
                username=current_user.username,
                verification_url=verification_url,
            )
            if success:
                logger.info(f"重新发送验证邮件至: {current_user.email}")
                return {"message": "验证邮件已发送，请查收"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="发送邮件失败，请稍后重试",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="邮件服务未启用"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新发送验证邮件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发送验证邮件失败"
        )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    """
    忘记密码 - 发送重置链接

    - **email**: 注册邮箱
    """
    # 查找用户
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # 为了安全，不论用户是否存在都返回成功
    # 避免通过此接口判断邮箱是否已注册
    if not user:
        logger.warning(f"密码重置请求：邮箱不存在 - {data.email}")
        return {"message": "如果该邮箱已注册，将收到密码重置邮件"}

    try:
        from email_service import email_service, create_email_verification
        from config import settings

        # 创建重置令牌
        token, expires_at = await create_email_verification(
            user_id=user.id, email=user.email, token_type="reset_password"
        )

        # 生成重置链接
        reset_url = f"http://localhost:5173/reset-password?token={token}"

        # 发送重置邮件
        if settings.SMTP_ENABLED:
            email_service.send_password_reset_email(
                to_email=user.email, username=user.username, reset_url=reset_url
            )
            logger.info(f"密码重置邮件已发送至: {user.email}")
        else:
            logger.warning("SMTP未启用，重置邮件未发送")

    except Exception as e:
        logger.error(f"发送重置邮件失败: {e}")
        # 即使发送失败，也返回成功消息（安全考虑）

    return {"message": "如果该邮箱已注册，将收到密码重置邮件"}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    重置密码

    - **token**: 重置令牌（从邮件中获取）
    - **new_password**: 新密码（至少6字符）
    """
    from email_service import verify_email_token

    # 验证令牌
    user_id = await verify_email_token(data.token, "reset_password")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="重置令牌无效或已过期"
        )

    # 更新密码
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    user.set_password(data.new_password)
    await db.commit()

    logger.info(f"用户{user.username}重置密码成功")

    return {"message": "密码重置成功，请使用新密码登录"}


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    要求管理员权限的依赖函数

    Args:
        current_user: 当前用户（从get_current_active_user获取）

    Returns:
        User: 管理员用户对象

    Raises:
        HTTPException: 用户不是管理员
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return current_user


async def init_default_admin():
    """
    初始化默认管理员账号（如果不存在）
    在应用启动时调用
    """
    from database import AsyncSessionLocal
    from config import settings
    
    try:
        async with AsyncSessionLocal() as db:
            try:
                # 检查是否已存在管理员
                result = await db.execute(
                    select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
                )
                admin = result.scalar_one_or_none()
                
                if not admin:
                    # 创建默认管理员
                    logger.info("🔍 开始创建默认管理员...")
                    admin = User(
                        username=settings.DEFAULT_ADMIN_USERNAME,
                        email=settings.DEFAULT_ADMIN_EMAIL,
                        role="admin",
                        is_active=True,
                        email_verified=True,  # 默认管理员邮箱已验证
                    )
                    admin.set_password(settings.DEFAULT_ADMIN_PASSWORD)
                    
                    # 创建用户配置
                    from models import UserConfig
                    config = UserConfig(user=admin)
                    
                    db.add(admin)
                    db.add(config)
                    await db.commit()
                    await db.refresh(admin)
                    
                    logger.info(f"✅ 默认管理员已创建: {admin.username}")
                    logger.info(f"   用户名: {settings.DEFAULT_ADMIN_USERNAME}")
                    logger.info(f"   密码: {settings.DEFAULT_ADMIN_PASSWORD}")
                    logger.info(f"   邮箱: {settings.DEFAULT_ADMIN_EMAIL}")
                    logger.warning("⚠️  请登录后立即修改默认密码！")
                else:
                    logger.info(f"✅ 默认管理员已存在: {admin.username}")
                    logger.debug(f"   用户ID: {admin.id}, 邮箱: {admin.email}")
                    # 确保密码是最新的（如果配置有变或密码不匹配）
                    if not admin.check_password(settings.DEFAULT_ADMIN_PASSWORD):
                        logger.info(f"🔄 更新默认管理员密码...")
                        admin.set_password(settings.DEFAULT_ADMIN_PASSWORD)
                        await db.commit()
                        logger.info(f"✅ 默认管理员密码已更新为: {settings.DEFAULT_ADMIN_PASSWORD}")
                    else:
                        logger.debug(f"   密码验证通过（默认密码）")
            except Exception as inner_e:
                await db.rollback()
                raise inner_e
    except Exception as e:
        logger.error(f"❌ 初始化默认管理员失败: {e}", exc_info=True)
        logger.error(f"   错误类型: {type(e).__name__}")
        logger.error("   请检查数据库连接和配置")
        # 不抛出异常，允许应用继续启动，但记录错误


# 重新导出，供其他路由文件使用
# 这样其他文件可以从 auth 导入，而不需要直接导入 security
__all__ = ["router", "AuthService", "get_current_active_user", "require_admin", "init_default_admin"]