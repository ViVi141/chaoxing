#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖验证脚本
检查所有必需的Python包是否正确安装
"""

import sys
import importlib
from typing import List, Tuple

# 必需的核心依赖
CORE_DEPS = [
    "requests",
    "httpx",
    "urllib3",
    "beautifulsoup4",
    "lxml",
    "pyaes",
    "cryptography",
    "loguru",
    "argparse",
]

# Web平台依赖
WEB_DEPS = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "alembic",
    "pydantic",
    "python-jose",
    "passlib",
    "python-multipart",
    "email-validator",
    "websockets",
    "aiohttp",
    "python-dotenv",
]

# 可选依赖（如果缺失会警告但不报错）
OPTIONAL_DEPS = [
    ("redis", "Redis队列（标准模式需要）"),
    ("asyncpg", "PostgreSQL异步驱动（标准模式需要）"),
    ("psycopg2", "PostgreSQL同步驱动（Celery任务需要）"),
    ("aiosqlite", "SQLite异步驱动（简单模式需要）"),
    ("celery", "Celery任务队列"),
    ("ddddocr", "验证码识别（可选）"),
    ("openai", "AI题库（可选）"),
]

# 开发工具（可选）
DEV_DEPS = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-mock",
    "black",
    "flake8",
    "ruff",
]


def check_module(module_name: str) -> Tuple[bool, str]:
    """检查模块是否可以导入"""
    try:
        # 处理特殊模块名
        import_name = module_name
        if module_name == "beautifulsoup4":
            import_name = "bs4"
        elif module_name == "python-jose":
            import_name = "jose"
        elif module_name == "python-multipart":
            import_name = "multipart"
        elif module_name == "email-validator":
            import_name = "email_validator"
        
        importlib.import_module(import_name)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"未知错误: {str(e)}"


def check_dependencies(deps: List[str], category: str) -> Tuple[int, int]:
    """检查依赖列表，返回（成功数，总数）"""
    print(f"\n{'='*60}")
    print(f"检查 {category} 依赖")
    print(f"{'='*60}")
    
    success_count = 0
    total_count = len(deps)
    
    for dep in deps:
        success, error = check_module(dep)
        if success:
            print(f"  ✓ {dep}")
            success_count += 1
        else:
            print(f"  ✗ {dep} - 缺失")
            if error:
                print(f"    错误: {error}")
    
    return success_count, total_count


def main():
    print("="*60)
    print("依赖验证工具")
    print("="*60)
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查核心依赖
    core_success, core_total = check_dependencies(CORE_DEPS, "核心依赖")
    
    # 检查Web平台依赖
    web_success, web_total = check_dependencies(WEB_DEPS, "Web平台依赖")
    
    # 检查可选依赖
    print(f"\n{'='*60}")
    print("检查可选依赖")
    print(f"{'='*60}")
    optional_success = 0
    optional_total = len(OPTIONAL_DEPS)
    for dep_name, description in OPTIONAL_DEPS:
        success, error = check_module(dep_name)
        if success:
            print(f"  ✓ {dep_name} - {description}")
            optional_success += 1
        else:
            print(f"  ⚠ {dep_name} - 未安装 ({description})")
    
    # 总结
    print(f"\n{'='*60}")
    print("验证结果")
    print(f"{'='*60}")
    print(f"核心依赖: {core_success}/{core_total}")
    print(f"Web平台依赖: {web_success}/{web_total}")
    print(f"可选依赖: {optional_success}/{optional_total}")
    
    total_success = core_success + web_success
    total_required = core_total + web_total
    
    if core_success == core_total and web_success == web_total:
        print(f"\n✓ 所有必需依赖已正确安装！")
        return 0
    else:
        print(f"\n✗ 缺少 {total_required - total_success} 个必需依赖")
        print("\n请运行以下命令安装缺失的依赖:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

