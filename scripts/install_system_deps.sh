#!/bin/bash
# -*- coding: utf-8 -*-
# 安装系统级依赖（Linux）
# 支持 Ubuntu/Debian/CentOS/RHEL/Fedora

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

# 检测Linux发行版
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
        VERSION=$(cat /etc/redhat-release | sed 's/.*release \([0-9]\+\).*/\1/')
    else
        print_error "无法检测Linux发行版"
        exit 1
    fi
    
    print_step "检测到系统: $DISTRO $VERSION"
}

# 安装Ubuntu/Debian依赖
install_debian_deps() {
    print_step "安装系统依赖（Ubuntu/Debian）..."
    
    sudo apt-get update
    
    # 基础编译工具
    sudo apt-get install -y \
        gcc \
        g++ \
        make \
        python3-dev \
        python3-pip \
        python3-venv \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
        curl \
        wget \
        git
    
    # PostgreSQL开发库（可选，仅在使用PostgreSQL时需要）
    if [ "$1" = "with-postgresql" ]; then
        sudo apt-get install -y \
            libpq-dev \
            postgresql-client
        print_success "已安装PostgreSQL开发库"
    fi
    
    print_success "系统依赖安装完成"
}

# 安装CentOS/RHEL/Fedora依赖
install_rhel_deps() {
    print_step "安装系统依赖（CentOS/RHEL/Fedora）..."
    
    if command -v dnf &> /dev/null; then
        PKG_MGR="dnf"
    elif command -v yum &> /dev/null; then
        PKG_MGR="yum"
    else
        print_error "未找到包管理器（yum/dnf）"
        exit 1
    fi
    
    sudo $PKG_MGR install -y \
        gcc \
        gcc-c++ \
        make \
        python3-devel \
        python3-pip \
        libffi-devel \
        openssl-devel \
        libxml2-devel \
        libxslt-devel \
        libjpeg-turbo-devel \
        libpng-devel \
        zlib-devel \
        curl \
        wget \
        git
    
    # PostgreSQL开发库（可选）
    if [ "$1" = "with-postgresql" ]; then
        sudo $PKG_MGR install -y \
            postgresql-devel \
            postgresql
        print_success "已安装PostgreSQL开发库"
    fi
    
    print_success "系统依赖安装完成"
}

# 主函数
main() {
    print_step "开始安装系统级依赖..."
    
    # 检查是否为root或sudo权限
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        print_warning "需要sudo权限来安装系统依赖"
        print_step "请输入sudo密码:"
        sudo -v
    fi
    
    detect_distro
    
    case $DISTRO in
        ubuntu|debian)
            install_debian_deps "$@"
            ;;
        rhel|centos|fedora|rocky|almalinux)
            install_rhel_deps "$@"
            ;;
        *)
            print_error "不支持的Linux发行版: $DISTRO"
            print_warning "请手动安装以下依赖:"
            echo "  - gcc, g++, make"
            echo "  - python3-dev / python3-devel"
            echo "  - libffi-dev / libffi-devel"
            echo "  - libssl-dev / openssl-devel"
            echo "  - libxml2-dev / libxml2-devel"
            echo "  - libxslt1-dev / libxslt-devel"
            echo "  - libjpeg-dev / libjpeg-turbo-devel"
            echo "  - libpng-dev / libpng-devel"
            echo "  - zlib1g-dev / zlib-devel"
            exit 1
            ;;
    esac
    
    print_success "所有系统依赖已安装完成！"
    echo ""
    print_step "下一步: 运行 pip install -r requirements.txt"
}

main "$@"

