#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web Backend启动入口
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

# 现在导入app
from app import app
from config import settings

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

