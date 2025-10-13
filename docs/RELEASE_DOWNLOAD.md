# 📦 Release下载指南

**快速找到适合你的版本！**

---

## 🎯 我应该下载什么？

```
┌──────────────────────────────────────────┐
│  你是...                                  │
└──────────────────────────────────────────┘
         │
         ├─ Windows用户 🪟
         │  └→ chaoxing-vX.X.X-windows-x64.zip
         │     • 双击.bat即可
         │     • 5分钟完成
         │
         ├─ Mac用户 🍎
         │  └→ chaoxing-vX.X.X-macos-x64.tar.gz
         │     • 运行.sh即可
         │     • 5分钟完成
         │
         ├─ Linux服务器管理员 🐧
         │  └→ chaoxing-vX.X.X-linux-x64.tar.gz
         │     • 含守护进程
         │     • 生产环境可用
         │
         ├─ Docker用户 🐳
         │  └→ docker pull ghcr.io/vivi141/chaoxing:latest
         │     • 一行命令
         │     • 跨平台
         │
         ├─ Kubernetes运维 ☸️
         │  └→ chaoxing-vX.X.X-k8s.tar.gz
         │     • 高可用
         │     • 自动扩缩容
         │
         └─ 开发者 💻
            └→ chaoxing-vX.X.X-source.tar.gz
               • 完整源码
               • 可修改
```

---

## 📋 所有文件列表

### 🌟 推荐：平台特定包（含前端构建）

| 文件名 | 平台 | 大小 | 说明 |
|--------|------|------|------|
| `chaoxing-vX.X.X-windows-x64.zip` | Windows | ~50MB | 双击.bat安装 ⭐ |
| `chaoxing-vX.X.X-macos-x64.tar.gz` | macOS | ~50MB | 运行.sh安装 ⭐ |
| `chaoxing-vX.X.X-linux-x64.tar.gz` | Linux | ~50MB | 支持守护进程 ⭐ |

### 🐳 Docker镜像

```bash
# GitHub Container Registry（推荐国内用户）
ghcr.io/vivi141/chaoxing:latest
ghcr.io/vivi141/chaoxing:2.3.0

# Docker Hub
vivi141/chaoxing:latest
vivi141/chaoxing:2.3.0
```

**支持架构**: linux/amd64, linux/arm64

### ☸️ Kubernetes

| 文件名 | 用途 | 大小 |
|--------|------|------|
| `chaoxing-vX.X.X-k8s.tar.gz` | K8s完整配置 | ~50KB |

### 💻 开发者

| 文件名 | 用途 | 大小 |
|--------|------|------|
| `chaoxing-vX.X.X-source.tar.gz` | 完整源码（不含前端构建） | ~30MB |
| `chaoxing-vX.X.X-frontend-only.tar.gz` | 仅前端dist（用于更新） | ~5MB |

---

## 🚀 快速开始

### Windows用户

```batch
1. 下载 chaoxing-vX.X.X-windows-x64.zip
2. 解压到任意目录（如 D:\chaoxing）
3. 双击运行: 一键安装.bat
4. 选择运行模式
5. 完成！访问 http://localhost:8000
```

### Mac用户

```bash
# 1. 下载
curl -LO https://github.com/ViVi141/chaoxing/releases/download/vX.X.X/chaoxing-vX.X.X-macos-x64.tar.gz

# 2. 解压
tar -xzf chaoxing-vX.X.X-macos-x64.tar.gz
cd release-package

# 3. 安装
chmod +x 一键安装.sh
./一键安装.sh

# 4. 完成！
```

### Linux服务器

```bash
# 1. 下载
wget https://github.com/ViVi141/chaoxing/releases/download/vX.X.X/chaoxing-vX.X.X-linux-x64.tar.gz

# 2. 解压
tar -xzf chaoxing-vX.X.X-linux-x64.tar.gz
cd release-package

# 3. 安装
./一键安装.sh

# 4. 启动守护进程
./daemon_control.sh start

# 5. 完成！
```

### Docker部署

```bash
# 1. 拉取镜像
docker pull ghcr.io/vivi141/chaoxing:latest

# 2. 下载配置
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 3. 启动
docker compose up -d

# 4. 完成！访问 http://localhost:8000
```

### Kubernetes部署

```bash
# 1. 下载K8s配置
wget https://github.com/ViVi141/chaoxing/releases/download/vX.X.X/chaoxing-vX.X.X-k8s.tar.gz

# 2. 解压
tar -xzf chaoxing-vX.X.X-k8s.tar.gz
cd k8s-configs

# 3. 修改配置（secret.yaml和ingress.yaml）
nano secret.yaml

# 4. 部署
kubectl apply -f .

# 5. 查看状态
kubectl get all -n chaoxing

# 6. 完成！
```

---

## 🎓 哪个适合我？

### 个人使用（1-5人）
- ✅ **Windows**: windows-x64.zip
- ✅ **Mac**: macos-x64.tar.gz
- ✅ **Linux**: linux-x64.tar.gz

**特点**: 最简单，5分钟部署

---

### 小团队（5-20人）
- ✅ **Linux服务器**: linux-x64.tar.gz + 守护进程
- ✅ **Docker**: 推荐使用Docker Compose

**特点**: 稳定可靠，易于维护

---

### 中型团队（20-100人）
- ✅ **Docker**: 容器化部署
- ✅ **Kubernetes**: 简单K8s配置

**特点**: 环境隔离，易于扩展

---

### 大型组织（100+人）
- ✅ **Kubernetes**: 完整K8s配置 + HPA
- ✅ **监控**: Prometheus + Grafana

**特点**: 高可用，自动扩缩容

---

### 开发者
- ✅ **源码包**: source.tar.gz
- ✅ **Git克隆**: `git clone https://github.com/ViVi141/chaoxing.git`

**特点**: 可修改，可定制

---

## ❓ 常见问题

### Q: Windows包和Linux包有什么区别？

A: 
- **平台特定脚本**: Windows包含.bat，Linux包含.sh
- **守护进程**: Windows使用NSSM，Linux使用systemd
- **核心代码**: 完全相同

### Q: Docker镜像包含前端吗？

A: 是的，Docker镜像包含完整的前端构建。

### Q: K8s包需要安装什么？

A: 需要一个运行的Kubernetes集群和kubectl工具。

### Q: 源码包和平台包有什么区别？

A:
- **源码包**: 不含前端构建，需要自己npm build
- **平台包**: 包含前端构建，开箱即用

### Q: 如何更新到新版本？

A:
- **平台包**: 下载新版本，覆盖文件（保留config.ini和data目录）
- **Docker**: `docker pull新镜像` + `docker compose up -d`
- **K8s**: `kubectl set image ...`

---

## 📊 版本历史

查看 [CHANGELOG.md](docs/CHANGELOG.md) 了解所有版本更新

---

## 🔗 详细文档

- [Release选择指南](docs/RELEASE_GUIDE.md) - 详细对比
- [快速部署](docs/QUICK_DEPLOY.md) - 部署教程
- [Docker部署](docs/DOCKER_SETUP.md) - Docker完整指南
- [K8s部署](k8s/README.md) - Kubernetes指南
- [守护进程](docs/DAEMON.md) - 后台运行配置

---

## 💬 需要帮助？

- 📖 查看[FAQ](docs/FAQ.md)
- 💬 提交[Issue](https://github.com/ViVi141/chaoxing/issues)
- 📧 联系作者

---

**GPL-3.0** 开源协议 | 完全免费使用

