#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Celery Worker启动入口
确保正确的路径设置
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 切换工作目录到web/backend
import os
os.chdir(Path(__file__).parent)

# 设置环境变量，让celery知道app的位置
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

