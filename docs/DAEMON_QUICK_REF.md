# 守护进程快速参考

## 🚀 快速使用

### Linux/macOS

```bash
# 赋予执行权限
chmod +x daemon_control.sh

# 启动服务（自动选择最佳方式）
./daemon_control.sh start

# 查看状态
./daemon_control.sh status

# 停止服务
./daemon_control.sh stop

# 查看日志
./daemon_control.sh logs backend
```

### Windows

```cmd
# 启动服务
daemon_control.bat start

# 查看状态
daemon_control.bat status

# 停止服务
daemon_control.bat stop
```

---

## 📋 方式选择

| 方式 | 适用系统 | 特点 | 推荐度 |
|------|---------|------|--------|
| **systemd** | Linux (Ubuntu/CentOS/Debian) | 系统级、自动重启、开机自启 | ⭐⭐⭐⭐⭐ |
| **supervisor** | Linux/macOS | 跨平台、Web管理界面 | ⭐⭐⭐⭐ |
| **Docker** | 全平台 | 容器化、易于扩展 | ⭐⭐⭐⭐ |
| **screen** | Linux/macOS | 简单快速、适合开发 | ⭐⭐⭐ |
| **nohup** | Linux/macOS | 最简单、无需安装 | ⭐⭐ |
| **NSSM** | Windows | Windows服务 | ⭐⭐⭐⭐ |

---

## 🎯 按场景选择

### 开发环境
```bash
# 使用screen（快速、临时）
./daemon_control.sh start screen
```

### 生产环境（Linux）
```bash
# 使用systemd（推荐）
./daemon_control.sh install-systemd
sudo systemctl enable chaoxing-backend
sudo systemctl start chaoxing-backend
sudo systemctl start chaoxing-celery
```

### 生产环境（跨平台）
```bash
# 使用Docker
cd web
docker-compose up -d
```

### Windows服务器
```cmd
# 使用NSSM
daemon_control.bat install-nssm
# 按提示安装Windows服务
```

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `daemon_control.sh` | Linux/macOS统一管理脚本 |
| `daemon_control.bat` | Windows统一管理脚本 |
| `web/backend/chaoxing-backend.service` | systemd后端服务配置 |
| `web/backend/chaoxing-celery.service` | systemd Celery服务配置 |
| `web/supervisor.conf` | supervisor配置文件 |
| `web/docker-compose.yml` | Docker完整模式配置 |
| `web/docker-compose.simple.yml` | Docker简单模式配置 |

---

## 🔍 常用命令

### systemd
```bash
# 启动
sudo systemctl start chaoxing-backend
sudo systemctl start chaoxing-celery

# 停止
sudo systemctl stop chaoxing-backend

# 重启
sudo systemctl restart chaoxing-backend

# 查看状态
sudo systemctl status chaoxing-backend

# 查看日志
sudo journalctl -u chaoxing-backend -f

# 开机自启
sudo systemctl enable chaoxing-backend
```

### supervisor
```bash
# 启动
sudo supervisorctl start chaoxing:*

# 停止
sudo supervisorctl stop chaoxing:*

# 重启
sudo supervisorctl restart chaoxing:*

# 查看状态
sudo supervisorctl status

# 查看日志
sudo supervisorctl tail -f chaoxing:chaoxing-backend

# 重新加载配置
sudo supervisorctl reread && sudo supervisorctl update
```

### Docker
```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f celery

# 重新构建
docker-compose up -d --build
```

### screen
```bash
# 查看会话
screen -ls

# 连接会话
screen -r chaoxing-backend

# 退出会话（不关闭）
Ctrl+A, D

# 关闭会话
screen -S chaoxing-backend -X quit
```

---

## ⚠️ 注意事项

1. **端口冲突**：确保8000端口未被占用
2. **权限问题**：Linux确保有写权限到日志目录
3. **路径配置**：修改服务文件中的实际路径
4. **用户配置**：修改服务运行用户（不要用root）
5. **日志管理**：定期清理日志文件
6. **资源监控**：生产环境监控CPU、内存使用

---

## 📖 完整文档

查看 [docs/DAEMON.md](docs/DAEMON.md) 获取详细说明和故障排查。

---

**GPL-3.0** 开源协议 | 完全免费使用

