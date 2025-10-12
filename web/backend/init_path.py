# -*- coding: utf-8 -*-
"""
统一的路径初始化模块
在其他模块中导入此模块即可自动配置路径
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径（只执行一次）
ROOT_PATH = Path(__file__).parent.parent.parent
ROOT_PATH_STR = str(ROOT_PATH)

if ROOT_PATH_STR not in sys.path:
    sys.path.insert(0, ROOT_PATH_STR)
    print(f"已添加项目根目录到路径: {ROOT_PATH_STR}")

