# 📦 数据库迁移指南

> 将SQLite数据库迁移到PostgreSQL + Redis，适合50+用户规模部署

---

## 📋 目录

- [迁移前准备](#迁移前准备)
- [Web图形化迁移（推荐）](#web图形化迁移推荐)
- [命令行迁移](#命令行迁移)
- [迁移后验证](#迁移后验证)
- [故障回滚](#故障回滚)
- [常见问题](#常见问题)

---

## 迁移前准备

### 1. 确认需要迁移

**何时需要迁移？**

- ✅ 用户数超过30人
- ✅ 出现频繁的 "database is locked" 错误
- ✅ 任务创建或执行缓慢
- ✅ 计划长期运营

**当前数据库类型检查：**

访问：管理员后台 → 数据库迁移 → 查看"当前数据库配置"

---

### 2. 安装PostgreSQL

#### Windows

```powershell
# 使用Chocolatey
choco install postgresql

# 或下载安装包
# https://www.postgresql.org/download/windows/
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Docker

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=chaoxing_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=chaoxing_db \
  -p 5432:5432 \
  postgres:15-alpine
```

---

### 3. 创建数据库

```bash
# 连接到PostgreSQL
sudo -u postgres psql

# 创建用户和数据库
CREATE USER chaoxing_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE chaoxing_db OWNER chaoxing_user;
GRANT ALL PRIVILEGES ON DATABASE chaoxing_db TO chaoxing_user;

# 退出
\q
```

---

### 4. 安装Redis

#### Windows

```powershell
# 使用Chocolatey
choco install redis-64

# 或下载安装包
# https://github.com/tporadowski/redis/releases
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# 设置密码（可选）
sudo nano /etc/redis/redis.conf
# 取消注释并设置：requirepass your_redis_password
sudo systemctl restart redis
```

#### Docker

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --requirepass your_redis_password
```

---

## Web图形化迁移（推荐）

### 步骤1：访问迁移管理页面

1. 以管理员身份登录Web界面
2. 进入：**管理员 → 数据库迁移**

### 步骤2：配置PostgreSQL

1. 填写PostgreSQL连接URL：
   ```
   postgresql+asyncpg://chaoxing_user:password@localhost:5432/chaoxing_db
   ```

2. 点击 **"测试PostgreSQL连接"**
3. 等待测试成功（✅ 绿色标记）

### 步骤3：配置Redis

1. 填写Redis连接URL：
   ```
   redis://:password@localhost:6379/0
   ```
   
   如果Redis没有设置密码：
   ```
   redis://localhost:6379/0
   ```

2. 点击 **"测试Redis连接"**
3. 等待测试成功（✅ 绿色标记）

### 步骤4：开始迁移

1. 确认两个连接都测试成功
2. 点击 **"开始迁移"** 按钮
3. 阅读确认对话框中的警告信息
4. 点击 **"确认迁移"**

### 步骤5：监控迁移进度

系统会自动显示迁移进度：

- ⏳ **准备**（0-10%）：测试目标数据库连接
- 📦 **备份**（10-20%）：备份当前SQLite数据库
- 🔄 **迁移**（20-70%）：迁移所有表数据
- ✅ **验证**（70-85%）：验证数据一致性
- ⚙️ **更新配置**（85-95%）：更新.env文件
- 🎉 **完成**（100%）：等待服务重启

**迁移时间：** 通常1-5分钟（取决于数据量）

### 步骤6：重启服务

#### Windows

```batch
# 方式1：使用提供的脚本
cd web\backend
restart_service.bat

# 方式2：手动重启
# 停止当前服务（Ctrl+C），然后：
python app.py
# 新终端
celery -A celery_app worker --loglevel=info --pool=solo
```

#### Linux

```bash
# 方式1：使用提供的脚本
cd web/backend
chmod +x restart_service.sh
./restart_service.sh

# 方式2：Docker
docker-compose restart backend celery

# 方式3：systemd
sudo systemctl restart chaoxing-backend
sudo systemctl restart chaoxing-celery
```

### 步骤7：验证迁移

1. 刷新Web页面
2. 检查 "当前数据库配置"：
   - ✅ 部署模式：**standard**
   - ✅ 数据库类型：**PostgreSQL**
   - ✅ 消息队列：**Redis**

3. 测试功能：
   - 登录系统
   - 查看任务列表
   - 创建测试任务
   - 查看任务日志

---

## 命令行迁移

### 使用Python脚本

```bash
cd web/backend
python database_migration.py
```

按照提示输入配置信息。

---

## 迁移后验证

### 1. 数据完整性检查

Web界面会自动显示验证结果：

| 表名 | 源记录数 | 目标记录数 | 状态 |
|------|----------|------------|------|
| users | 50 | 50 | ✅ 一致 |
| tasks | 234 | 234 | ✅ 一致 |
| task_logs | 15680 | 15680 | ✅ 一致 |

### 2. 功能测试

- ✅ 用户登录正常
- ✅ 任务创建成功
- ✅ 任务执行正常
- ✅ 实时日志显示
- ✅ WebSocket推送正常

### 3. 性能对比

迁移前后性能对比：

| 指标 | SQLite | PostgreSQL | 提升 |
|------|--------|------------|------|
| 任务列表加载 | 2-3秒 | <500ms | 🚀 4-6倍 |
| 任务创建 | 1-2秒 | <200ms | 🚀 5-10倍 |
| 并发任务数 | 3-5个 | 50+个 | 🚀 10倍+ |
| 数据库锁错误 | 频繁 | 无 | ✅ 完全解决 |

---

## 故障回滚

### 如果迁移失败或数据有问题

#### 方法1：恢复备份（快速）

```bash
# 1. 停止服务
# Windows: Ctrl+C
# Linux: sudo systemctl stop chaoxing-backend chaoxing-celery

# 2. 查找备份文件
cd web/backend/backups
ls -lh  # 查看备份文件列表

# 3. 恢复备份
cp chaoxing_backup_YYYYMMDD_HHMMSS.db ../data/chaoxing.db

# 4. 修改.env文件
cd ..
nano .env  # 或使用其他编辑器

# 修改以下配置：
DEPLOY_MODE=simple
DATABASE_URL=sqlite+aiosqlite:///./data/chaoxing.db
CELERY_BROKER_URL=filesystem://localhost/
CELERY_RESULT_BACKEND=file://./data/celery_results

# 5. 重启服务
./restart_service.sh  # Linux
# 或
restart_service.bat   # Windows
```

#### 方法2：从PostgreSQL导出（如果数据已经在PG中）

```bash
# 导出PostgreSQL数据
pg_dump -U chaoxing_user -d chaoxing_db > backup.sql

# 如需恢复到新的PostgreSQL
psql -U chaoxing_user -d chaoxing_db_new < backup.sql
```

---

## 常见问题

### Q1: 迁移失败，出现连接错误

**A:** 检查PostgreSQL/Redis是否正常运行：

```bash
# PostgreSQL
sudo systemctl status postgresql
psql -U chaoxing_user -h localhost -d chaoxing_db -c "SELECT 1"

# Redis
redis-cli ping
# 如果有密码
redis-cli -a your_password ping
```

### Q2: 迁移后部分数据丢失

**A:** 查看验证详情，如果记录数不匹配：

1. 停止服务
2. 恢复SQLite备份
3. 检查PostgreSQL连接稳定性
4. 重新执行迁移

### Q3: 服务重启后仍然使用SQLite

**A:** 检查.env文件是否已更新：

```bash
cat web/backend/.env | grep DATABASE_URL
```

应该显示：
```
DATABASE_URL=postgresql+asyncpg://...
```

如果没有更新，手动修改.env文件。

### Q4: Celery任务无法执行

**A:** 检查Redis连接：

```bash
# 测试Redis连接
redis-cli -a your_password ping

# 查看Celery日志
tail -f web/backend/logs/celery.log
```

确认CELERY_BROKER_URL配置正确。

### Q5: 迁移时间过长

**A:** 迁移时间取决于数据量：

| 数据量 | 预计时间 |
|--------|----------|
| <1000条记录 | 30秒 |
| 1000-10000条 | 1-2分钟 |
| 10000-50000条 | 2-5分钟 |
| 50000+条 | 5-15分钟 |

如果超过预期时间，检查：
- 网络连接是否稳定
- PostgreSQL是否有足够资源
- 是否有其他程序占用SQLite文件

### Q6: 可以迁回SQLite吗？

**A:** 理论上可以，但不推荐。步骤：

1. 停止服务
2. 恢复SQLite备份文件
3. 修改.env文件切回SQLite配置
4. 重启服务

**注意：** 迁移到PostgreSQL后产生的新数据不会自动同步回SQLite。

### Q7: 多久需要清理备份文件？

**A:** 建议保留最近3-5个备份文件：

```bash
cd web/backend/backups
ls -lt  # 按时间排序查看
rm chaoxing_backup_older_file.db  # 删除旧备份
```

---

## 性能优化建议

### PostgreSQL优化

#### 1. 调整连接池

修改 `web/backend/database.py`：

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,        # 增加连接池大小
    max_overflow=40,     # 增加溢出连接数
    pool_pre_ping=True
)
```

#### 2. 启用查询缓存

```sql
-- 连接到PostgreSQL
ALTER DATABASE chaoxing_db SET shared_buffers = '256MB';
ALTER DATABASE chaoxing_db SET effective_cache_size = '1GB';
```

### Redis优化

#### 1. 调整内存限制

```bash
# 编辑Redis配置
sudo nano /etc/redis/redis.conf

# 设置最大内存
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### 2. 启用持久化

```bash
# RDB持久化
save 900 1
save 300 10
save 60 10000

# AOF持久化
appendonly yes
```

---

## 监控与维护

### 1. 数据库大小监控

```bash
# PostgreSQL数据库大小
psql -U chaoxing_user -d chaoxing_db -c "
  SELECT pg_size_pretty(pg_database_size('chaoxing_db'));
"

# 表大小统计
psql -U chaoxing_user -d chaoxing_db -c "
  SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### 2. 定期清理日志

```sql
-- 删除30天前的任务日志
DELETE FROM task_logs WHERE created_at < NOW() - INTERVAL '30 days';

-- 删除90天前的系统日志
DELETE FROM system_logs WHERE created_at < NOW() - INTERVAL '90 days';

-- 清理已完成的任务（180天前）
DELETE FROM tasks 
WHERE status = 'completed' 
AND end_time < NOW() - INTERVAL '180 days';
```

### 3. 备份策略

#### 自动备份脚本

```bash
#!/bin/bash
# backup_postgres.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/chaoxing"
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U chaoxing_user chaoxing_db | gzip > $BACKUP_DIR/chaoxing_$DATE.sql.gz

# 保留最近7天的备份
find $BACKUP_DIR -name "chaoxing_*.sql.gz" -mtime +7 -delete

echo "Backup completed: chaoxing_$DATE.sql.gz"
```

添加到crontab：
```bash
# 每天凌晨2点自动备份
0 2 * * * /path/to/backup_postgres.sh
```

---

## 技术支持

如果遇到问题：

1. 📖 查看 [常见问题](#常见问题)
2. 🔍 查看服务日志：`web/backend/logs/`
3. 💬 提交Issue：https://github.com/ViVi141/chaoxing/issues
4. 📧 邮件联系：747384120@qq.com

---

**最后更新：** 2025-10-13  
**版本：** 2.1.0

