@echo off
chcp 65001 >nul
REM Chaoxing Windows守护进程控制脚本
REM 使用Windows服务或NSSM管理

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%web\backend"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_DIR=%BACKEND_DIR%\logs"

REM 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:main
if "%1"=="" goto show_help
if /i "%1"=="start" goto start_service
if /i "%1"=="stop" goto stop_service
if /i "%1"=="status" goto show_status
if /i "%1"=="install-nssm" goto install_nssm
if /i "%1"=="help" goto show_help
if /i "%1"=="-h" goto show_help
if /i "%1"=="--help" goto show_help

echo [错误] 未知命令: %1
goto show_help

:show_help
echo.
echo Chaoxing Windows守护进程控制脚本
echo.
echo 用法: %~nx0 ^<命令^>
echo.
echo 命令:
echo     start              启动服务（后台运行）
echo     stop               停止服务
echo     status             查看服务状态
echo     install-nssm       安装NSSM Windows服务
echo     help               显示帮助
echo.
echo Windows推荐方式:
echo   1. 使用NSSM（推荐） - 完整的Windows服务
echo   2. 使用启动脚本    - 简单的后台运行
echo   3. 使用计划任务    - 开机自启动
echo.
echo 示例:
echo     %~nx0 start              # 启动服务
echo     %~nx0 stop               # 停止服务
echo     %~nx0 status             # 查看状态
echo     %~nx0 install-nssm       # 安装Windows服务
echo.
goto :eof

:start_service
echo [*] 启动服务...
cd /d "%BACKEND_DIR%"

REM 检查是否已在运行
tasklist /FI "WINDOWTITLE eq Chaoxing Backend*" 2>nul | find /i "cmd.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [!] 后端服务可能已在运行
) else (
    echo [+] 启动后端服务...
    start "Chaoxing Backend" /B cmd /c ""%VENV_DIR%\Scripts\activate" && python app.py > "%LOG_DIR%\backend.log" 2>&1"
)

tasklist /FI "WINDOWTITLE eq Chaoxing Celery*" 2>nul | find /i "cmd.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [!] Celery服务可能已在运行
) else (
    echo [+] 启动Celery服务...
    start "Chaoxing Celery" /B cmd /c ""%VENV_DIR%\Scripts\activate" && celery -A celery_app worker --loglevel=info > "%LOG_DIR%\celery.log" 2>&1"
)

echo.
echo [OK] 服务已启动
echo.
echo 日志位置:
echo   后端: %LOG_DIR%\backend.log
echo   Celery: %LOG_DIR%\celery.log
echo.
echo 查看状态: %~nx0 status
goto :eof

:stop_service
echo [*] 停止服务...

REM 停止后端
for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Chaoxing Backend*" /NH 2^>nul ^| find /i "cmd.exe"') do (
    echo [+] 停止后端服务 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM 停止Celery
for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Chaoxing Celery*" /NH 2^>nul ^| find /i "cmd.exe"') do (
    echo [+] 停止Celery服务 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM 确保进程被停止
taskkill /F /FI "WINDOWTITLE eq *app.py*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *celery*worker*" >nul 2>&1

echo [OK] 服务已停止
goto :eof

:show_status
echo [*] 服务状态:
echo.

tasklist /FI "WINDOWTITLE eq Chaoxing Backend*" 2>nul | find /i "cmd.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [+] 后端服务: 运行中
    tasklist /FI "WINDOWTITLE eq Chaoxing Backend*" /NH
) else (
    echo [-] 后端服务: 未运行
)

echo.

tasklist /FI "WINDOWTITLE eq Chaoxing Celery*" 2>nul | find /i "cmd.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Celery服务: 运行中
    tasklist /FI "WINDOWTITLE eq Chaoxing Celery*" /NH
) else (
    echo [-] Celery服务: 未运行
)

echo.
goto :eof

:install_nssm
echo [*] 安装NSSM Windows服务
echo.
echo NSSM (Non-Sucking Service Manager) 可以将任何程序作为Windows服务运行
echo.
echo 安装步骤:
echo   1. 下载NSSM: https://nssm.cc/download
echo   2. 解压到系统PATH或项目目录
echo   3. 运行以下命令:
echo.
echo      # 安装后端服务
echo      nssm install chaoxing-backend "%VENV_DIR%\Scripts\python.exe" "app.py"
echo      nssm set chaoxing-backend AppDirectory "%BACKEND_DIR%"
echo      nssm set chaoxing-backend DisplayName "Chaoxing Backend Service"
echo      nssm set chaoxing-backend Description "超星学习通后端服务"
echo      nssm set chaoxing-backend Start SERVICE_AUTO_START
echo      nssm set chaoxing-backend AppStdout "%LOG_DIR%\nssm_backend_stdout.log"
echo      nssm set chaoxing-backend AppStderr "%LOG_DIR%\nssm_backend_stderr.log"
echo.
echo      # 安装Celery服务
echo      nssm install chaoxing-celery "%VENV_DIR%\Scripts\celery.exe" "-A celery_app worker --loglevel=info"
echo      nssm set chaoxing-celery AppDirectory "%BACKEND_DIR%"
echo      nssm set chaoxing-celery DisplayName "Chaoxing Celery Worker"
echo      nssm set chaoxing-celery Description "超星学习通任务队列"
echo      nssm set chaoxing-celery Start SERVICE_AUTO_START
echo      nssm set chaoxing-celery AppStdout "%LOG_DIR%\nssm_celery_stdout.log"
echo      nssm set chaoxing-celery AppStderr "%LOG_DIR%\nssm_celery_stderr.log"
echo.
echo   4. 启动服务:
echo      nssm start chaoxing-backend
echo      nssm start chaoxing-celery
echo.
echo   5. 管理服务:
echo      services.msc  # 打开Windows服务管理器
echo.
echo   6. 卸载服务（如需要）:
echo      nssm stop chaoxing-backend
echo      nssm remove chaoxing-backend confirm
echo      nssm stop chaoxing-celery
echo      nssm remove chaoxing-celery confirm
echo.
goto :eof

endlocal

