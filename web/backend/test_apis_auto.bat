@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   API Test Runner
echo ========================================
echo.

:: Check if backend is running
echo Checking if backend is running...
curl -s http://localhost:8000/api/health >nul 2>&1

if %errorlevel% == 0 (
    echo [OK] Backend is already running
    echo.
    echo Running API tests...
    echo.
    C:\Users\ViVi141\Desktop\chaoxing\.venv\Scripts\python.exe test_all_apis.py
) else (
    echo [INFO] Backend is not running
    echo Starting backend service...
    echo.
    
    :: Start backend in background
    start "Chaoxing Backend" /MIN cmd /c "cd /d %~dp0 && C:\Users\ViVi141\Desktop\chaoxing\.venv\Scripts\python.exe run_app.py"
    
    :: Wait for backend to start
    echo Waiting for backend to start (10 seconds)...
    timeout /t 10 /nobreak >nul
    
    :: Check again
    curl -s http://localhost:8000/api/health >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Backend started successfully
        echo.
        echo Running API tests...
        echo.
        C:\Users\ViVi141\Desktop\chaoxing\.venv\Scripts\python.exe test_all_apis.py
    ) else (
        echo [ERROR] Failed to start backend
        echo Please start backend manually: python run_app.py
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Test Complete
echo ========================================
pause

