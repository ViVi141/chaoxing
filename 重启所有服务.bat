@echo off
chcp 65001 >nul
echo ================================
echo 重启所有服务
echo ================================
echo.

cd /d "%~dp0"

echo [1/3] 检查虚拟环境...
if not exist ".venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，请先运行 setup_env.bat
    pause
    exit /b 1
)

echo 虚拟环境存在
echo.

echo [2/3] 安装新依赖...
call .venv\Scripts\activate.bat
pip install -q psycopg2-binary==2.9.9 2>nul
echo 依赖已更新
echo.

echo [3/3] 启动所有服务...
echo.

echo 正在启动后端...
start "超星后端" cmd /k "cd /d %~dp0web\backend & ..\..\.venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

echo.
echo 正在启动Celery...
start "超星Celery" cmd /k "cd /d %~dp0web\backend & ..\..\.venv\Scripts\python.exe -m celery -A celery_app worker --loglevel=info -P solo"
timeout /t 3 /nobreak >nul

echo.
echo 正在启动前端...
cd web\frontend
start "超星前端" cmd /k "npm run dev"

echo.
echo ================================
echo 所有服务已启动！
echo ================================
echo.
echo 访问地址:
echo   前端: http://localhost:5173
echo   后端: http://localhost:8000
echo.
echo 默认管理员账号:
echo   用户名: admin
echo   密码: Admin@123
echo.
echo 按任意键关闭此窗口...
pause >nul
