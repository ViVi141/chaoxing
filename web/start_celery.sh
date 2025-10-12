#!/bin/bash
# 超星学习通Web平台 - Celery Worker启动脚本

echo "========================================"
echo "  超星学习通Web平台 - Celery Worker"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# 检查根目录虚拟环境
echo "[1/3] 检查项目虚拟环境..."
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ 未检测到虚拟环境！"
    echo ""
    echo "请先运行项目根目录的环境设置脚本："
    echo "  chmod +x setup_env.sh && ./setup_env.sh"
    echo "  或手动执行：python3 -m venv .venv && pip install -r requirements.txt"
    echo ""
    exit 1
fi
echo "✅ 检测到虚拟环境"

echo ""
echo "[2/3] 激活虚拟环境..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 激活虚拟环境失败！"
    exit 1
fi
echo "✅ 虚拟环境已激活"

echo ""
echo "[3/3] 启动Celery Worker..."
echo ""
echo "按 Ctrl+C 停止Worker"
echo ""

# 启动Celery（使用统一入口）
cd web/backend
python run_celery.py

