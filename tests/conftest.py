# -*- coding: utf-8 -*-
"""
pytest配置文件
提供通用的fixtures和配置
"""
import sys
import os
from pathlib import Path

# 在导入任何其他模块之前设置测试环境变量
# 这很重要，因为database.py在导入时会立即创建引擎
# 使用共享内存数据库，确保所有连接使用同一个数据库
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file::memory:?cache=shared"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "True"
os.environ["DEPLOY_MODE"] = "simple"  # 使用简单模式（SQLite）

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "web" / "backend"))

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 导入模型（此时环境变量已设置，database.py会使用正确的数据库URL）
from web.backend.database import Base
from web.backend.models import User, UserConfig, Task, SystemConfig

# 注意：不再需要自定义event_loop fixture
# pytest-asyncio会自动管理事件循环


@pytest.fixture(scope="function")
async def async_db_engine():
    """异步数据库引擎（测试用）"""
    # 使用共享内存SQLite数据库，确保所有连接使用同一个数据库
    # 注意：必须与conftest.py顶部设置的DATABASE_URL一致
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///file::memory:?cache=shared")

    engine = create_async_engine(
        DATABASE_URL, 
        echo=False, 
        future=True,
        connect_args={"check_same_thread": False, "timeout": 20}  # SQLite特定配置
    )

    # 创建所有表
    # Base.metadata是独立的，不绑定到特定引擎
    # 使用这个引擎创建表，确保表在共享内存数据库中
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理（可选，因为内存数据库会在连接关闭时自动清理）
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_db_session(async_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """异步数据库会话"""
    async_session = async_sessionmaker(
        async_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def sync_db_engine():
    """同步数据库引擎（测试用）"""
    DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def sync_db_session(sync_db_engine) -> Generator[Session, None, None]:
    """同步数据库会话"""
    SessionLocal = sessionmaker(bind=sync_db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456!",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def test_admin_data():
    """测试管理员数据"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "Admin123456!",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
async def test_user(async_db_session: AsyncSession, test_user_data):
    """创建测试用户"""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        role=test_user_data["role"],
        is_active=test_user_data["is_active"],
    )
    user.set_password(test_user_data["password"])

    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)

    return user


@pytest.fixture
async def test_admin(async_db_session: AsyncSession, test_admin_data):
    """创建测试管理员"""
    admin = User(
        username=test_admin_data["username"],
        email=test_admin_data["email"],
        role=test_admin_data["role"],
        is_active=test_admin_data["is_active"],
    )
    admin.set_password(test_admin_data["password"])

    async_db_session.add(admin)
    await async_db_session.commit()
    await async_db_session.refresh(admin)

    return admin


@pytest.fixture
def mock_tiku_response():
    """模拟题库响应"""
    return {"success": True, "answer": "A", "confidence": 0.95}


@pytest.fixture
def mock_course_data():
    """模拟课程数据"""
    return {
        "courseId": "12345",
        "clazzId": "67890",
        "cpi": "111111",
        "title": "测试课程",
        "has_finished": False,
    }


# 标记所有异步测试
def pytest_collection_modifyitems(items):
    """自动标记异步测试"""
    for item in items:
        if asyncio.iscoroutinefunction(item.obj):
            item.add_marker(pytest.mark.asyncio)


# 测试环境配置
# 注意：环境变量已在文件顶部设置，这里不再重复设置
# 这个fixture保留用于其他可能的测试环境配置
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境变量（已在文件顶部设置）"""
    # 环境变量已在文件顶部设置，这里只是确保它们存在
    expected_db_url = "sqlite+aiosqlite:///file::memory:?cache=shared"
    actual_db_url = os.environ.get("DATABASE_URL")
    assert actual_db_url == expected_db_url, f"Expected DATABASE_URL={expected_db_url}, got {actual_db_url}"
    assert os.environ.get("TESTING") == "1"
    
    yield
    
    # 测试结束后不清理环境变量，因为可能有其他测试需要
    # 如果需要清理，可以取消下面的注释
    # for key in ["TESTING", "DATABASE_URL", "SECRET_KEY", "DEBUG", "DEPLOY_MODE"]:
    #     os.environ.pop(key, None)
