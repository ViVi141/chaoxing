# :package: 生产环境部署指南

> 基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)  
> 开发: ViVi141 (747384120@qq.com) | 更新: 2025-10-12

## 🚀 快速开始（Docker方式 - 推荐）

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少2GB内存

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/Samueli924/chaoxing
cd chaoxing/web

# 2. 复制环境配置
cp .env.example .env

# 3. 修改.env文件中的关键配置
nano .env  # 修改SECRET_KEY、数据库密码等

# 4. 启动所有服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f

# 6. 访问
# 前端: http://localhost:3000
# 后端API文档: http://localhost:8000/api/docs
# 管理员后台: http://localhost:3000/admin
```

### 默认账号
- 用户名: `admin`
- 密码: `Admin@123`
- **⚠️ 首次登录后立即修改密码！**

## 📋 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (80/443)                       │
│                   反向代理 + 静态文件服务                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴──────────────┐
        │                              │
┌───────▼────────┐            ┌───────▼────────┐
│  Frontend      │            │   Backend      │
│  Vue 3 (3000)  │            │  FastAPI (8000)│
└────────────────┘            └────────┬───────┘
                                       │
                        ┌──────────────┼──────────────┐
                        │              │              │
                 ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼─────┐
                 │ PostgreSQL │ │   Redis    │ │  Celery  │
                 │   (5432)   │ │   (6379)   │ │  Worker  │
                 └────────────┘ └────────────┘ └──────────┘
```

## 📦 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| nginx | 80, 443 | 反向代理和静态文件 |
| backend | 8000 | FastAPI后端服务 |
| frontend | 3000 | Vue 3前端开发服务器 |
| postgres | 5432 | PostgreSQL数据库 |
| redis | 6379 | Redis缓存和消息队列 |
| celery | - | Celery异步任务Worker |

## 🔧 手动部署（不使用Docker）

### 后端部署

```bash
# 1. 安装Python 3.10+
python --version  # 确保是3.10或以上

# 2. 创建虚拟环境
cd web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
nano .env  # 修改配置

# 5. 初始化数据库
alembic upgrade head

# 6. 启动后端服务（开发模式）
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# 生产模式（使用Gunicorn）
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
```

### Celery Worker部署

```bash
# 在backend目录下
source venv/bin/activate

# 启动Celery Worker
celery -A celery_app worker --loglevel=info \
  --concurrency=4 --max-tasks-per-child=1000

# 启动Celery Beat（定时任务，如需要）
celery -A celery_app beat --loglevel=info
```

### 前端部署

```bash
# 1. 安装Node.js 18+
node --version  # 确保是18或以上

# 2. 安装pnpm（推荐）或npm
npm install -g pnpm

# 3. 安装依赖
cd web/frontend
pnpm install

# 4. 配置环境变量
cp .env.example .env
nano .env  # 修改API地址等

# 5. 开发模式
pnpm dev

# 6. 生产构建
pnpm build

# 7. 预览生产构建
pnpm preview
```

### Nginx配置

```nginx
# /etc/nginx/sites-available/chaoxing

upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/chaoxing/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# SSL配置（使用Let's Encrypt）
# certbot --nginx -d your-domain.com
```

## 🐘 PostgreSQL设置

```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE chaoxing_db;
CREATE USER chaoxing_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chaoxing_db TO chaoxing_user;
\q

# 更新.env中的数据库URL
DATABASE_URL=postgresql+asyncpg://chaoxing_user:your_password@localhost/chaoxing_db
```

## 🔐 安全配置清单

### 必须修改的配置
- [ ] `SECRET_KEY` - 生成强随机密钥
- [ ] `JWT_SECRET_KEY` - 生成强随机密钥
- [ ] `DEFAULT_ADMIN_PASSWORD` - 修改默认管理员密码
- [ ] 数据库密码
- [ ] Redis密码（生产环境）

### 生成安全密钥

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 推荐的安全措施
1. ✅ 使用HTTPS（Let's Encrypt免费证书）
2. ✅ 配置防火墙（只开放80/443端口）
3. ✅ 定期备份数据库
4. ✅ 启用Redis认证
5. ✅ 使用非root用户运行服务
6. ✅ 限制API请求频率
7. ✅ 定期更新依赖

## 📊 监控和维护

### 日志查看

```bash
# Docker方式
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f nginx

# 手动部署
tail -f logs/web_app.log
tail -f logs/celery.log
tail -f /var/log/nginx/access.log
```

### 数据库备份

```bash
# 备份
docker-compose exec postgres pg_dump -U chaoxing_user chaoxing_db > backup.sql

# 恢复
docker-compose exec -T postgres psql -U chaoxing_user chaoxing_db < backup.sql
```

### 性能监控

```bash
# 查看资源使用
docker stats

# 查看Celery任务状态
celery -A celery_app inspect active
celery -A celery_app inspect stats
```

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新后端
cd web/backend
pip install -r requirements.txt
alembic upgrade head

# 3. 重启服务
docker-compose restart backend celery

# 4. 更新前端
cd web/frontend
pnpm install
pnpm build

# 5. 重启Nginx
docker-compose restart nginx
```

## ⚡ 性能优化

### 后端优化
```python
# config.py中调整
- 增加数据库连接池大小
- 调整Celery并发数
- 启用响应压缩
- 使用Redis缓存
```

### 前端优化
```javascript
// vite.config.js
- 启用代码分割
- 压缩资源
- 使用CDN加速
- 启用浏览器缓存
```

## 🐛 故障排查

### 后端无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查数据库连接
psql -U chaoxing_user -d chaoxing_db -h localhost

# 查看详细错误
uvicorn app:app --log-level debug
```

### Celery任务不执行
```bash
# 检查Redis连接
redis-cli ping

# 检查Celery Worker状态
celery -A celery_app inspect ping

# 清空任务队列
celery -A celery_app purge
```

### 数据库迁移失败
```bash
# 查看当前版本
alembic current

# 回滚到上一版本
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 📈 扩展性

### 水平扩展
- 增加Celery Worker数量
- 使用负载均衡（多个backend实例）
- 使用PostgreSQL主从复制

### 垂直扩展
- 增加服务器内存和CPU
- 使用更快的SSD
- 优化数据库索引

## 📞 技术支持

遇到问题？
1. 查看日志文件
2. 搜索GitHub Issues
3. 提交新Issue（包含日志和环境信息）

## 📜 许可证

GPL-3.0 License

---

**祝部署顺利！** 🎉

