#!/bin/bash
# -*- coding: utf-8 -*-
# Chaoxing 守护进程控制脚本
# 支持多种方式：systemd, supervisor, screen, nohup

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="chaoxing"
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/web/backend"
FRONTEND_DIR="${PROJECT_ROOT}/web/frontend"
VENV_DIR="${PROJECT_ROOT}/.venv"
LOG_DIR="${BACKEND_DIR}/logs"

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 打印带颜色的消息
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

print_success() {
    print_msg "$GREEN" "✓ $@"
}

print_error() {
    print_msg "$RED" "✗ $@"
}

print_warning() {
    print_msg "$YELLOW" "⚠ $@"
}

print_info() {
    print_msg "$BLUE" "ℹ $@"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查进程是否运行
is_process_running() {
    local name=$1
    pgrep -f "$name" >/dev/null 2>&1
}

# 显示帮助信息
show_help() {
    cat << EOF
Chaoxing 守护进程控制脚本

用法: $0 <命令> [选项]

命令:
    start [method]      启动服务（可选方法：systemd, supervisor, screen, nohup）
    stop [method]       停止服务
    restart [method]    重启服务
    status             查看服务状态
    logs [service]     查看日志（backend/celery/frontend）
    install-systemd    安装systemd服务
    install-supervisor 安装supervisor配置

方法:
    systemd            使用systemd管理（推荐Linux）
    supervisor         使用supervisor管理（通用）
    screen            使用screen会话（简单）
    nohup             使用nohup后台运行（最简单）

示例:
    $0 start systemd              # 使用systemd启动
    $0 start screen               # 使用screen启动
    $0 stop                       # 停止所有服务
    $0 status                     # 查看服务状态
    $0 logs backend               # 查看后端日志
    $0 install-systemd            # 安装systemd服务

EOF
}

# ============ systemd方式 ============
start_systemd() {
    print_info "使用systemd启动服务..."
    
    if ! command_exists systemctl; then
        print_error "systemctl未安装，请使用其他方式"
        return 1
    fi
    
    sudo systemctl start chaoxing-backend.service
    sudo systemctl start chaoxing-celery.service
    
    print_success "systemd服务已启动"
    sudo systemctl status chaoxing-backend.service --no-pager
    sudo systemctl status chaoxing-celery.service --no-pager
}

stop_systemd() {
    print_info "停止systemd服务..."
    sudo systemctl stop chaoxing-backend.service
    sudo systemctl stop chaoxing-celery.service
    print_success "systemd服务已停止"
}

install_systemd() {
    print_info "安装systemd服务..."
    
    if [ ! -f "/etc/systemd/system/chaoxing-backend.service" ]; then
        sudo cp "${BACKEND_DIR}/chaoxing-backend.service" /etc/systemd/system/
        print_success "已安装chaoxing-backend.service"
    fi
    
    if [ ! -f "/etc/systemd/system/chaoxing-celery.service" ]; then
        sudo cp "${BACKEND_DIR}/chaoxing-celery.service" /etc/systemd/system/
        print_success "已安装chaoxing-celery.service"
    fi
    
    # 修改服务文件中的路径
    print_warning "请编辑以下文件，修改项目路径和用户："
    echo "  /etc/systemd/system/chaoxing-backend.service"
    echo "  /etc/systemd/system/chaoxing-celery.service"
    echo ""
    print_info "修改完成后运行："
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable chaoxing-backend.service"
    echo "  sudo systemctl enable chaoxing-celery.service"
    echo "  sudo systemctl start chaoxing-backend.service"
    echo "  sudo systemctl start chaoxing-celery.service"
}

# ============ supervisor方式 ============
start_supervisor() {
    print_info "使用supervisor启动服务..."
    
    if ! command_exists supervisorctl; then
        print_error "supervisor未安装: pip install supervisor"
        return 1
    fi
    
    sudo supervisorctl start chaoxing:*
    print_success "supervisor服务已启动"
    sudo supervisorctl status
}

stop_supervisor() {
    print_info "停止supervisor服务..."
    sudo supervisorctl stop chaoxing:*
    print_success "supervisor服务已停止"
}

install_supervisor() {
    print_info "安装supervisor配置..."
    
    if [ ! -d "/etc/supervisor/conf.d" ]; then
        print_error "/etc/supervisor/conf.d 目录不存在，请先安装supervisor"
        return 1
    fi
    
    sudo cp "${PROJECT_ROOT}/web/supervisor.conf" /etc/supervisor/conf.d/chaoxing.conf
    print_success "已安装supervisor配置"
    
    print_warning "请编辑配置文件，修改项目路径和用户："
    echo "  /etc/supervisor/conf.d/chaoxing.conf"
    echo ""
    print_info "修改完成后运行："
    echo "  sudo supervisorctl reread"
    echo "  sudo supervisorctl update"
    echo "  sudo supervisorctl start chaoxing:*"
}

# ============ screen方式 ============
start_screen() {
    print_info "使用screen启动服务..."
    
    if ! command_exists screen; then
        print_error "screen未安装: sudo apt install screen"
        return 1
    fi
    
    # 启动后端
    if screen -list | grep -q "chaoxing-backend"; then
        print_warning "chaoxing-backend会话已存在"
    else
        cd "${BACKEND_DIR}"
        screen -dmS chaoxing-backend bash -c "source ${VENV_DIR}/bin/activate && python app.py"
        print_success "后端已在screen会话中启动"
    fi
    
    # 启动celery
    if screen -list | grep -q "chaoxing-celery"; then
        print_warning "chaoxing-celery会话已存在"
    else
        cd "${BACKEND_DIR}"
        screen -dmS chaoxing-celery bash -c "source ${VENV_DIR}/bin/activate && celery -A celery_app worker --loglevel=info"
        print_success "Celery已在screen会话中启动"
    fi
    
    print_info "查看会话: screen -ls"
    print_info "连接会话: screen -r chaoxing-backend"
    print_info "退出会话: Ctrl+A, D"
    
    screen -ls | grep chaoxing
}

stop_screen() {
    print_info "停止screen会话..."
    
    if screen -list | grep -q "chaoxing-backend"; then
        screen -S chaoxing-backend -X quit
        print_success "已停止chaoxing-backend会话"
    fi
    
    if screen -list | grep -q "chaoxing-celery"; then
        screen -S chaoxing-celery -X quit
        print_success "已停止chaoxing-celery会话"
    fi
}

# ============ nohup方式 ============
start_nohup() {
    print_info "使用nohup启动服务..."
    
    cd "${BACKEND_DIR}"
    
    # 启动后端
    if is_process_running "python.*app.py"; then
        print_warning "后端已在运行"
    else
        nohup ${VENV_DIR}/bin/python app.py > "${LOG_DIR}/nohup_backend.log" 2>&1 &
        echo $! > "${LOG_DIR}/backend.pid"
        print_success "后端已启动 (PID: $!)"
    fi
    
    # 启动celery
    if is_process_running "celery.*worker"; then
        print_warning "Celery已在运行"
    else
        nohup ${VENV_DIR}/bin/celery -A celery_app worker --loglevel=info > "${LOG_DIR}/nohup_celery.log" 2>&1 &
        echo $! > "${LOG_DIR}/celery.pid"
        print_success "Celery已启动 (PID: $!)"
    fi
    
    print_info "日志文件："
    echo "  后端: ${LOG_DIR}/nohup_backend.log"
    echo "  Celery: ${LOG_DIR}/nohup_celery.log"
}

stop_nohup() {
    print_info "停止nohup进程..."
    
    # 停止后端
    if [ -f "${LOG_DIR}/backend.pid" ]; then
        PID=$(cat "${LOG_DIR}/backend.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_success "已停止后端 (PID: $PID)"
        fi
        rm -f "${LOG_DIR}/backend.pid"
    fi
    
    # 停止celery
    if [ -f "${LOG_DIR}/celery.pid" ]; then
        PID=$(cat "${LOG_DIR}/celery.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_success "已停止Celery (PID: $PID)"
        fi
        rm -f "${LOG_DIR}/celery.pid"
    fi
    
    # 确保进程被杀死
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "celery.*worker" 2>/dev/null || true
}

# ============ 通用控制函数 ============
start_service() {
    local method=${1:-auto}
    
    case $method in
        auto)
            if command_exists systemctl && [ -f "/etc/systemd/system/chaoxing-backend.service" ]; then
                start_systemd
            elif command_exists supervisorctl && [ -f "/etc/supervisor/conf.d/chaoxing.conf" ]; then
                start_supervisor
            elif command_exists screen; then
                start_screen
            else
                start_nohup
            fi
            ;;
        systemd)
            start_systemd
            ;;
        supervisor)
            start_supervisor
            ;;
        screen)
            start_screen
            ;;
        nohup)
            start_nohup
            ;;
        *)
            print_error "未知方法: $method"
            show_help
            exit 1
            ;;
    esac
}

