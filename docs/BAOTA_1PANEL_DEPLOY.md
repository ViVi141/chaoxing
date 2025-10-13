# 宝塔面板/1Panel部署指南

**版本**: v2.3.0  
**适用**: 使用国内服务器管理面板的用户

---

## ✅ 完全兼容确认

你的项目**完美兼容**宝塔面板和1Panel：

| 组件 | 要求 | 宝塔/1Panel支持 | 状态 |
|------|------|----------------|------|
| **Python后端** | FastAPI + uvicorn | ✅ 原生支持 | ✅ |
| **前端** | 静态文件 | ✅ Nginx托管 | ✅ |
| **不需要Node.js** | ❌ 运行时 | ✅ 完美 | ✅ |
| **数据库** | PostgreSQL/SQLite | ✅ 支持 | ✅ |
| **Redis** | 可选 | ✅ 支持 | ✅ |

---

## 🚀 宝塔面板部署（推荐）

### 方式1：Python项目管理器（简单）⭐⭐⭐⭐⭐

#### 步骤1：准备环境

```bash
# 1. 安装Python管理器
宝塔面板 → 软件商店 → Python项目管理器 → 安装

# 2. 安装Python 3.10+
宝塔面板 → 软件商店 → Python 3.11 → 安装

# 3. 上传Release包
# 下载：https://github.com/ViVi141/chaoxing/releases/latest
# 上传到：/www/wwwroot/chaoxing/
```

#### 步骤2：解压并配置

```bash
# SSH连接服务器
cd /www/wwwroot/chaoxing/
tar -xzf chaoxing-v2.3.0-linux-x64.tar.gz
cd release-package/

# 运行一键安装脚本
chmod +x 一键安装.sh
./一键安装.sh

# 选择 "Web平台模式"
```

#### 步骤3：配置Python项目

```
1. 宝塔面板 → Python项目管理器 → 添加项目

项目配置：
- 项目名称：chaoxing
- 项目路径：/www/wwwroot/chaoxing/release-package/web/backend
- Python版本：3.11
- 启动文件：app.py
- 启动方式：python
- 启动命令：
  python app.py
  
  或使用gunicorn（推荐生产环境）：
  gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

- 端口：8000
- 是否开机启动：是
```

#### 步骤4：配置Nginx反向代理

```nginx
# 宝塔面板 → 网站 → 添加站点
# 域名：your-domain.com
# 根目录：/www/wwwroot/chaoxing/release-package/web/frontend/dist

# 点击"设置" → 配置文件，添加：

location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket支持
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

location /ws {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

#### 步骤5：配置Celery（可选）

```bash
# 创建Celery启动脚本
宝塔面板 → 计划任务 → Shell脚本

名称：Chaoxing Celery Worker
脚本内容：
#!/bin/bash
cd /www/wwwroot/chaoxing/release-package/web/backend
source ../../.venv/bin/activate
celery -A celery_app worker --detach --loglevel=info

执行周期：开机时执行
```

#### 步骤6：配置数据库

```bash
# 如果使用PostgreSQL
宝塔面板 → 数据库 → 添加数据库
- 数据库名：chaoxing_db
- 用户名：chaoxing_user
- 密码：生成强密码

# 修改后端配置
nano /www/wwwroot/chaoxing/release-package/web/backend/.env

DATABASE_URL=postgresql+asyncpg://chaoxing_user:密码@localhost:5432/chaoxing_db
```

#### 步骤7：运行迁移

```bash
cd /www/wwwroot/chaoxing/release-package/web/backend
source ../../.venv/bin/activate
alembic upgrade head
```

#### 步骤8：完成！

访问：`http://your-domain.com`

---

### 方式2：Docker Compose（最简单）⭐⭐⭐⭐⭐

#### 前置要求

```bash
# 安装Docker
宝塔面板 → 软件商店 → Docker → 安装
宝塔面板 → 软件商店 → Docker Compose → 安装
```

