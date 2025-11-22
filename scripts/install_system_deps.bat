@echo off
chcp 65001 >nul
REM 安装系统级依赖（Windows）
REM Windows通常不需要额外安装系统依赖，但需要确保Python已正确安装

echo ================================================================
echo        安装系统级依赖（Windows）
echo ================================================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 未安装Python，请先安装Python 3.12+
    echo     下载地址: https://www.python.org/downloads/
    echo     安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [+] Python版本: %PYTHON_VERSION%

REM 检查pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] pip未安装，正在尝试安装...
    python -m ensurepip --upgrade
)

echo.
echo [+] Windows系统依赖检查完成
echo.
echo 注意: Windows通常不需要额外安装系统依赖
echo 如果遇到编译错误，请确保:
echo   1. 已安装 Visual C++ Build Tools
echo   2. 已安装 Windows SDK
echo   3. 使用预编译的wheel包（推荐）
echo.
echo 下载地址:
echo   Visual C++ Build Tools: https://visualstudio.microsoft.com/downloads/
echo.
pause

