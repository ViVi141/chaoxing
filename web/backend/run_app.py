#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web Backend启动入口
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

# 现在导入app（会从当前目录导入）
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


