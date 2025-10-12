#!/bin/bash
# 超星学习通自动化 - 环境设置脚本 (Linux/Mac)
# 使用方法：chmod +x setup_env.sh && ./setup_env.sh

echo "===================================="
echo "超星学习通自动化 - 环境设置"
echo "===================================="
echo ""

echo "[1/4] 检查虚拟环境..."
if [ -f ".venv/bin/python" ]; then
    echo "✅ 检测到已有虚拟环境，将使用现有环境"
else
    echo "未检测到虚拟环境，正在创建..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败！请检查Python是否已安装。"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

echo ""
echo "[2/4] 激活虚拟环境..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 激活虚拟环境失败！"
    exit 1
fi
echo "✅ 虚拟环境已激活"

echo ""
echo "[3/4] 升级pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip已升级"

echo ""
echo "[4/4] 安装项目依赖（可能需要几分钟）..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败！"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ 环境设置完成！"
echo "===================================="
echo ""
echo "使用方法："
echo ""
echo "【命令行版】"
echo "  python main.py -c config.ini"
echo ""
echo "【Web平台】"
echo "  1. 启动后端：  cd web/backend && python app.py"
echo "  2. 启动Celery：cd web/backend && celery -A celery_app worker --loglevel=info"
echo "  3. 启动前端：  cd web/frontend && npm run dev"
echo ""
echo "【Docker部署】"
echo "  cd web && docker-compose -f docker-compose.simple.yml up -d"
echo ""
echo "===================================="
echo ""

