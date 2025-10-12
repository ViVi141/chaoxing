@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Celery Worker
echo ========================================
echo.

call ..\..\venv\Scripts\activate.bat
python run_celery.py

pause

