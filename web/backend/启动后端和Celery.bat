@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================
echo 启动后端和Celery
echo ================================
echo.

echo 正在启动后端...
start "超星后端" cmd /k "..\..\.venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

echo 正在启动Celery...
start "超星Celery" cmd /k "..\..\.venv\Scripts\python.exe -m celery -A celery_app worker --loglevel=info -P solo"

echo.
echo 已启动后端和Celery
echo 按任意键关闭此窗口...
pause >nul

