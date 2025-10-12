#!/bin/bash
# 超星学习通Web平台 - 一键启动所有服务 (Linux/Mac)

echo "========================================"
echo "  超星学习通Web平台 - 一键启动"
echo "========================================"
echo ""

# 检查虚拟环境
echo "[检查] 虚拟环境状态..."
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ 未检测到虚拟环境！"
    echo ""
    echo "正在运行环境设置脚本..."
    chmod +x setup_env.sh
    ./setup_env.sh
    if [ $? -ne 0 ]; then
        echo "❌ 环境设置失败！"
        exit 1
    fi
fi
echo "✅ 虚拟环境就绪"

echo ""
echo "========================================"
echo "  正在启动所有服务..."
echo "========================================"
echo ""

# 激活虚拟环境
source .venv/bin/activate

echo "[1/3] 启动后端服务（后台运行）..."
cd web/backend
nohup python run_app.py > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "  后端PID: $BACKEND_PID"
cd ../..
sleep 2

echo "[2/3] 启动Celery Worker（后台运行）..."
cd web/backend
nohup python run_celery.py > ../../logs/celery.log 2>&1 &
CELERY_PID=$!
echo "  Celery PID: $CELERY_PID"
cd ../..
sleep 2

echo "[3/3] 启动前端服务（后台运行）..."
cd web/frontend
nohup npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  前端PID: $FRONTEND_PID"
cd ../..

echo ""
echo "========================================"
echo "  所有服务已启动！"
echo "========================================"
echo ""
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/api/docs"
echo "  前端界面: http://localhost:5173"
echo ""
echo "  默认管理员账号: admin / Admin@123"
echo ""
echo "  后端PID: $BACKEND_PID"
echo "  Celery PID: $CELERY_PID"
echo "  前端PID: $FRONTEND_PID"
echo ""
echo "========================================"
echo ""
echo "停止服务："
echo "  kill $BACKEND_PID $CELERY_PID $FRONTEND_PID"
echo ""
echo "查看日志："
echo "  后端: tail -f logs/backend.log"
echo "  Celery: tail -f logs/celery.log"
echo "  前端: tail -f logs/frontend.log"
echo ""

