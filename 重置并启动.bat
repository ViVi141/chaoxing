@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Reset Database and Start Services
echo ========================================
echo.

:: 确认删除
echo [WARNING] This will delete all data!
echo.
set /p confirm="Are you sure? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo.
    echo [INFO] Cancelled by user
    pause
    exit /b 0
)

echo.
echo [INFO] Deleting database and cache...

:: 删除数据库
if exist "web\backend\data\chaoxing.db" (
    del /f /q "web\backend\data\chaoxing.db"
    echo [OK] Database deleted
)

:: 删除Celery缓存
if exist "web\backend\data\celery_results" (
    rmdir /s /q "web\backend\data\celery_results"
    echo [OK] Celery results deleted
)

if exist "web\backend\data\celery_broker" (
    rmdir /s /q "web\backend\data\celery_broker"
    echo [OK] Celery broker deleted
)

:: 删除Python缓存
if exist "web\backend\__pycache__" (
    rmdir /s /q "web\backend\__pycache__"
)

if exist "web\backend\routes\__pycache__" (
    rmdir /s /q "web\backend\routes\__pycache__"
)

echo [OK] All cache cleared
echo.

:: 创建data目录
if not exist "web\backend\data" (
    mkdir "web\backend\data"
)

echo [INFO] Starting services...
echo.

:: 启动服务
call "启动Refine完整版.bat"

