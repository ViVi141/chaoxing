# Docker部署指南

**版本**: v2.3.0  
**适用**: Docker部署完整指南

---

## 🐳 Docker镜像信息

### 预构建镜像

本项目提供预构建的Docker镜像，支持多架构：

| 镜像源 | 拉取命令 | 说明 |
|--------|---------|------|
| **Docker Hub** | `docker pull vivi141/chaoxing:latest` | 全球访问 |
| **GitHub** | `docker pull ghcr.io/vivi141/chaoxing:latest` | 推荐国内 |

**支持架构**:
- ✅ `linux/amd64` - x86_64服务器/PC
- ✅ `linux/arm64` - ARM64服务器/树莓派

**版本标签**:
- `latest` - 最新稳定版（推荐使用）
- `main` - 主分支最新（开发版）

---

## 🚀 快速开始

### 方式1：使用预构建镜像（推荐）

```bash
# 1. 创建工作目录
mkdir chaoxing && cd chaoxing

# 2. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 3. 创建.env文件
cat > .env << EOF
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
EOF

# 4. 修改docker-compose.yml使用预构建镜像
# 将backend的build部分替换为：
#   backend:
#     image: ghcr.io/vivi141/chaoxing:latest
#     # build:
#     #   context: ..
#     #   dockerfile: web/backend/Dockerfile

# 5. 启动服务
docker compose up -d

# 6. 查看日志
docker compose logs -f backend

# 7. 访问
# 前端界面：http://localhost:8000
# API 文档：http://localhost:8000/api/docs
```

### 方式2：从源码构建

```bash
# 1. 克隆仓库
git clone https://github.com/ViVi141/chaoxing.git
cd chaoxing/web

# 2. 启动服务（自动构建）
docker compose up -d

# 3. 访问
# 前端界面：http://localhost:8000
# API 文档：http://localhost:8000/api/docs
```

---

## 📋 docker-compose.yml配置

### 完整版（PostgreSQL + Redis）

```yaml
services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: chaoxing_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme123}
      POSTGRES_DB: chaoxing_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD:-changeme123}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # 后端服务（使用预构建镜像）
  backend:
    image: ghcr.io/vivi141/chaoxing:latest
    environment:
      DATABASE_URL: postgresql+asyncpg://chaoxing_user:${POSTGRES_PASSWORD}@postgres:5432/chaoxing_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Celery Worker
  celery:
    image: ghcr.io/vivi141/chaoxing:latest
    command: celery -A celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql+asyncpg://chaoxing_user:${POSTGRES_PASSWORD}@postgres:5432/chaoxing_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 简化版（SQLite）

```yaml
services:
  backend:
    image: ghcr.io/vivi141/chaoxing:latest
    environment:
      DATABASE_URL: sqlite:///./data/chaoxing.db
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    restart: unless-stopped
```

---

## 🌐 访问说明

### 端口配置

**统一端口：`8000`**

- **前端界面**：`http://localhost:8000`
  - 访问 Web 管理界面
  - 前端和后端统一通过端口 8000 提供服务
  
- **API 文档**：`http://localhost:8000/api/docs`
  - Swagger UI 交互式 API 文档
  - 可用于测试 API 接口

- **API 端点**：`http://localhost:8000/api/*`
  - 所有 API 请求以 `/api/` 开头
  - 例如：`/api/auth/login`、`/api/tasks`

- **WebSocket**：`ws://localhost:8000/ws/*`
  - WebSocket 连接以 `/ws/` 开头
  - 例如：`/ws/connect`

### 生产环境部署

如果需要在生产环境部署，建议：

1. **使用 Nginx 反向代理**（推荐）
   - 配置 SSL/TLS 证书
   - 设置域名和端口映射
   - 参考下方 Nginx 配置示例

2. **修改端口映射**
   ```yaml
   ports:
     - "80:8000"    # HTTP
     - "443:8000"   # HTTPS（需要额外配置）
   ```

---

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f backend

# 进入容器
docker compose exec backend bash
```

### 镜像管理

```bash
# 拉取最新镜像
docker pull ghcr.io/vivi141/chaoxing:latest

# 查看本地镜像
docker images | grep chaoxing

# 删除旧镜像
docker rmi vivi141/chaoxing:old_version

# 清理未使用镜像
docker image prune -a
```

### 数据库管理

```bash
# 数据库迁移
docker compose exec backend alembic upgrade head

# 创建管理员用户
docker compose exec backend python -c "
from web.backend.database import SessionLocal
from web.backend.models import User
from web.backend.security import get_password_hash

db = SessionLocal()
user = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    is_active=True,
    is_superuser=True
)
db.add(user)
db.commit()
print('Admin user created!')
"

# 备份数据库
docker compose exec postgres pg_dump -U chaoxing_user chaoxing_db > backup.sql

# 恢复数据库
docker compose exec -T postgres psql -U chaoxing_user chaoxing_db < backup.sql
```

---

## 🔄 更新版本

### 更新到最新版本

```bash
# 1. 停止服务
docker compose down

# 2. 拉取最新镜像
docker compose pull

# 3. 启动服务
docker compose up -d

# 4. 查看日志确认
docker compose logs -f backend
```


---

## 🌐 反向代理配置

### Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Traefik

```yaml
services:
  backend:
    image: ghcr.io/vivi141/chaoxing:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.chaoxing.rule=Host(`your-domain.com`)"
      - "traefik.http.services.chaoxing.loadbalancer.server.port=8000"
```

---

## 🔒 安全配置

### 环境变量

创建 `.env` 文件（不要提交到Git）：

```bash
# 数据库密码（强密码）
POSTGRES_PASSWORD=your_very_secure_password_here_32_chars

# Redis密码
REDIS_PASSWORD=your_redis_password_here_16_chars

# JWT密钥（至少32字符）
SECRET_KEY=your_secret_key_minimum_32_characters_long
JWT_SECRET_KEY=your_jwt_secret_key_also_32_chars

# 调试模式（生产环境必须为False）
DEBUG=False

# 日志级别
LOG_LEVEL=INFO
```

### 生成安全密钥

```bash
# Python生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL生成
openssl rand -base64 32
```

---

## 📊 性能优化

### 资源限制

```yaml
services:
  backend:
    image: ghcr.io/vivi141/chaoxing:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 健康检查

```yaml
services:
  backend:
    image: ghcr.io/vivi141/chaoxing:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 🐛 故障排除

### 常见问题

#### 1. 容器无法启动

```bash
# 查看日志
docker compose logs backend

# 检查环境变量
docker compose config

# 检查端口占用
netstat -tlnp | grep 8000
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker compose ps postgres

# 测试连接
docker compose exec backend python -c "
from web.backend.database import engine
try:
    engine.connect()
    print('Database connection OK!')
except Exception as e:
    print(f'Connection failed: {e}')
"
```

#### 3. 镜像拉取失败

```bash
# 使用镜像加速（中国用户）
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启Docker
sudo systemctl restart docker

# 或使用Docker Hub
docker pull vivi141/chaoxing:latest
```

---

## 📈 监控

### Docker Stats

```bash
# 实时监控
docker stats

# 查看特定容器
docker stats chaoxing_backend
```

### 日志管理

```bash
# 限制日志大小
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🔗 相关链接

- [Docker Hub](https://hub.docker.com/r/vivi141/chaoxing)
- [GitHub Container Registry](https://github.com/ViVi141/chaoxing/pkgs/container/chaoxing)
- [Docker文档](https://docs.docker.com/)
- [守护进程部署](DAEMON.md)

---

**GPL-3.0** 开源协议 | 完全免费使用

