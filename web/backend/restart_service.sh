#!/bin/bash
########################################
# 超星学习通 - 服务重启脚本（Linux/Mac）
# 用于数据库迁移后重启服务
########################################

set -e

echo "========================================"
echo "超星学习通服务重启脚本"
echo "========================================"
echo ""

# 检测是否使用Docker
if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
    echo "检测到Docker Compose环境"
    echo ""
    echo "[1/2] 停止服务..."
    docker-compose stop backend celery
    
    echo "[2/2] 启动服务..."
    docker-compose up -d backend celery
    
    echo ""
    echo "✅ Docker服务重启完成！"
    docker-compose ps
    exit 0
fi

# 检测是否使用systemd
if command -v systemctl &> /dev/null; then
    if systemctl list-units --type=service | grep -q "chaoxing"; then
        echo "检测到systemd服务"
        echo ""
        echo "[1/2] 重启后端服务..."
        sudo systemctl restart chaoxing-backend
        
        echo "[2/2] 重启Celery服务..."
        sudo systemctl restart chaoxing-celery
        
        echo ""
        echo "✅ systemd服务重启完成！"
        sudo systemctl status chaoxing-backend chaoxing-celery
        exit 0
    fi
fi

# 检测是否使用supervisor
if command -v supervisorctl &> /dev/null; then
    if sudo supervisorctl status | grep -q "chaoxing"; then
        echo "检测到Supervisor服务"
        echo ""
        echo "[1/2] 重启后端服务..."
        sudo supervisorctl restart chaoxing-backend
        
        echo "[2/2] 重启Celery服务..."
        sudo supervisorctl restart chaoxing-celery
        
        echo ""
        echo "✅ Supervisor服务重启完成！"
        sudo supervisorctl status
        exit 0
    fi
fi

# 手动重启
echo "使用手动重启模式"
echo ""

echo "[1/4] 查找并停止Celery进程..."
pkill -f "celery -A celery_app" || echo "未找到Celery进程"
sleep 2

echo "[2/4] 查找并停止后端进程..."
pkill -f "python app.py" || echo "未找到后端进程"
sleep 2

echo "[3/4] 启动后端服务..."
nohup python app.py > logs/app.log 2>&1 &
echo "后端服务已启动 (PID: $!)"
sleep 3

echo "[4/4] 启动Celery Worker..."
nohup celery -A celery_app worker --loglevel=info > logs/celery.log 2>&1 &
echo "Celery Worker已启动 (PID: $!)"
sleep 2

echo ""
echo "========================================"
echo "✅ 服务重启完成！"
echo ""
echo "后端服务: http://localhost:8000"
echo "API文档: http://localhost:8000/api/docs"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/app.log"
echo "  Celery: tail -f logs/celery.log"
echo "========================================"
echo ""

