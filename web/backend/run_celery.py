#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Celery Worker启动入口
确保正确的路径设置
"""
import sys
import os
from pathlib import Path

# 切换工作目录到web/backend（必须在导入前）
BACKEND_DIR = Path(__file__).parent
os.chdir(BACKEND_DIR)

# 添加项目根目录到Python路径（在工作目录之后）
ROOT_DIR = BACKEND_DIR.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# 设置环境变量
os.environ.setdefault('PYTHONPATH', str(ROOT_DIR))

if __name__ == "__main__":
    from celery_app import app
    import platform
    
    # 根据操作系统选择池模式
    pool_mode = 'solo' if platform.system() == 'Windows' else 'prefork'
    
    # 启动worker
    app.worker_main([
        'worker',
        '--loglevel=info',
        f'--pool={pool_mode}',
        '--concurrency=2'  # 并发数
    ])

