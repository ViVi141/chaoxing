@echo off
REM ========================================
REM 超星学习通 - 服务重启脚本（Windows）
REM 用于数据库迁移后重启服务
REM ========================================

echo ========================================
echo 超星学习通服务重启脚本
echo ========================================
echo.

echo [1/4] 停止Celery Worker...
taskkill /F /IM celery.exe >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *celery*" >nul 2>&1
timeout /t 2 >nul

echo [2/4] 停止后端服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" >nul 2>&1
timeout /t 2 >nul

echo [3/4] 启动后端服务...
start "超星学习通-后端" python app.py
timeout /t 3 >nul

echo [4/4] 启动Celery Worker...
start "超星学习通-Celery" celery -A celery_app worker --loglevel=info --pool=solo
timeout /t 2 >nul

echo.
echo ========================================
echo ✅ 服务重启完成！
echo.
echo 后端服务: http://localhost:8000
echo API文档: http://localhost:8000/api/docs
echo.
echo 请检查两个终端窗口确认服务启动成功
echo ========================================
echo.

pause

