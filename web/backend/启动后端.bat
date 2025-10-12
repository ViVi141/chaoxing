@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Backend API Server
echo ========================================
echo.

call ..\..\venv\Scripts\activate.bat
python run_app.py

pause

