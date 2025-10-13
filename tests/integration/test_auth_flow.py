# -*- coding: utf-8 -*-
"""
测试认证流程
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.auth
class TestAuthFlow:
    """测试认证流程"""

    async def test_user_registration_and_login(self, test_user):
        """测试用户注册和登录流程"""
        # 使用test_user fixture，避免重复创建

        # 1. 验证用户创建成功
        assert test_user.id is not None
        assert test_user.username == "testuser"
        assert test_user.email == "test@example.com"

        # 2. 验证密码
        is_valid = test_user.check_password("Test123456!")
        assert is_valid == True

        # 3. 导入并创建访问令牌
        from web.backend.auth import create_access_token

        token = create_access_token(data={"sub": test_user.username})
        assert token is not None
        assert len(token) > 0

    async def test_password_change(self, async_db_session: AsyncSession, test_user):
        """测试密码修改流程"""
        old_password = "Test123456!"
        new_password = "NewPassword123!"

        # 1. 验证旧密码
        assert test_user.check_password(old_password) == True

        # 2. 设置新密码
        test_user.set_password(new_password)
        await async_db_session.commit()

        # 3. 验证新密码
        assert test_user.check_password(new_password) == True
        assert test_user.check_password(old_password) == False

    async def test_user_roles(
        self, async_db_session: AsyncSession, test_user, test_admin
    ):
        """测试用户角色"""
        # 普通用户
        assert test_user.role == "user"
        assert test_user.is_admin == False

        # 管理员
        assert test_admin.role == "admin"
        assert test_admin.is_admin == True