stop_service() {
    local method=${1:-all}
    
    if [ "$method" = "all" ]; then
        stop_systemd 2>/dev/null || true
        stop_supervisor 2>/dev/null || true
        stop_screen 2>/dev/null || true
        stop_nohup 2>/dev/null || true
    else
        case $method in
            systemd) stop_systemd ;;
            supervisor) stop_supervisor ;;
            screen) stop_screen ;;
            nohup) stop_nohup ;;
            *)
                print_error "未知方法: $method"
                exit 1
                ;;
        esac
    fi
}

show_status() {
    print_info "服务状态："
    echo ""
    
    # systemd
    if command_exists systemctl && systemctl is-active chaoxing-backend.service >/dev/null 2>&1; then
        print_success "systemd服务运行中"
        systemctl status chaoxing-backend.service --no-pager | head -5
        systemctl status chaoxing-celery.service --no-pager | head -5
        return
    fi
    
    # supervisor
    if command_exists supervisorctl; then
        STATUS=$(sudo supervisorctl status chaoxing:* 2>/dev/null || echo "")
        if [ ! -z "$STATUS" ]; then
            print_success "supervisor服务："
            echo "$STATUS"
            return
        fi
    fi
    
    # screen
    if command_exists screen; then
        SCREENS=$(screen -ls | grep chaoxing || echo "")
        if [ ! -z "$SCREENS" ]; then
            print_success "screen会话："
            echo "$SCREENS"
            return
        fi
    fi
    
    # 进程检查
    if is_process_running "python.*app.py"; then
        print_success "后端进程运行中"
        ps aux | grep "[p]ython.*app.py"
    else
        print_warning "后端未运行"
    fi
    
    if is_process_running "celery.*worker"; then
        print_success "Celery进程运行中"
        ps aux | grep "[c]elery.*worker"
    else
        print_warning "Celery未运行"
    fi
}

show_logs() {
    local service=${1:-backend}
    
    case $service in
        backend)
            if [ -f "${LOG_DIR}/nohup_backend.log" ]; then
                tail -f "${LOG_DIR}/nohup_backend.log"
            elif [ -f "${LOG_DIR}/backend.log" ]; then
                tail -f "${LOG_DIR}/backend.log"
            else
                print_error "未找到后端日志"
            fi
            ;;
        celery)
            if [ -f "${LOG_DIR}/nohup_celery.log" ]; then
                tail -f "${LOG_DIR}/nohup_celery.log"
            elif [ -f "${LOG_DIR}/celery.log" ]; then
                tail -f "${LOG_DIR}/celery.log"
            else
                print_error "未找到Celery日志"
            fi
            ;;
        *)
            print_error "未知服务: $service"
            echo "可用服务: backend, celery"
            ;;
    esac
}

# ============ 主程序 ============
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command=$1
    shift
    
    case $command in
        start)
            start_service "$@"
            ;;
        stop)
            stop_service "$@"
            ;;
        restart)
            stop_service "$@"
            sleep 2
            start_service "$@"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        install-systemd)
            install_systemd
            ;;
        install-supervisor)
            install_supervisor
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