#### 部署步骤

```bash
# 1. 创建目录
mkdir -p /www/wwwroot/chaoxing
cd /www/wwwroot/chaoxing

# 2. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 3. 创建.env文件
cat > .env << EOF
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
EOF

# 4. 启动
docker compose up -d

# 5. 查看状态
docker compose ps
```

#### 配置Nginx反向代理

```nginx
# 宝塔面板 → 网站 → 添加站点
# 域名：your-domain.com

# 配置文件：
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

---

## 🚀 1Panel部署

### 方式1：Docker编排（推荐）⭐⭐⭐⭐⭐

#### 步骤1：准备配置

```bash
# 1. 创建项目目录
mkdir -p /opt/chaoxing
cd /opt/chaoxing

# 2. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml
```

#### 步骤2：1Panel导入

```
1. 1Panel → 容器 → 编排
2. 点击"创建编排"
3. 名称：chaoxing
4. 描述：超星学习通自动化平台
5. 路径：/opt/chaoxing
6. 方式：上传docker-compose.yml 或 粘贴内容
7. 点击"确定"
```

#### 步骤3：配置环境变量

```
1. 在编排中找到chaoxing
2. 点击"编辑"
3. 添加环境变量：

# 数据库配置
POSTGRES_PASSWORD=your_secure_postgres_password
DATABASE_URL=postgresql+asyncpg://chaoxing_user:your_secure_postgres_password@postgres:5432/chaoxing_db

# Redis配置
REDIS_PASSWORD=your_secure_redis_password
REDIS_URL=redis://:your_secure_redis_password@redis:6379/0
CELERY_BROKER_URL=redis://:your_secure_redis_password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your_secure_redis_password@redis:6379/0

# 应用密钥（使用强密钥生成工具）
SECRET_KEY=your_secret_key_at_least_32_characters_long
JWT_SECRET_KEY=your_jwt_secret_key_at_least_32_chars

# 可选配置
DEBUG=False
LOG_LEVEL=INFO

4. 保存

💡 提示：密钥生成方法见下方
```

#### 生成安全密钥

```bash
# 方式1：Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方式2：OpenSSL
openssl rand -base64 32

# 方式3：在线工具
# https://generate-secret.vercel.app/32
```

#### 步骤4：启动

```
1. 点击"▶️ 启动"
2. 等待1-2分钟
3. 查看容器状态：全部Running
```

#### 步骤5：配置反向代理

```
1. 1Panel → 网站 → 创建网站
2. 域名：your-domain.com
3. 反向代理：http://127.0.0.1:8000
4. 保存
```

#### 步骤6：完成！

访问：`http://your-domain.com`

---

### 方式2：Python运行环境

#### 步骤1：安装运行环境

```
1. 1Panel → 网站 → 运行环境
2. 安装Python 3.11
```

#### 步骤2：上传项目

```bash
# 上传Release包到 /opt/1panel/apps/chaoxing/
cd /opt/1panel/apps/chaoxing/
tar -xzf chaoxing-v2.3.0-linux-x64.tar.gz
```

#### 步骤3：创建项目

```
1. 1Panel → 网站 → Python
2. 创建项目
   - 项目名：chaoxing
   - 版本：3.11
   - 项目路径：/opt/1panel/apps/chaoxing/release-package
   - 启动文件：web/backend/app.py
   - 启动命令：python web/backend/app.py
   - 端口：8000
```

#### 步骤4：安装依赖

```bash
cd /opt/1panel/apps/chaoxing/release-package
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🔧 常见问题

### Q: 前端需要安装Node.js吗？

**A**: ❌ **不需要！** Release包中的`web/frontend/dist/`已经是构建好的静态文件，直接用Nginx托管即可。

---

### Q: 如何更新版本？

#### 宝塔面板
```bash
# 1. 停止项目
宝塔面板 → Python项目管理器 → 停止

# 2. 下载新版本Release包并解压

