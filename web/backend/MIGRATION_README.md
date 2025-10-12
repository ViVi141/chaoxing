# 数据库迁移功能说明

## ✨ 功能概述

本系统提供了**图形化的数据库迁移功能**，允许管理员通过Web界面将SQLite数据库迁移到PostgreSQL + Redis，无需手动操作命令行。

---

## 🎯 适用场景

### 何时需要迁移？

- ✅ 用户规模超过30人
- ✅ 频繁出现 "database is locked" 错误
- ✅ 任务创建或执行缓慢
- ✅ 需要更高的并发处理能力

### 迁移后的优势

| 指标 | SQLite | PostgreSQL | 提升 |
|------|--------|------------|------|
| 支持用户数 | 20-30人 | 500+人 | 🚀 20倍+ |
| 并发任务 | 3-5个 | 50+个 | 🚀 10倍+ |
| 响应速度 | 1-3秒 | <500ms | 🚀 2-6倍 |
| 数据库锁 | 频繁 | 无 | ✅ 完全解决 |

---

## 📋 快速开始

### 1. 安装依赖

#### PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql

# Windows (Chocolatey)
choco install postgresql

# Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 postgres:15-alpine
```

#### Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# Windows (Chocolatey)
choco install redis-64

# Docker
docker run -d --name redis \
  -p 6379:6379 redis:7-alpine
```

### 2. 创建数据库

```sql
-- 连接PostgreSQL
psql -U postgres

-- 创建数据库和用户
CREATE USER chaoxing_user WITH PASSWORD 'your_password';
CREATE DATABASE chaoxing_db OWNER chaoxing_user;
GRANT ALL PRIVILEGES ON DATABASE chaoxing_db TO chaoxing_user;
```

### 3. Web图形化迁移

1. 以**管理员身份**登录Web界面
2. 进入：**管理员 → 数据库迁移**
3. 填写PostgreSQL和Redis连接信息
4. 测试连接（两个都要成功）
5. 点击"开始迁移"
6. 等待迁移完成（1-5分钟）
7. 重启服务

---

## 🔧 API端点

迁移功能提供以下API端点（管理员专用）：

### 测试连接

```bash
# 测试PostgreSQL
POST /api/migration/test-postgresql
Content-Type: application/json
Authorization: Bearer {token}

{
  "database_url": "postgresql+asyncpg://user:pass@host:5432/db"
}

# 测试Redis
POST /api/migration/test-redis
Content-Type: application/json
Authorization: Bearer {token}

{
  "redis_url": "redis://:password@host:6379/0"
}
```

### 开始迁移

```bash
POST /api/migration/start
Content-Type: application/json
Authorization: Bearer {token}

{
  "target_database_url": "postgresql+asyncpg://...",
  "redis_url": "redis://...",
  "confirm": true
}
```

### 查询状态

```bash
GET /api/migration/status
Authorization: Bearer {token}
```

返回：

```json
{
  "is_running": true,
  "current_step": "迁移数据",
  "progress": 45,
  "message": "正在迁移表: tasks...",
  "result": null,
  "error": null
}
```

### 获取当前配置

```bash
GET /api/migration/current-config
Authorization: Bearer {token}
```

---

## 📊 迁移流程

```
┌─────────────┐
│  准备阶段   │ → 测试目标数据库连接 (0-10%)
└─────────────┘
       ↓
┌─────────────┐
│  备份阶段   │ → 自动备份SQLite (10-20%)
└─────────────┘
       ↓
┌─────────────┐
│  创建表结构 │ → 在PostgreSQL创建表 (20-25%)
└─────────────┘
       ↓
┌─────────────┐
│  迁移数据   │ → 批量迁移所有表 (25-70%)
└─────────────┘
       ↓
┌─────────────┐
│  验证数据   │ → 对比记录数 (70-85%)
└─────────────┘
       ↓
┌─────────────┐
│  更新配置   │ → 自动修改.env (85-95%)
└─────────────┘
       ↓
┌─────────────┐
│  等待重启   │ → 提示重启服务 (95-100%)
└─────────────┘
```

---

