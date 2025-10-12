# 🚀 部署模式说明

> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)

---

## 📋 两种部署模式

Web平台支持两种部署模式，可在安装向导中选择：

### 1. 简单模式（推荐）⭐

**特点**：
- ✅ **零依赖** - 无需PostgreSQL和Redis
- ✅ **快速启动** - 只需Python和Node.js
- ✅ **易于维护** - 所有数据存储在SQLite文件
- ✅ **适合规模** - <50用户，<20并发任务

**技术栈**：
- 数据库：SQLite（aiosqlite）
- 任务队列：Celery + 文件系统broker
- 缓存：无需Redis

**数据存储**：
- `chaoxing_web.db` - SQLite数据库文件
- `celery_broker/` - Celery消息队列目录
- `celery_results/` - Celery结果存储目录

### 2. 标准模式

**特点**：
- ⚡ **高性能** - PostgreSQL + Redis
- ⚡ **高并发** - 支持大量用户
- ⚡ **生产级** - 企业级数据库
- ⚡ **适合规模** - >50用户，>20并发任务

**技术栈**：
- 数据库：PostgreSQL 15+
- 任务队列：Celery + Redis
- 缓存：Redis

**依赖服务**：
- PostgreSQL（需要安装）
- Redis（需要安装）

---

## 🎯 如何选择

### 选择简单模式，如果你：
- 🏠 个人或小团队使用（<10人）
- 💻 在Windows本地运行
- ⚡ 想快速体验，不想安装额外服务
- 📚 用于学习和测试

### 选择标准模式，如果你：
- 🏢 生产环境部署
- 👥 大团队使用（>10人）
- 🌐 对外提供服务
- 📈 需要高性能和稳定性

---

## 📦 简单模式部署

### Windows（推荐）

```batch
REM 1. 启动后端（双击）
web\start_backend.bat

REM 2. 启动Celery（双击）
web\start_celery.bat

REM 3. 启动前端（双击）
web\frontend\start.bat

REM 4. 访问
http://localhost:5173
```

### Linux/Mac

```bash
# 在项目根目录
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 后端（终端1）
cd web/backend
python app.py

# Celery（终端2）
cd web/backend
celery -A celery_app worker --loglevel=info

# 前端（终端3）
cd web/frontend
npm install
npm run dev
```

### Docker（简单模式）

```bash
cd web
docker-compose -f docker-compose.simple.yml up -d
```

---

## 📦 标准模式部署

### 前置要求
- PostgreSQL 15+
- Redis 7.0+

### 配置环境变量

编辑`web/.env`：

```env
# 修改为标准模式
DEPLOY_MODE=standard

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost/chaoxing_db

# Redis配置
REDIS_URL=redis://:password@localhost:6379/0
CELERY_BROKER_URL=redis://:password@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:password@localhost:6379/0
```

### Docker部署

```bash
cd web
cp env.example .env
# 编辑.env设置DEPLOY_MODE=standard
docker-compose up -d
```

---

## 🔄 模式切换

### 从简单模式升级到标准模式

1. **导出数据**（如需要）：
   ```bash
   # 导出SQLite数据
   sqlite3 chaoxing_web.db .dump > backup.sql
   ```

2. **安装依赖**：
   ```bash
   # 安装PostgreSQL和Redis
   ```

3. **修改配置**：
   ```env
   DEPLOY_MODE=standard
   DATABASE_URL=postgresql+asyncpg://...
   CELERY_BROKER_URL=redis://...
   ```

4. **迁移数据**（如需要）：
   ```bash
   # 导入到PostgreSQL
   psql -U user -d chaoxing_db < backup.sql
   ```

5. **重启服务**：
   ```bash
   docker-compose restart
   ```

### 从标准模式降级到简单模式

1. **备份数据**
2. **修改DEPLOY_MODE=simple**
3. **清理Redis数据**
4. **重启服务**

---

## 📊 性能对比

| 指标 | 简单模式 | 标准模式 |
|------|---------|---------|
| 启动时间 | <10秒 | <30秒 |
| 内存占用 | ~200MB | ~500MB |
| 并发用户 | 10-50人 | 100-1000人 |
| 并发任务 | 5-20个 | 50-200个 |
| API响应 | <100ms | <50ms |
| 数据库性能 | 中等 | 高 |
| 扩展性 | 低 | 高 |
| 部署难度 | 极简单 | 中等 |

---

## 💡 使用建议

### 个人使用
→ **简单模式** + Windows启动脚本

### 小团队（<10人）
→ **简单模式** + Docker Compose Simple

### 中型团队（10-50人）
→ **简单模式** 或 **标准模式**（根据性能需求）

### 大型团队（>50人）
→ **标准模式** + Docker Compose + Nginx

### 生产环境
→ **标准模式** + Docker + 负载均衡

---

## 🛠️ 故障排查

### 简单模式常见问题

**Q: Celery任务不执行？**
A: 检查celery_broker目录是否创建，自动创建失败请手动创建：
```bash
mkdir -p celery_broker/out celery_broker/processed
```

**Q: SQLite数据库锁定？**
A: 不要同时运行多个后端实例，SQLite不支持高并发写入

**Q: 数据库文件在哪？**
A: 在`web/backend/chaoxing_web.db`

### 标准模式常见问题

**Q: 无法连接PostgreSQL？**
A: 检查数据库是否运行，连接字符串是否正确

**Q: Redis连接失败？**
A: 检查Redis服务，确认密码正确

**Q: 性能慢？**
A: 调整PostgreSQL和Redis配置，增加连接池

---

## 📝 配置示例

### 简单模式.env

```env
DEPLOY_MODE=simple
DATABASE_URL=sqlite+aiosqlite:///./chaoxing_web.db
CELERY_BROKER_URL=filesystem://
CELERY_RESULT_BACKEND=file://./celery_results
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DEBUG=False
```

### 标准模式.env

```env
DEPLOY_MODE=standard
DATABASE_URL=postgresql+asyncpg://chaoxing:pass@localhost/chaoxing_db
REDIS_URL=redis://:pass@localhost:6379/0
CELERY_BROKER_URL=redis://:pass@localhost:6379/0
CELERY_RESULT_BACKEND=redis://:pass@localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DEBUG=False
```

---

## ✨ 推荐使用

**对于大多数用户**，我们推荐使用**简单模式**：
1. 部署简单，无需额外依赖
2. 性能足够应对小规模使用
3. 维护方便，数据存储在文件中
4. 可随时升级到标准模式

---

**相关文档**：
- [QUICK_START.md](../QUICK_START.md) - 快速启动
- [web/START_GUIDE.md](../web/START_GUIDE.md) - 详细指南
- [web/DEPLOYMENT_GUIDE.md](../web/DEPLOYMENT_GUIDE.md) - 部署指南

---

**最后更新**: 2025-10-12

