@echo off
chcp 65001 >nul
echo ========================================
echo   超星学习通Web平台 - 后端启动脚本
echo ========================================
echo.

REM 保存当前目录
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%..

REM 检查根目录虚拟环境
echo [1/3] 检查项目虚拟环境...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ 未检测到虚拟环境！
    echo.
    echo 请先运行项目根目录的环境设置脚本：
    echo   双击运行：setup_env.bat
    echo   或手动执行：python -m venv .venv ^&^& pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo ✅ 检测到虚拟环境

echo.
echo [2/3] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败！
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

echo.
echo [3/3] 启动后端服务...
echo.
echo ========================================
echo   服务信息
echo ========================================
echo   API文档: http://localhost:8000/api/docs
echo   健康检查: http://localhost:8000/api/health
echo   管理员账号: admin / Admin@123
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动后端（使用统一入口）
cd web\backend
python run_app.py

pause