## 🛠️ 技术实现

### 后端模块

#### `database_migration.py`

核心迁移逻辑：

- `DatabaseMigrator` 类：主迁移器
- `test_target_connection()`: 测试连接
- `backup_source_database()`: 备份SQLite
- `create_target_tables()`: 创建表结构
- `migrate_table_data()`: 迁移单表数据
- `verify_migration()`: 验证数据一致性
- `update_env_file()`: 更新配置文件

#### `routes/migration.py`

API路由：

- `POST /test-postgresql`: 测试PostgreSQL连接
- `POST /test-redis`: 测试Redis连接
- `GET /current-config`: 获取当前配置
- `POST /start`: 开始迁移
- `GET /status`: 查询迁移状态
- `POST /reset-status`: 重置状态

### 前端页面

#### `pages/admin/DatabaseMigration.tsx`

功能组件：

- 显示当前数据库配置
- 连接测试表单
- 实时进度显示（步骤条 + 进度条）
- 迁移结果验证表格
- 重启服务说明

### 进度推送

采用**轮询机制**（每2秒一次）而非WebSocket：

- 更简单可靠
- 迁移是短时间操作，轮询开销可接受
- 避免WebSocket连接管理复杂性

---

## 🔄 服务重启

### Windows

```batch
# 使用提供的脚本
cd web\backend
restart_service.bat

# 或手动
# 终端1
python app.py

# 终端2
celery -A celery_app worker --loglevel=info --pool=solo
```

### Linux

```bash
# 使用提供的脚本
cd web/backend
chmod +x restart_service.sh
./restart_service.sh

# 或Docker
docker-compose restart backend celery

# 或systemd
sudo systemctl restart chaoxing-backend chaoxing-celery
```

---

## ⚠️ 注意事项

### 迁移前

1. ✅ 确保PostgreSQL和Redis正常运行
2. ✅ 测试连接成功后再迁移
3. ✅ 选择业务低峰期执行
4. ✅ 通知用户系统将短暂不可用

### 迁移中

1. ⏳ 不要关闭浏览器
2. ⏳ 不要停止后端服务
3. ⏳ 耐心等待（通常1-5分钟）

### 迁移后

1. 🔄 必须重启服务才能生效
2. ✅ 验证数据完整性
3. ✅ 测试核心功能
4. 📦 保留SQLite备份文件

---

## 🐛 故障排查

### 连接测试失败

```bash
# PostgreSQL
psql -U chaoxing_user -h localhost -d chaoxing_db -c "SELECT 1"

# Redis
redis-cli ping
redis-cli -a password ping  # 如果有密码
```

### 迁移失败

1. 查看错误信息
2. 检查日志文件：`logs/chaoxing_error_*.log`
3. 使用备份恢复：`backups/chaoxing_backup_*.db`

### 服务无法启动

1. 检查.env文件是否正确更新
2. 确认PostgreSQL/Redis正常运行
3. 查看服务日志

---

## 📁 文件结构

```
web/backend/
├── database_migration.py         # 迁移工具（核心）
├── routes/
│   └── migration.py               # 迁移API路由
├── backups/                       # 自动备份目录
│   └── chaoxing_backup_*.db       # SQLite备份文件
├── restart_service.bat            # Windows重启脚本
└── restart_service.sh             # Linux重启脚本

web/frontend/src/pages/admin/
└── DatabaseMigration.tsx          # 迁移管理页面

docs/
└── DATABASE_MIGRATION.md          # 详细迁移文档
```

---

## 📖 相关文档

- [详细迁移指南](../../docs/DATABASE_MIGRATION.md)
- [配置说明](../../docs/CONFIGURATION.md)
- [数据库设计](../../docs/DATABASE.md)
- [API文档](../../docs/API.md)

---

## 🤝 技术支持

遇到问题？

1. 查看 [详细文档](../../docs/DATABASE_MIGRATION.md#常见问题)
2. 提交Issue：https://github.com/ViVi141/chaoxing/issues
3. 邮件联系：747384120@qq.com

---

**版本：** 2.1.0  
**更新：** 2025-10-13

