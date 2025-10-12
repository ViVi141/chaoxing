@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Refine Frontend - Setup and Start
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [1/2] Installing dependencies...
    echo This may take 5-10 minutes, please wait...
    echo.
    call npm install
    
    if errorlevel 1 (
        echo.
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
    
    echo.
    echo Dependencies installed successfully!
    echo.
) else (
    echo [INFO] Dependencies already installed
    echo.
)

echo [2/2] Starting development server...
echo.
echo Open browser: http://localhost:5173
echo Login: admin / Admin@123
echo.

npm run dev

