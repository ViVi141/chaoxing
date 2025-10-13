@echo off
chcp 65001 >nul
REM 快速启动脚本 - 零配置部署

echo =========================================
echo   超星学习通自动化工具 - 快速启动
echo =========================================
echo.

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装！请先安装Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker已安装

REM 检查docker compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose未安装！请升级Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker Compose已安装
echo.

REM 停止并删除旧容器
echo 🧹 清理旧容器...
docker compose -f docker-compose.simple.yml down -v 2>nul

REM 创建数据目录
echo 📁 创建数据目录...
if not exist "backend\data" mkdir backend\data
if not exist "backend\logs" mkdir backend\logs

REM 拉取最新镜像
echo 📥 拉取最新Docker镜像...
docker compose -f docker-compose.simple.yml pull

REM 启动容器
echo 🚀 启动容器...
docker compose -f docker-compose.simple.yml up -d --force-recreate

REM 等待容器启动
echo ⏳ 等待服务启动（30秒）...
timeout /t 30 /nobreak >nul

REM 检查容器状态
echo.
echo 📊 容器状态：
docker compose -f docker-compose.simple.yml ps

REM 检查后端日志
echo.
echo 📋 后端日志（最后20行）：
docker logs chaoxing_backend --tail 20

REM 检查健康状态
echo.
echo 🔍 服务健康检查...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  后端服务可能还在启动中，请稍等片刻
) else (
    echo ✅ 后端服务运行正常
)

echo.
echo =========================================
echo   🎉 启动完成！
echo =========================================
echo.
echo 访问地址：http://localhost:8000
echo.
echo 查看日志：
echo   docker logs chaoxing_backend -f
echo   docker logs chaoxing_celery_lite -f
echo.
echo 停止服务：
echo   docker compose -f docker-compose.simple.yml down
echo.
pause

