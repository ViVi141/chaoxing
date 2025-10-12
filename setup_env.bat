@echo off
REM 超星学习通自动化 - 环境设置脚本 (Windows)
REM 使用方法：双击运行此文件

echo ====================================
echo 超星学习通自动化 - 环境设置
echo ====================================
echo.

echo [1/4] 检查虚拟环境...
if exist ".venv\Scripts\python.exe" (
    echo ✅ 检测到已有虚拟环境，将使用现有环境
) else (
    echo 未检测到虚拟环境，正在创建...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败！请检查Python是否已安装。
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

echo.
echo [2/4] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败！
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

echo.
echo [3/4] 升级pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip已升级

echo.
echo [4/4] 安装项目依赖（可能需要几分钟）...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ====================================
echo ✅ 环境设置完成！
echo ====================================
echo.
echo 使用方法：
echo.
echo 【命令行版】
echo   python main.py -c config.ini
echo.
echo 【Web平台】
echo   1. 启动后端：  web\start_backend.bat
echo   2. 启动Celery：web\start_celery.bat
echo   3. 启动前端：  cd web\frontend ^&^& start.bat
echo.
echo 【Docker部署】
echo   cd web ^&^& docker-compose -f docker-compose.simple.yml up -d
echo.
echo ====================================
echo.

pause

