@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   超星学习通 - Refine完整版启动
echo ==========================================
echo.
echo 版本: 2.0.0-refine
echo 技术栈: React + Refine + Ant Design
echo.
echo ==========================================

REM 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_env.bat first
    pause
    exit /b 1
)

echo [Step 1/4] Stopping old services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul
echo   Done
echo.

echo [Step 2/4] Starting Backend API...
start "Backend-API" cmd /k ".venv\Scripts\activate.bat & cd web\backend & python run_app.py"
timeout /t 3 >nul
echo   Done
echo.

echo [Step 3/4] Starting Celery Worker...
start "Celery-Worker" cmd /k ".venv\Scripts\activate.bat & cd web\backend & python run_celery.py"
timeout /t 3 >nul
echo   Done
echo.

echo [Step 4/4] Checking frontend dependencies...
cd web\frontend

if not exist "node_modules\" (
    echo.
    echo [INFO] First time setup - Installing dependencies...
    echo This will take about 5-10 minutes, please wait...
    echo.
    call npm install
    
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
)

echo.
echo [Step 4/4] Starting Refine Frontend...
echo.
start "Refine-Frontend" cmd /k "npm run dev"

cd ..\..

echo.
echo ==========================================
echo   All Services Started Successfully!
echo ==========================================
echo.
echo Services:
echo   - Backend API:  http://localhost:8000
echo   - API Docs:     http://localhost:8000/api/docs
echo   - Frontend:     http://localhost:5173
echo.
echo Default Login:
echo   - Username: admin
echo   - Password: Admin@123
echo.
echo Tips:
echo   - Wait 10-30 seconds for all services to start
echo   - Frontend will open automatically in your browser
echo   - Close windows to stop services
echo.
echo ==========================================
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo Browser opened! Services are running in separate windows.
echo.
pause