# 3. 覆盖文件（保留data和logs目录）
cp -r release-package/* /www/wwwroot/chaoxing/release-package/

# 4. 重启项目
宝塔面板 → Python项目管理器 → 启动
```

#### 1Panel Docker
```bash
# 1. 拉取新镜像
docker pull ghcr.io/vivi141/chaoxing:latest

# 2. 1Panel → 容器 → 编排 → 重建
# 或命令行：
cd /opt/chaoxing
docker compose pull
docker compose up -d
```

---

### Q: 性能优化建议？

#### 宝塔面板
```
1. PHP/Python并发优化
   - 工作进程：4-8个（根据CPU核心数）
   - 使用gunicorn启动

2. 数据库优化
   - 启用查询缓存
   - 调整max_connections

3. Nginx优化
   - 开启gzip压缩
   - 设置缓存
   - 启用HTTP/2
```

#### 1Panel
```
1. 容器资源限制
   编排 → 编辑 → 资源限制
   - CPU: 2核
   - 内存: 2GB

2. 数据库优化
   - 使用持久化卷
   - 定期备份
```

---

### Q: 如何查看日志？

#### 宝塔面板
```bash
# Python项目日志
宝塔面板 → Python项目管理器 → 查看日志

# 或SSH查看
tail -f /www/wwwroot/chaoxing/release-package/web/backend/logs/*.log
```

#### 1Panel
```bash
# 容器日志
1Panel → 容器 → 编排 → chaoxing → 日志

# 或命令行
docker compose logs -f backend
```

---

## 🔒 安全配置

### SSL证书配置

#### 宝塔面板
```
1. 网站 → 你的站点 → SSL
2. Let's Encrypt → 申请
3. 强制HTTPS：开启
```

#### 1Panel
```
1. 网站 → 你的站点 → HTTPS
2. 申请证书（Let's Encrypt）
3. 自动续期：开启
```

### 防火墙配置

```bash
# 宝塔面板
安全 → 放行端口：
- 80 (HTTP)
- 443 (HTTPS)
- 8000 (后端，仅localhost)

# 1Panel
主机 → 防火墙 → 规则
- 同上
```

---

## 📊 性能监控

### 宝塔面板

```
1. 监控 → 系统监控
   - CPU使用率
   - 内存使用
   - 磁盘IO

2. 监控 → 进程管理
   - 查看Python进程
   - 查看Celery进程
```

### 1Panel

```
1. 主机 → 监控
   - 实时监控CPU/内存
   
2. 容器 → 容器列表
   - 查看各容器资源使用
```

---

## 🆚 宝塔 vs 1Panel 对比

| 特性 | 宝塔面板 | 1Panel | 推荐 |
|------|---------|--------|------|
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1Panel |
| **Docker支持** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1Panel |
| **Python项目** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 宝塔 |
| **社区生态** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 宝塔 |
| **开源免费** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1Panel |

### 推荐选择

| 场景 | 推荐 | 方式 |
|------|------|------|
| **新手** | 1Panel | Docker Compose |
| **小团队** | 宝塔 | Python项目管理 |
| **中大型** | 1Panel | Docker Compose |
| **多个项目** | 宝塔 | 统一管理 |

---

## 📖 完整部署示例

### 宝塔面板完整流程

```bash
# === 1. 环境准备 ===
# 宝塔面板 → 软件商店
# 安装：Python 3.11, Python项目管理器, Nginx, PostgreSQL 15

# === 2. 下载Release ===
cd /www/wwwroot
wget https://github.com/ViVi141/chaoxing/releases/download/v2.3.0/chaoxing-v2.3.0-linux-x64.tar.gz
tar -xzf chaoxing-v2.3.0-linux-x64.tar.gz
mv release-package chaoxing
cd chaoxing

# === 3. 运行安装脚本 ===
chmod +x 一键安装.sh
./一键安装.sh
# 选择：Web平台模式

# === 4. 创建数据库 ===
# 宝塔 → 数据库 → 添加
# 名称：chaoxing_db
# 用户：chaoxing_user

# === 5. 配置环境变量 ===
# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > web/backend/.env << EOF
# 数据库连接（使用宝塔创建的数据库）
DATABASE_URL=postgresql+asyncpg://chaoxing_user:你的数据库密码@localhost:5432/chaoxing_db

# 如果使用SQLite（简单模式）
# DATABASE_URL=sqlite:///./data/chaoxing.db

# 应用密钥
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Redis配置（可选）
# REDIS_URL=redis://:your_redis_password@localhost:6379/0
# CELERY_BROKER_URL=redis://:your_redis_password@localhost:6379/0

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
EOF

# === 6. 数据库迁移 ===
cd web/backend
source ../../.venv/bin/activate
alembic upgrade head

# === 7. 配置Python项目 ===
# 宝塔 → Python项目管理器 → 添加项目
# 路径：/www/wwwroot/chaoxing/web/backend
# 启动：gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# === 8. 配置网站 ===
# 宝塔 → 网站 → 添加站点
# 根目录：/www/wwwroot/chaoxing/web/frontend/dist
# 反向代理：/api → http://127.0.0.1:8000

# === 9. 启动服务 ===
# 宝塔 → Python项目管理器 → 启动

# === 10. 完成！===
# 访问：http://your-domain.com
```

---

### 1Panel完整流程（Docker）

```bash
# === 1. 创建目录 ===
mkdir -p /opt/chaoxing
cd /opt/chaoxing

# === 2. 下载配置 ===
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# === 3. 创建环境变量 ===
# 生成安全密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > .env << EOF
# 数据库配置
POSTGRES_PASSWORD=your_secure_postgres_password
DATABASE_URL=postgresql+asyncpg://chaoxing_user:your_secure_postgres_password@postgres:5432/chaoxing_db

# Redis配置
REDIS_PASSWORD=your_secure_redis_password
REDIS_URL=redis://:your_secure_redis_password@redis:6379/0
CELERY_BROKER_URL=redis://:your_secure_redis_password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your_secure_redis_password@redis:6379/0

# 应用密钥
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
EOF

# === 4. 1Panel导入 ===
# 1Panel → 容器 → 编排 → 创建编排
# 名称：chaoxing
# 路径：/opt/chaoxing
# 上传docker-compose.yml

# === 5. 启动 ===
# 点击 "▶️ 启动"

# === 6. 配置网站 ===
# 1Panel → 网站 → 创建网站
# 反向代理：http://127.0.0.1:8000

# === 7. 完成！===
# 访问：http://your-domain.com
```

---

## 🎁 宝塔/1Panel优势

### 为什么适合国内用户

| 优势 | 说明 |
|------|------|
| **中文界面** | 完全中文，易懂 |
| **可视化** | 无需命令行 |
| **一键操作** | SSL、备份、监控 |
| **生态完善** | 插件丰富 |
| **国内优化** | 速度快，支持好 |

### 你的项目特别适合

```
✅ 前端已构建 → 不需要Node.js运行环境
✅ Python后端 → 宝塔/1Panel原生支持
✅ 标准Web服务 → 完美兼容
✅ Docker支持 → 1Panel更简单
✅ 文档完整 → 易于部署
```

---

## 🔗 相关资源

- [宝塔面板官网](https://www.bt.cn)
- [1Panel官网](https://1panel.cn)
- [Docker部署指南](DOCKER_SETUP.md)
- [守护进程部署](DAEMON.md)

---

## 💡 最佳实践

### 小团队（推荐宝塔 + Python项目管理）
```
- 熟悉的界面
- Python项目管理方便
- 适合多个项目
```

### 中大团队（推荐1Panel + Docker）
```
- 现代化界面
- Docker管理更好
- 容器隔离安全
```

---

**GPL-3.0** 开源协议 | 完全免费使用

