# 守护进程部署指南

**版本**: v2.2.3  
**更新**: 2025-10-13

本指南提供多种方式运行Chaoxing服务，防止关闭终端后服务停止。

---

## 📋 目录

- [快速开始](#快速开始)
- [方式一：systemd（推荐Linux）](#方式一systemd推荐linux)
- [方式二：supervisor（通用方案）](#方式二supervisor通用方案)
- [方式三：screen/tmux（临时会话）](#方式三screentmux临时会话)
- [方式四：nohup（最简单）](#方式四nohup最简单)
- [方式五：Docker（容器化）](#方式五docker容器化)
- [生产环境建议](#生产环境建议)
- [故障排查](#故障排查)

---

## 🚀 快速开始

### 使用统一管理脚本（推荐）

```bash
# 赋予执行权限
chmod +x daemon_control.sh

# 查看帮助
./daemon_control.sh help

# 启动服务（自动选择最佳方式）
./daemon_control.sh start

# 查看状态
./daemon_control.sh status

# 停止服务
./daemon_control.sh stop

# 查看日志
./daemon_control.sh logs backend
./daemon_control.sh logs celery
```

---

## 方式一：systemd（推荐Linux）

### ✅ 优点
- 系统级管理，开机自启
- 自动重启机制
- 完善的日志管理
- 资源限制和安全控制

### 适用系统
- Ubuntu 16.04+
- Debian 8+
- CentOS 7+
- Fedora
- 其他使用systemd的Linux发行版

### 安装步骤

#### 1. 修改服务文件

编辑以下文件，修改项目路径和用户：

```bash
# 编辑后端服务
sudo nano web/backend/chaoxing-backend.service

# 编辑Celery服务
sudo nano web/backend/chaoxing-celery.service
```

**必须修改的内容**：
```ini
# 修改用户（改为你的用户名或www-data）
User=你的用户名
Group=你的用户名

# 修改工作目录（改为实际项目路径）
WorkingDirectory=/你的实际路径/chaoxing/web/backend

# 修改环境变量中的路径
Environment="PATH=/你的实际路径/chaoxing/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/你的实际路径/chaoxing"

# 修改ExecStart中的路径
ExecStart=/你的实际路径/chaoxing/.venv/bin/gunicorn ...
```

#### 2. 安装服务

```bash
# 使用脚本自动安装
./daemon_control.sh install-systemd

# 或手动安装
sudo cp web/backend/chaoxing-backend.service /etc/systemd/system/
sudo cp web/backend/chaoxing-celery.service /etc/systemd/system/

# 重载systemd配置
sudo systemctl daemon-reload
```

#### 3. 启动服务

```bash
# 启动服务
sudo systemctl start chaoxing-backend
sudo systemctl start chaoxing-celery

# 设置开机自启
sudo systemctl enable chaoxing-backend
sudo systemctl enable chaoxing-celery

# 查看状态
sudo systemctl status chaoxing-backend
sudo systemctl status chaoxing-celery
```

#### 4. 管理命令

```bash
# 停止服务
sudo systemctl stop chaoxing-backend
sudo systemctl stop chaoxing-celery

# 重启服务
sudo systemctl restart chaoxing-backend
sudo systemctl restart chaoxing-celery

# 查看日志
sudo journalctl -u chaoxing-backend -f
sudo journalctl -u chaoxing-celery -f

# 查看最近50行日志
sudo journalctl -u chaoxing-backend -n 50

# 查看今天的日志
sudo journalctl -u chaoxing-backend --since today

# 取消开机自启
sudo systemctl disable chaoxing-backend
```

---

## 方式二：supervisor（通用方案）

### ✅ 优点
- 跨平台（Linux/macOS）
- 统一的Web管理界面
- 进程组管理
- 自动重启机制

### 安装supervisor

```bash
# Ubuntu/Debian
sudo apt install supervisor

# CentOS/RHEL
sudo yum install supervisor

# 使用pip安装（通用）
pip install supervisor
```

### 配置步骤

#### 1. 修改配置文件

```bash
# 编辑配置文件
nano web/supervisor.conf
```

**必须修改的内容**：
```ini
# 修改项目路径
directory=/你的实际路径/chaoxing/web/backend

# 修改启动命令中的路径
command=/你的实际路径/chaoxing/.venv/bin/gunicorn ...

# 修改环境变量
environment=PYTHONPATH="/你的实际路径/chaoxing",PATH="/你的实际路径/chaoxing/.venv/bin:%(ENV_PATH)s"

# 修改运行用户
user=你的用户名

# 修改日志路径（确保目录存在）
stdout_logfile=/你的实际路径/chaoxing/web/backend/logs/supervisor_backend_stdout.log
```

#### 2. 安装配置

```bash
# 使用脚本安装
./daemon_control.sh install-supervisor

# 或手动安装
sudo cp web/supervisor.conf /etc/supervisor/conf.d/chaoxing.conf

# 重新读取配置
sudo supervisorctl reread
sudo supervisorctl update
```

#### 3. 管理命令

```bash
# 启动所有服务
sudo supervisorctl start chaoxing:*

# 启动单个服务
sudo supervisorctl start chaoxing:chaoxing-backend
sudo supervisorctl start chaoxing:chaoxing-celery

# 停止服务
sudo supervisorctl stop chaoxing:*

# 重启服务
sudo supervisorctl restart chaoxing:*

# 查看状态
sudo supervisorctl status

# 查看日志（实时）
sudo supervisorctl tail -f chaoxing:chaoxing-backend
sudo supervisorctl tail -f chaoxing:chaoxing-celery

# 重新加载配置（修改配置文件后）
sudo supervisorctl reread
sudo supervisorctl update
```

### Web管理界面（可选）

在 `/etc/supervisor/supervisord.conf` 中启用：

```ini
[inet_http_server]
port=*:9001
username=admin
password=your_password
```

然后访问：`http://your_server:9001`

---

## 方式三：screen/tmux（临时会话）

### ✅ 优点
- 快速简单
- 适合开发和测试
- 可以随时连接查看

### ❌ 缺点
- 不适合生产环境
- 没有自动重启
- 会话可能意外关闭

### screen方式

#### 1. 安装screen

```bash
# Ubuntu/Debian
sudo apt install screen

# CentOS/RHEL
sudo yum install screen

# macOS
brew install screen
```

#### 2. 启动服务

```bash
# 使用脚本启动
./daemon_control.sh start screen

# 或手动启动
cd web/backend

# 启动后端（在screen会话中）
screen -dmS chaoxing-backend bash -c "source ../../.venv/bin/activate && python app.py"

# 启动Celery（在screen会话中）
screen -dmS chaoxing-celery bash -c "source ../../.venv/bin/activate && celery -A celery_app worker --loglevel=info"
```

#### 3. 管理命令

```bash
# 查看所有会话
screen -ls

# 连接到会话
screen -r chaoxing-backend
screen -r chaoxing-celery

# 退出会话（不关闭）
# 按 Ctrl+A, 然后按 D

# 关闭会话
screen -S chaoxing-backend -X quit
screen -S chaoxing-celery -X quit

# 使用脚本停止
./daemon_control.sh stop screen
```

### tmux方式

```bash
# 安装tmux
sudo apt install tmux

# 创建会话并启动后端
tmux new -d -s chaoxing-backend "cd web/backend && source ../../.venv/bin/activate && python app.py"

# 创建会话并启动Celery
tmux new -d -s chaoxing-celery "cd web/backend && source ../../.venv/bin/activate && celery -A celery_app worker --loglevel=info"

# 查看会话
tmux ls

# 连接到会话
tmux attach -t chaoxing-backend

# 退出会话（不关闭）
# 按 Ctrl+B, 然后按 D

# 关闭会话
tmux kill-session -t chaoxing-backend
tmux kill-session -t chaoxing-celery
```

---

## 方式四：nohup（最简单）

### ✅ 优点
- 最简单，无需额外安装
- 立即可用

### ❌ 缺点
- 没有进程管理功能
- 没有自动重启
- 日志管理简陋

### 使用方法

```bash
# 使用脚本启动
./daemon_control.sh start nohup

# 或手动启动
cd web/backend

# 启动后端
nohup ../../.venv/bin/python app.py > logs/nohup_backend.log 2>&1 &
echo $! > logs/backend.pid

# 启动Celery
nohup ../../.venv/bin/celery -A celery_app worker --loglevel=info > logs/nohup_celery.log 2>&1 &
echo $! > logs/celery.pid

# 查看进程
ps aux | grep python
ps aux | grep celery

# 停止服务
kill $(cat logs/backend.pid)
kill $(cat logs/celery.pid)

# 或使用脚本停止
./daemon_control.sh stop nohup

# 查看日志
tail -f logs/nohup_backend.log
tail -f logs/nohup_celery.log
```

---

## 方式五：Docker（容器化）

### ✅ 优点
- 环境隔离
- 一键部署
- 跨平台
- 易于扩展

### 使用方法

项目已包含Docker配置，参见：
- `web/docker-compose.yml`（完整模式）
- `web/docker-compose.simple.yml`（简单模式）

```bash
# 简单模式（SQLite + 文件队列）
cd web
docker-compose -f docker-compose.simple.yml up -d

# 完整模式（PostgreSQL + Redis）
cd web
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f celery

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

## 🏭 生产环境建议

### 架构建议

```
[Nginx] → [Gunicorn + FastAPI] → [PostgreSQL]
             ↓
        [Celery Worker] → [Redis]
```

### 推荐配置

1. **Web服务器**：Nginx反向代理
   - 处理静态文件
   - SSL/TLS终止
   - 负载均衡

2. **应用服务器**：Gunicorn + Uvicorn Worker
   - 多进程部署
   - 自动重启
   - 超时控制

3. **任务队列**：Celery + Redis
   - 异步任务处理
   - 任务重试机制
   - 结果存储

4. **进程管理**：systemd（Linux）或supervisor
   - 服务监控
   - 自动重启
   - 日志管理

5. **数据库**：PostgreSQL
   - 数据持久化
   - 事务支持
   - 并发控制

### Nginx配置示例

创建 `/etc/nginx/sites-available/chaoxing`：

```nginx
upstream chaoxing_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 静态文件
    location /static {
        alias /opt/chaoxing/web/frontend/dist/assets;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 前端
    location / {
        root /opt/chaoxing/web/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api {
        proxy_pass http://chaoxing_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # 日志
    access_log /var/log/nginx/chaoxing_access.log;
    error_log /var/log/nginx/chaoxing_error.log;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/chaoxing /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 故障排查

### 服务无法启动

#### 1. 检查端口占用

```bash
# 检查8000端口
sudo lsof -i :8000
sudo netstat -tlnp | grep 8000

# 如果被占用，杀死进程
sudo kill -9 <PID>
```

#### 2. 检查权限

```bash
# 确保日志目录存在且有写权限
mkdir -p web/backend/logs
chmod 755 web/backend/logs

# 检查文件所有者
ls -l web/backend/

# 修改所有者（如果需要）
sudo chown -R your_user:your_user .
```

#### 3. 检查Python环境

```bash
# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
pip list

# 重新安装依赖
pip install -r requirements.txt
```

### 服务运行异常

#### 1. 查看日志

```bash
# systemd日志
sudo journalctl -u chaoxing-backend -n 100
sudo journalctl -u chaoxing-celery -n 100

# supervisor日志
sudo supervisorctl tail chaoxing:chaoxing-backend
tail -f web/backend/logs/supervisor_backend_stderr.log

# 应用日志
tail -f web/backend/logs/chaoxing_*.log
```

#### 2. 测试手动启动

```bash
cd web/backend
source ../../.venv/bin/activate

# 测试后端
python app.py

# 测试Celery
celery -A celery_app worker --loglevel=debug
```

### 数据库连接问题

```bash
# 检查数据库文件
ls -l web/backend/data/chaoxing.db

# 检查PostgreSQL（如果使用）
sudo systemctl status postgresql
psql -U your_user -d chaoxing -c "SELECT 1;"

# 检查Redis（如果使用）
redis-cli ping
```

### 性能问题

```bash
# 检查系统资源
htop
free -h
df -h

# 检查进程
ps aux | grep python
ps aux | grep celery

# 优化worker数量（根据CPU核心数）
# 编辑服务文件，修改--workers参数
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志获取错误信息
2. 搜索 [Issues](https://github.com/ViVi141/chaoxing/issues)
3. 提交新的Issue，包含：
   - 操作系统和版本
   - Python版本
   - 错误日志
   - 复现步骤

---

## 📚 相关文档

- [快速开始](QUICK_START.md)
- [配置指南](CONFIGURATION.md)
- [常见问题](FAQ.md)
- [架构说明](ARCHITECTURE.md)

---

**GPL-3.0** 开源协议 | 完全免费使用

