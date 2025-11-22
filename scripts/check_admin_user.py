#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 PostgreSQL 数据库中是否创建了默认管理员用户
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from sqlalchemy import select
from web.backend.database import AsyncSessionLocal, engine
from web.backend.models import User, Base
from web.backend.config import settings

async def check_admin_user():
    """检查默认管理员用户"""
    print("=" * 60)
    print("检查 PostgreSQL 默认管理员用户")
    print("=" * 60)
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"部署模式: {settings.DEPLOY_MODE}")
    print(f"默认管理员用户名: {settings.DEFAULT_ADMIN_USERNAME}")
    print(f"默认管理员邮箱: {settings.DEFAULT_ADMIN_EMAIL}")
    print("=" * 60)
    
    try:
        # 测试数据库连接
        async with engine.begin() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    try:
        # 检查表是否存在
        async with engine.begin() as conn:
            result = await conn.execute(
                sqlalchemy.text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
                )
            )
            table_exists = result.scalar()
        
        if not table_exists:
            print("❌ users 表不存在！")
            print("   请先启动应用以创建数据库表")
            return False
        
        print("✅ users 表存在")
        
        # 检查管理员用户
        async with AsyncSessionLocal() as db:
            # 查询所有用户
            result = await db.execute(select(User))
            all_users = result.scalars().all()
            
            print(f"\n📊 数据库中的用户总数: {len(all_users)}")
            
            if len(all_users) > 0:
                print("\n用户列表:")
                for user in all_users:
                    print(f"  - ID: {user.id}, 用户名: {user.username}, 角色: {user.role}, 邮箱: {user.email}, 激活: {user.is_active}")
            
            # 检查默认管理员
            result = await db.execute(
                select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
            )
            admin = result.scalar_one_or_none()
            
            if admin:
                print(f"\n✅ 找到默认管理员用户:")
                print(f"   ID: {admin.id}")
                print(f"   用户名: {admin.username}")
                print(f"   邮箱: {admin.email}")
                print(f"   角色: {admin.role}")
                print(f"   激活状态: {admin.is_active}")
                print(f"   邮箱已验证: {admin.email_verified}")
                print(f"   创建时间: {admin.created_at}")
                
                # 验证密码
                if admin.check_password(settings.DEFAULT_ADMIN_PASSWORD):
                    print(f"   ✅ 密码验证成功（默认密码: {settings.DEFAULT_ADMIN_PASSWORD}）")
                else:
                    print(f"   ⚠️  密码已修改（不是默认密码）")
                
                return True
            else:
                print(f"\n❌ 未找到默认管理员用户 '{settings.DEFAULT_ADMIN_USERNAME}'")
                print("   可能的原因:")
                print("   1. 应用启动时创建管理员失败（请查看日志）")
                print("   2. 管理员用户名被修改")
                print("   3. 数据库迁移时未包含管理员用户")
                return False
                
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    import sqlalchemy
    result = asyncio.run(check_admin_user())
    sys.exit(0 if result else 1)

