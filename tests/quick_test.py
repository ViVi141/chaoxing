#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证数据库表创建和基本功能
"""
import sys
import os
from pathlib import Path
import tempfile
import asyncio

# Windows 控制台编码处理
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# 重要：将 web/backend 添加到路径，这样 models.py 中的 from database import Base 可以正常工作
sys.path.insert(0, str(project_root / "web" / "backend"))

# 设置测试环境变量
test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{test_db.name}"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "True"
os.environ["DEPLOY_MODE"] = "simple"

print(f"[INFO] 测试数据库文件: {test_db.name}")
print(f"[INFO] 数据库URL: {os.environ['DATABASE_URL']}")

# 导入数据库相关模块（必须先导入 Base）
# 注意：models.py 使用 from database import Base，所以需要确保路径正确
# 由于我们已经将 web/backend 添加到 sys.path，可以直接导入 database
from database import Base, engine as global_engine, AsyncSessionLocal, init_db

# 导入所有模型，确保它们注册到 Base.metadata
# 注意：必须在导入 Base 之后导入模型
# models.py 使用 from database import Base，所以需要确保 database 模块在路径中
# 我们需要导入整个 models 模块来触发所有模型的注册
import models  # 这会触发所有模型的注册
from models import User

# 验证模型是否已注册
print(f"[DEBUG] Base.metadata.tables 在导入模型后: {list(Base.metadata.tables.keys())}")

async def test_database():
    """测试数据库功能"""
    print("\n" + "="*60)
    print("[TEST] 开始快速测试")
    print("="*60)
    
    try:
        # 1. 创建表
        print("\n[STEP 1] 创建数据库表...")
        # 先检查 Base.metadata 中是否有表定义
        print(f"[DEBUG] Base.metadata.tables: {list(Base.metadata.tables.keys())}")
        
        # 使用 begin() 确保事务正确提交
        async with global_engine.begin() as conn:
            # 使用 run_sync 执行同步的 create_all
            def create_tables(connection):
                Base.metadata.create_all(connection)
            await conn.run_sync(create_tables)
        print("[OK] 表创建成功")
        
        # 2. 验证表是否存在
        print("\n[STEP 2] 验证表是否存在...")
        from sqlalchemy import text
        async with global_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            )
            tables = result.fetchall()
            if tables:
                print(f"[OK] 找到 users 表: {tables}")
            else:
                print("[ERROR] 未找到 users 表")
                # 列出所有表以便调试
                result_all = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                all_tables = result_all.fetchall()
                print(f"[DEBUG] 数据库中的所有表: {all_tables}")
                return False
        
        # 3. 创建测试用户
        print("\n[STEP 3] 创建测试用户...")
        async with AsyncSessionLocal() as session:
            user = User(
                username="testuser",
                email="test@example.com",
                role="user",
                is_active=True,
            )
            user.set_password("Test123456!")
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"[OK] 用户创建成功: ID={user.id}, username={user.username}")
        
        # 4. 查询用户
        print("\n[STEP 4] 查询用户...")
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.username == "testuser"))
            found_user = result.scalar_one_or_none()
            
            if found_user:
                print(f"[OK] 找到用户: ID={found_user.id}, username={found_user.username}, email={found_user.email}")
            else:
                print("[ERROR] 未找到用户")
                return False
        
        # 5. 验证密码
        print("\n[STEP 5] 验证密码...")
        if found_user.check_password("Test123456!"):
            print("[OK] 密码验证成功")
        else:
            print("[ERROR] 密码验证失败")
            return False
        
        print("\n" + "="*60)
        print("[SUCCESS] 所有测试通过！")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        print(f"\n[CLEANUP] 清理测试数据库文件: {test_db.name}")
        try:
            await global_engine.dispose()
            # 等待一下，确保文件释放
            await asyncio.sleep(0.1)
            if os.path.exists(test_db.name):
                os.unlink(test_db.name)
            print("[OK] 清理完成")
        except Exception as e:
            print(f"[WARNING] 清理时出错: {e}")
            print(f"[INFO] 数据库文件位置: {test_db.name} (可手动删除)")

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)

