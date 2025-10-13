@echo off
chcp 65001 >nul
REM 超星学习通 - 一键安装脚本（Windows）
REM 自动安装依赖、配置并启动服务

setlocal enabledelayedexpansion

echo ================================================================
echo        超星学习通自动化平台 - 一键安装脚本
echo ================================================================
echo.
echo [*] 开始安装...
echo.

REM 1. 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 未安装Python，请先安装Python 3.10+
    echo     下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [+] Python版本: %PYTHON_VERSION%

REM 2. 检查是否从Release下载
echo.
echo 选择安装方式:
echo   1. 从源码安装（需要Node.js，构建前端）
echo   2. 下载Release版本（推荐，包含预编译前端）
echo.
set /p INSTALL_METHOD="请选择 (1/2): "

if "%INSTALL_METHOD%"=="2" (
    echo.
    echo [*] Release安装方式
    echo [!] 请手动下载Release版本:
    echo     https://github.com/ViVi141/chaoxing/releases/latest
    echo.
    echo     下载 chaoxing-vX.X.X-full.zip
    echo     解压后运行本脚本
    echo.
    pause
)

REM 3. 创建虚拟环境
echo.
echo [*] 创建Python虚拟环境...
python -m venv .venv
if %errorlevel% equ 0 (
    call .venv\Scripts\activate
    echo [+] 虚拟环境已创建
) else (
    echo [!] 虚拟环境创建失败，将全局安装
)

REM 4. 安装Python依赖
echo.
echo [*] 安装Python依赖（这可能需要几分钟）...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo [+] Python依赖安装完成
) else (
    echo [!] 部分依赖安装失败，请检查网络或手动安装
)

REM 5. 检查前端
if not exist "web\frontend\dist" (
    echo.
    echo [!] 未找到前端构建文件
    
    where npm >nul 2>&1
    if %errorlevel% equ 0 (
        echo [*] 检测到npm，开始构建前端...
        cd web\frontend
        call npm install
        call npm run build
        cd ..\..
        echo [+] 前端构建完成
    ) else (
        echo [!] 未安装Node.js，将跳过前端构建
        echo     Web平台需要手动构建或下载Release版本
        echo     命令行模式不受影响
    )
)

REM 6. 生成配置文件
echo.
echo [*] 生成配置文件...

if not exist "config.ini" (
    copy config_template.ini config.ini >nul
    echo [+] 配置文件已创建: config.ini
    echo [!] 请编辑 config.ini 填入你的超星账号和密码
) else (
    echo [!] config.ini 已存在，跳过
)

REM 7. 创建必要目录
if not exist "web\backend\logs" mkdir web\backend\logs
if not exist "web\backend\data" mkdir web\backend\data

REM 8. 选择运行模式
echo.
echo 选择运行模式:
echo   1. 命令行模式（简单，适合个人）
echo   2. Web平台模式（功能完整，适合团队）
echo.
set /p RUN_MODE="请选择 (1/2): "

echo.
if "%RUN_MODE%"=="1" (
    REM 命令行模式
    echo [OK] 安装完成！
    echo.
    echo ================================================================
    echo                   命令行模式使用说明
    echo ================================================================
    echo.
    echo 1. 编辑配置文件:
    echo    notepad config.ini
    echo.
    echo 2. 运行程序:
    echo    .venv\Scripts\activate  ^(如果使用虚拟环境^)
    echo    python main.py -c config.ini
    echo.
    echo 3. 查看帮助:
    echo    python main.py --help
    echo.
) else (
    REM Web平台模式
    echo [OK] 安装完成！
    echo.
    echo ================================================================
    echo                   Web平台模式使用说明
    echo ================================================================
    echo.
    echo 一键启动:
    echo    启动Refine完整版.bat
    echo.
    echo 或使用守护进程:
    echo    daemon_control.bat start
    echo.
    echo 手动启动:
    echo    # 窗口1 - 后端
    echo    cd web\backend
    echo    ..\..\.venv\Scripts\activate  ^(如果使用虚拟环境^)
    echo    python app.py
    echo.
    echo    # 窗口2 - Celery
    echo    cd web\backend
    echo    ..\..\.venv\Scripts\activate  ^(如果使用虚拟环境^)
    echo    celery -A celery_app worker --loglevel=info
    echo.
    echo 访问: http://localhost:8000/api/docs
    echo.
)

echo ================================================================
echo 文档:
echo   - 快速开始: docs\QUICK_START.md
echo   - 守护进程: docs\DAEMON.md
echo   - 完整文档: docs\INDEX.md
echo ================================================================
echo.

echo [OK] 安装完成！祝使用愉快！
echo.
pause

