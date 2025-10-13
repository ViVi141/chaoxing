# Web界面配置数据库

**版本**: v2.3.0  
**适用**: 通过Web界面配置和迁移数据库

---

## 🎯 渐进式部署策略

### 推荐流程

```
步骤1：SQLite快速启动（1分钟）
   ↓
步骤2：使用和测试功能（随时）
   ↓
步骤3：Web界面配置PostgreSQL（可选，5分钟）
   ↓
步骤4：Web界面配置Redis（可选，3分钟）
   ↓
完成：生产级配置
```

---

## 🚀 步骤1：SQLite快速启动

### Docker方式（推荐）

```bash
# 1. 创建目录
mkdir -p chaoxing && cd chaoxing

# 2. 下载简化配置
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.simple.yml

# 3. 创建.env（可选，使用默认值也可以）
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-32-chars
JWT_SECRET_KEY=your-jwt-secret-32-chars
EOF

# 4. 启动（使用SQLite）
docker compose -f docker-compose.simple.yml up -d

# 5. 访问
# http://localhost:8000
```

### 宝塔/1Panel方式

```bash
# 下载Release包后，默认就是SQLite模式
cd /www/wwwroot/chaoxing/release-package
./一键安装.sh

# 会自动使用SQLite
# DATABASE_URL=sqlite:///./data/chaoxing.db
```

---

## 📊 步骤2：Web界面配置（规划中）

### 当前状态
⚠️ **Web界面数据库配置功能正在开发中**

当前需要手动配置（见步骤3），未来版本会提供：
- 🔄 Web界面数据库迁移向导
- 🔄 一键从SQLite迁移到PostgreSQL
- 🔄 Redis配置管理界面

---

## 🔧 步骤3：手动配置高级数据库（当前方法）

### 从SQLite迁移到PostgreSQL

#### Docker环境

```bash
# 1. 停止当前服务
docker compose -f docker-compose.simple.yml down

# 2. 备份SQLite数据
cp web/backend/data/chaoxing.db chaoxing.db.backup

# 3. 下载完整配置
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 4. 创建.env配置
cat > .env << 'EOF'
# PostgreSQL配置
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 应用密钥
SECRET_KEY=your_secret_key_32_chars
JWT_SECRET_KEY=your_jwt_secret_32_chars

# 其他
DEBUG=False
EOF

# 5. 启动完整环境（包含PostgreSQL + Redis）
docker compose up -d

# 6. 等待数据库就绪
docker compose logs -f postgres

# 7. 迁移数据（可选）
docker compose exec backend python tools/migrate_sqlite_to_postgres.py
```

#### 宝塔面板环境

```bash
# 1. 创建PostgreSQL数据库
# 宝塔 → 数据库 → 添加数据库
# 名称：chaoxing_db
# 用户：chaoxing_user
# 密码：生成强密码

# 2. 修改配置文件
nano /www/wwwroot/chaoxing/web/backend/.env

# 修改为：
DATABASE_URL=postgresql+asyncpg://chaoxing_user:密码@localhost:5432/chaoxing_db

# 3. 重启Python项目
# 宝塔 → Python项目管理器 → 重启

# 4. 运行数据迁移（如果有旧数据）
cd /www/wwwroot/chaoxing/web/backend
source ../../.venv/bin/activate
alembic upgrade head
```

---

## 📖 配置详解

### SQLite + Redis配置（简化模式）

**优点**：
- ✅ 快速启动（1分钟）
- ✅ 轻量级（SQLite + Redis）
- ✅ 支持Celery后台任务
- ✅ 适合1-20人使用

**缺点**：
- ⚠️ SQLite不支持高并发（20+人建议升级）
- ⚠️ 不支持分布式部署

**适用场景**：
- ✅ 个人使用
- ✅ 小团队（5-20人）
- ✅ 快速体验测试

**配置**：
```bash
DATABASE_URL=sqlite:///./data/chaoxing.db
```

---

### PostgreSQL配置（推荐生产）

**优点**：
- ✅ 高性能
- ✅ 支持并发
- ✅ 事务完整性
- ✅ 适合团队使用

**配置**：
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
```

**示例**：
```bash
# Docker环境（容器名）
DATABASE_URL=postgresql+asyncpg://chaoxing_user:pass@postgres:5432/chaoxing_db

# 宝塔环境（localhost）
DATABASE_URL=postgresql+asyncpg://chaoxing_user:pass@localhost:5432/chaoxing_db

# 远程数据库
DATABASE_URL=postgresql+asyncpg://user:pass@192.168.1.100:5432/chaoxing_db
```

---

### Redis配置（可选）

**功能**：
- ✅ Celery任务队列（后台任务）
- ✅ 缓存（提升性能）
- ✅ Session存储

**配置**：
```bash
# 无密码
REDIS_URL=redis://localhost:6379/0

# 有密码
REDIS_URL=redis://:password@localhost:6379/0

# Docker环境
REDIS_URL=redis://:password@redis:6379/0
```

**如果不配置Redis**：
- ⚠️ Celery功能不可用（但不影响核心功能）
- ⚠️ 无法使用后台任务
- ✅ 其他功能正常

---

## 🔄 升级路径

### 路径1：SQLite → PostgreSQL

```bash
# 适合：用户增长，需要更好性能

1. 安装PostgreSQL
2. 修改DATABASE_URL
3. 运行数据迁移
4. 重启服务
```

### 路径2：无Redis → 有Redis

```bash
# 适合：需要后台任务功能

1. 安装Redis
2. 添加REDIS_URL配置
3. 启动Celery worker
4. 重启服务
```

### 路径3：完整升级

```bash
# SQLite → PostgreSQL + Redis

1. 使用docker-compose.yml替换simple版本
2. docker compose up -d
3. 自动迁移数据
4. 完成！
```

---

## 💡 最佳实践

### 个人使用（1-5人）
```yaml
推荐配置：
- 数据库：SQLite ✅
- Redis：不需要 ❌
- 部署时间：1分钟
```

### 小团队（5-20人）
```yaml
推荐配置：
- 数据库：PostgreSQL ✅
- Redis：可选 ⚠️
- 部署时间：5分钟
```

### 中大型（20+人）
```yaml
推荐配置：
- 数据库：PostgreSQL ✅
- Redis：必需 ✅
- Celery：必需 ✅
- 部署时间：10分钟
```

---

## 🔗 相关文档

- [数据库迁移指南](DATABASE_MIGRATION.md)
- [Docker简化配置](../web/docker-compose.simple.yml)
- [Docker完整配置](../web/docker-compose.yml)
- [宝塔/1Panel部署](BAOTA_1PANEL_DEPLOY.md)

---

**GPL-3.0** 开源协议 | 完全免费使用

