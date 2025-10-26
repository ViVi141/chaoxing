#!/usr/bin/env python3
"""
简化的启动脚本，用于绕过导入问题
"""
import os
import sys
import subprocess

# 设置环境变量
os.environ.setdefault('PYTHONPATH', '/app')

# 切换到正确的工作目录
os.chdir('/app/web/backend')

# 启动应用
if __name__ == "__main__":
    try:
        # 直接启动uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app:app', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ], check=True)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)
