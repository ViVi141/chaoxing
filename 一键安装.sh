#!/bin/bash
# -*- coding: utf-8 -*-
# 超星学习通 - 一键安装脚本（Linux/macOS）
# 自动下载、安装依赖、配置并启动服务

set -e

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 欢迎信息
clear
cat << "EOF"
================================================================
       超星学习通自动化平台 - 一键安装脚本
================================================================
EOF

echo ""
print_step "开始安装..."
echo ""

# 1. 检查系统要求
print_step "检查系统要求..."

if ! command_exists python3; then
    print_error "未安装Python 3，请先安装Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python版本: $PYTHON_VERSION"

if ! command_exists git; then
    print_warning "未安装Git，将使用wget/curl下载"
fi

# 2. 选择安装方式
echo ""
print_step "选择安装方式:"
echo "  1. 从源码安装（需要npm，构建前端）"
echo "  2. 下载Release版本（推荐，包含预编译前端）"
echo ""
read -p "请选择 (1/2): " INSTALL_METHOD

if [ "$INSTALL_METHOD" = "2" ]; then
    # Release安装
    print_step "下载最新Release版本..."
    
    # 获取最新版本号
    LATEST_VERSION=$(curl -s https://api.github.com/repos/ViVi141/chaoxing/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    
    if [ -z "$LATEST_VERSION" ]; then
        print_warning "无法获取最新版本，使用v2.3.0"
        LATEST_VERSION="v2.3.0"
    fi
    
    print_success "最新版本: $LATEST_VERSION"
    
    # 下载完整包
    DOWNLOAD_URL="https://github.com/ViVi141/chaoxing/releases/download/${LATEST_VERSION}/chaoxing-${LATEST_VERSION}-full.tar.gz"
    
    print_step "下载中: $DOWNLOAD_URL"
    
    if command_exists wget; then
        wget -O chaoxing-full.tar.gz "$DOWNLOAD_URL"
    elif command_exists curl; then
        curl -L -o chaoxing-full.tar.gz "$DOWNLOAD_URL"
    else
        print_error "未安装wget或curl"
        exit 1
    fi
    
    # 解压
    print_step "解压文件..."
    tar -xzf chaoxing-full.tar.gz
    cd release-package
    
    print_success "Release版本下载完成（已包含前端构建）"
    
else
    # 源码安装
    print_step "克隆源码..."
    
    if command_exists git; then
        git clone https://github.com/ViVi141/chaoxing.git
        cd chaoxing
    else
        print_error "Git未安装，无法克隆源码"
        exit 1
    fi
    
    # 构建前端
    if command_exists npm; then
        print_step "构建前端..."
        cd web/frontend
        npm install
        npm run build
        cd ../..
        print_success "前端构建完成"
    else
        print_warning "未安装npm，将跳过前端构建"
        print_warning "Web平台需要手动构建前端或下载Release版本"
    fi
fi

# 3. 创建虚拟环境
print_step "创建Python虚拟环境..."

if ! python3 -m venv .venv; then
    print_warning "虚拟环境创建失败，将全局安装"
    USE_VENV=false
else
    USE_VENV=true
    source .venv/bin/activate
    print_success "虚拟环境已创建"
fi

# 4. 安装Python依赖
print_step "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Python依赖安装完成"

# 5. 生成配置文件
print_step "生成配置文件..."

if [ ! -f "config.ini" ]; then
    cp config_template.ini config.ini
    print_success "配置文件已创建: config.ini"
    print_warning "请编辑 config.ini 填入你的超星账号和密码"
else
    print_warning "config.ini 已存在，跳过"
fi

# 6. 创建日志目录
mkdir -p web/backend/logs
mkdir -p web/backend/data

# 7. 选择运行模式
echo ""
print_step "选择运行模式:"
echo "  1. 命令行模式（简单，适合个人）"
echo "  2. Web平台模式（功能完整，适合团队）"
echo ""
read -p "请选择 (1/2): " RUN_MODE

echo ""
if [ "$RUN_MODE" = "1" ]; then
    # 命令行模式
    print_success "安装完成！"
    echo ""
    echo "================================================================"
    echo "                    命令行模式使用说明"
    echo "================================================================"
    echo ""
    echo "1. 编辑配置文件:"
    echo "   nano config.ini"
    echo ""
    echo "2. 运行程序:"
    if [ "$USE_VENV" = true ]; then
        echo "   source .venv/bin/activate"
    fi
    echo "   python main.py -c config.ini"
    echo ""
    echo "3. 查看帮助:"
    echo "   python main.py --help"
    echo ""
else
    # Web平台模式
    print_success "安装完成！"
    echo ""
    echo "================================================================"
    echo "                    Web平台模式使用说明"
    echo "================================================================"
    echo ""
    echo "快速启动（推荐）:"
    echo "   chmod +x daemon_control.sh"
    echo "   ./daemon_control.sh start"
    echo ""
    echo "手动启动:"
    echo "   # 终端1 - 后端"
    echo "   cd web/backend"
    if [ "$USE_VENV" = true ]; then
        echo "   source ../../.venv/bin/activate"
    fi
    echo "   python app.py"
    echo ""
    echo "   # 终端2 - Celery"
    echo "   cd web/backend"
    if [ "$USE_VENV" = true ]; then
        echo "   source ../../.venv/bin/activate"
    fi
    echo "   celery -A celery_app worker --loglevel=info"
    echo ""
    echo "访问: http://localhost:8000/api/docs"
    echo ""
    echo "生产环境部署:"
    echo "   查看文档: docs/DAEMON.md"
    echo ""
fi

echo "================================================================"
echo "文档:"
echo "  - 快速开始: docs/QUICK_START.md"
echo "  - 守护进程: docs/DAEMON.md"
echo "  - 完整文档: docs/INDEX.md"
echo "================================================================"
echo ""

print_success "安装完成！祝使用愉快！"

