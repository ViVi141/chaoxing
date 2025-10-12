@echo off
REM 超星学习通Web平台 - 一键启动所有服务 (Windows)
chcp 65001 >nul

echo ========================================
echo   超星学习通Web平台 - 一键启动
echo ========================================
echo.

REM 检查虚拟环境
echo [检查] 虚拟环境状态...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ 未检测到虚拟环境！
    echo.
    echo 正在运行环境设置脚本...
    call setup_env.bat
    if errorlevel 1 (
        echo ❌ 环境设置失败！
        pause
        exit /b 1
    )
)
echo ✅ 虚拟环境就绪

echo.
echo ========================================
echo   正在启动所有服务...
echo ========================================
echo.

echo [1/3] 启动后端服务...
start "超星-后端服务" cmd /k "call .venv\Scripts\activate.bat && cd web\backend && python run_app.py"
timeout /t 3 >nul

echo [2/3] 启动Celery Worker...
start "超星-Celery Worker" cmd /k "call .venv\Scripts\activate.bat && cd web\backend && python run_celery.py"
timeout /t 3 >nul

echo [3/3] 启动前端服务...
start "超星-前端服务" cmd /k "cd web\frontend && npm run dev"

echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo.
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/api/docs
echo   前端界面: http://localhost:5173
echo.
echo   默认管理员账号: admin / Admin@123
echo.
echo ========================================
echo.
echo 提示：关闭所有窗口即可停止服务
echo.

pause

