#!/bin/bash
# -*- coding: utf-8 -*-
# 数据库备份脚本
# 用途：定期备份SQLite/PostgreSQL数据库
# 使用：./backup.sh [sqlite|postgres]

set -e

# 配置
BACKUP_DIR="/var/backups/chaoxing"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SQLITE_DB_FILE="${PROJECT_ROOT}/web/backend/data/chaoxing.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $@${NC}"
}

print_error() {
    echo -e "${RED}✗ $@${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $@${NC}"
}

# 创建备份目录
mkdir -p "$BACKUP_DIR"

backup_sqlite() {
    print_info "开始备份SQLite数据库..."
    
    if [ ! -f "$SQLITE_DB_FILE" ]; then
        print_error "数据库文件不存在: $SQLITE_DB_FILE"
        exit 1
    fi
    
    # 备份文件名
    BACKUP_FILE="$BACKUP_DIR/chaoxing_sqlite_${TIMESTAMP}.db"
    
    # 复制数据库文件
    cp "$SQLITE_DB_FILE" "$BACKUP_FILE"
    
    # 压缩
    gzip "$BACKUP_FILE"
    
    # 获取文件大小
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    
    print_success "SQLite备份完成: ${BACKUP_FILE}.gz ($SIZE)"
    
    # 删除7天前的备份
    find "$BACKUP_DIR" -name "chaoxing_sqlite_*.db.gz" -mtime +7 -delete
    print_info "已删除7天前的旧备份"
}

backup_postgres() {
    print_info "开始备份PostgreSQL数据库..."
    
    # 从环境变量或.env文件读取配置
    if [ -f "${PROJECT_ROOT}/web/.env" ]; then
        source "${PROJECT_ROOT}/web/.env"
    fi
    
    # 默认配置
    PG_HOST=${POSTGRES_HOST:-localhost}
    PG_PORT=${POSTGRES_PORT:-5432}
    PG_USER=${POSTGRES_USER:-chaoxing}
    PG_DB=${POSTGRES_DB:-chaoxing}
    
    # 检查pg_dump是否可用
    if ! command -v pg_dump &> /dev/null; then
        print_error "pg_dump未安装，请安装PostgreSQL客户端工具"
        exit 1
    fi
    
    # 备份文件名
    BACKUP_FILE="$BACKUP_DIR/chaoxing_postgres_${TIMESTAMP}.sql"
    
    # 使用pg_dump备份
    # 注意：需要配置.pgpass或PGPASSWORD环境变量
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
        --format=plain \
        --no-owner \
        --no-acl \
        > "$BACKUP_FILE"
    
    # 压缩
    gzip "$BACKUP_FILE"
    
    # 获取文件大小
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    
    print_success "PostgreSQL备份完成: ${BACKUP_FILE}.gz ($SIZE)"
    
    # 删除7天前的备份
    find "$BACKUP_DIR" -name "chaoxing_postgres_*.sql.gz" -mtime +7 -delete
    print_info "已删除7天前的旧备份"
}

backup_all() {
    print_info "备份所有数据..."
    
    # 备份SQLite（如果存在）
    if [ -f "$SQLITE_DB_FILE" ]; then
        backup_sqlite
    fi
    
    # 备份PostgreSQL（如果配置了）
    if [ -f "${PROJECT_ROOT}/web/.env" ]; then
        source "${PROJECT_ROOT}/web/.env"
        if [ ! -z "$POSTGRES_HOST" ]; then
            backup_postgres
        fi
    fi
    
    print_success "所有数据库备份完成"
}

show_backups() {
    print_info "现有备份列表:"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR" | grep "chaoxing_" | awk '{print $9, "(" $5 ")", $6, $7, $8}'
    else
        print_info "备份目录不存在"
    fi
}

restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        print_error "请指定要恢复的备份文件"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    print_info "准备恢复备份: $backup_file"
    
    # 确认操作
    read -p "这将覆盖当前数据库，是否继续？(yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "操作已取消"
        exit 0
    fi
    
    # 根据文件类型恢复
    if [[ $backup_file == *"sqlite"* ]]; then
        # 解压并恢复SQLite
        gunzip -c "$backup_file" > "$SQLITE_DB_FILE"
        print_success "SQLite数据库已恢复"
    elif [[ $backup_file == *"postgres"* ]]; then
        # 恢复PostgreSQL
        source "${PROJECT_ROOT}/web/.env"
        gunzip -c "$backup_file" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"
        print_success "PostgreSQL数据库已恢复"
    else
        print_error "未知的备份文件类型"
        exit 1
    fi
}

show_help() {
    cat << EOF
数据库备份脚本

用法: $0 [命令] [选项]

命令:
    sqlite          仅备份SQLite数据库
    postgres        仅备份PostgreSQL数据库
    all             备份所有数据库（默认）
    list            列出现有备份
    restore <file>  恢复指定备份
    help            显示此帮助

示例:
    $0                                  # 备份所有数据库
    $0 sqlite                           # 仅备份SQLite
    $0 list                             # 查看备份列表
    $0 restore backup_file.sql.gz       # 恢复备份

定时任务（crontab）:
    0 2 * * * /path/to/backup.sh all    # 每天凌晨2点自动备份

备份目录: $BACKUP_DIR
保留时间: 7天

EOF
}

# 主程序
case "${1:-all}" in
    sqlite)
        backup_sqlite
        ;;
    postgres)
        backup_postgres
        ;;
    all)
        backup_all
        ;;
    list)
        show_backups
        ;;
    restore)
        restore_backup "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac

exit 0

