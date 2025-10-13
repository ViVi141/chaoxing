# Release选择指南

**版本**: v2.3.0  
**帮助用户选择最适合的部署方式**

---

## 🎯 快速选择

### 我应该下载哪个文件？

```
┌─ 你的操作系统是什么？
│
├─ Windows
│  └─ 下载: chaoxing-vX.X.X-windows-x64.zip ✅
│     • 双击.bat即可安装
│     • 包含前端构建
│     • 5分钟部署
│
├─ macOS
│  └─ 下载: chaoxing-vX.X.X-macos-x64.tar.gz ✅
│     • 运行.sh即可安装
│     • 包含前端构建
│     • 5分钟部署
│
├─ Linux服务器
│  ├─ 简单部署
│  │  └─ 下载: chaoxing-vX.X.X-linux-x64.tar.gz ✅
│  │     • 运行.sh即可安装
│  │     • 支持守护进程
│  │
│  ├─ Docker部署
│  │  └─ 命令: docker pull ghcr.io/vivi141/chaoxing:latest 🐳
│  │     • 一行命令部署
│  │     • 环境隔离
│  │
│  └─ Kubernetes集群
│     └─ 下载: chaoxing-vX.X.X-k8s.tar.gz ☸️
│        • 生产环境
│        • 高可用
│        • 自动扩缩容
│
└─ 开发者
   └─ 下载: chaoxing-vX.X.X-source.tar.gz 💻
      • 完整源码
      • 需要npm build前端
      • 可以修改代码
```

---

## 📦 所有Release文件详解

### 1. Windows用户专用 🪟

**文件**: `chaoxing-vX.X.X-windows-x64.zip`

**包含**:
- ✅ 所有Python源码
- ✅ 前端已构建（web/frontend/dist）
- ✅ 一键安装.bat脚本
- ✅ Windows守护进程脚本

**安装步骤**:
```batch
1. 解压到 D:\chaoxing
2. 双击运行: 一键安装.bat
3. 选择运行模式（命令行/Web）
4. 完成！
```

**适合**:
- ✅ Windows 10/11用户
- ✅ 个人使用
- ✅ 不想安装Node.js
- ✅ 想要最简单的部署

**不适合**:
- ❌ 需要修改前端代码
- ❌ 需要生产环境高可用

---

### 2. macOS用户专用 🍎

**文件**: `chaoxing-vX.X.X-macos-x64.tar.gz`

**包含**:
- ✅ 所有Python源码
- ✅ 前端已构建
- ✅ 一键安装.sh脚本
- ✅ macOS守护进程脚本

**安装步骤**:
```bash
tar -xzf chaoxing-vX.X.X-macos-x64.tar.gz
cd release-package
chmod +x 一键安装.sh
./一键安装.sh
```

**适合**:
- ✅ macOS用户
- ✅ 本地开发测试
- ✅ 不想安装Node.js

---

### 3. Linux服务器专用 🐧

**文件**: `chaoxing-vX.X.X-linux-x64.tar.gz`

**包含**:
- ✅ 所有Python源码
- ✅ 前端已构建
- ✅ 一键安装.sh + 守护进程脚本
- ✅ systemd/supervisor配置

**安装步骤**:
```bash
wget https://github.com/ViVi141/chaoxing/releases/download/vX.X.X/chaoxing-vX.X.X-linux-x64.tar.gz
tar -xzf chaoxing-vX.X.X-linux-x64.tar.gz
cd release-package
./一键安装.sh
./daemon_control.sh start
```

**适合**:
- ✅ Linux服务器部署
- ✅ 需要守护进程
- ✅ 中小型团队使用

**不适合**:
- ❌ 需要容器化部署
- ❌ 需要自动扩缩容

---

### 4. Docker镜像 🐳

**镜像地址**:
```bash
# GitHub Container Registry（推荐）
ghcr.io/vivi141/chaoxing:latest
ghcr.io/vivi141/chaoxing:2.3.0

# Docker Hub
vivi141/chaoxing:latest
vivi141/chaoxing:2.3.0
```

**支持架构**:
- ✅ linux/amd64 (x86_64)
- ✅ linux/arm64 (ARM64/树莓派)

**快速启动**:
```bash
# 1. 拉取镜像
docker pull ghcr.io/vivi141/chaoxing:latest

# 2. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 3. 启动
docker compose up -d
```

**适合**:
- ✅ 熟悉Docker
- ✅ 需要环境隔离
- ✅ 快速部署
- ✅ 容器化管理

**不适合**:
- ❌ 不了解Docker
- ❌ 需要K8s高级功能

---

### 5. Kubernetes配置 ☸️

**文件**: `chaoxing-vX.X.X-k8s.tar.gz`

**包含**:
- ✅ 所有K8s YAML配置
- ✅ Deployment/Service/Ingress
- ✅ HPA自动扩缩容
- ✅ PVC存储配置
- ✅ 完整部署文档

**部署步骤**:
```bash
tar -xzf chaoxing-vX.X.X-k8s.tar.gz
cd k8s-configs
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f .
```

**适合**:
- ✅ Kubernetes集群
- ✅ 生产环境
- ✅ 大规模部署
- ✅ 需要高可用
- ✅ 需要自动扩缩容

**不适合**:
- ❌ 没有K8s集群
- ❌ 小规模个人使用

---

### 6. 源码包（开发者） 💻

**文件**: `chaoxing-vX.X.X-source.tar.gz`

**包含**:
- ✅ 完整Python源码
- ✅ 前端源码（未构建）
- ❌ 不含前端dist

**安装步骤**:
```bash
tar -xzf chaoxing-vX.X.X-source.tar.gz
cd source-package

# 需要手动构建前端
cd web/frontend
npm install
npm run build
cd ../..

# 然后安装
./一键安装.sh
```

**适合**:
- ✅ 开发者
- ✅ 需要修改代码
- ✅ 需要自定义前端
- ✅ 想要最新代码

**不适合**:
- ❌ 普通用户
- ❌ 不想安装Node.js

---

### 7. 前端更新包 🎨

**文件**: `chaoxing-vX.X.X-frontend-only.tar.gz`

**包含**:
- ✅ 仅web/frontend/dist目录

**用途**:
- 用于更新前端构建
- 老用户升级

**使用方法**:
```bash
tar -xzf chaoxing-vX.X.X-frontend-only.tar.gz
cp -r dist/* /path/to/chaoxing/web/frontend/dist/
```

---

## 🎯 部署场景推荐

### 个人学习使用

**推荐**: 平台特定包（Windows/Mac/Linux）

**理由**:
- 最简单，5分钟部署
- 包含前端构建
- 一键安装脚本

**下载**:
- Windows: `windows-x64.zip`
- Mac: `macos-x64.tar.gz`
- Linux: `linux-x64.tar.gz`

---

### 小团队（5-20人）

**推荐**: Linux包 + 守护进程

**理由**:
- 稳定可靠
- 支持后台运行
- 容易维护

**下载**: `linux-x64.tar.gz`

**部署**:
```bash
./一键安装.sh
./daemon_control.sh install-systemd
./daemon_control.sh start
```

---

### 中型团队（20-100人）

**推荐**: Docker Compose

**理由**:
- 环境隔离
- 一键部署
- 容易迁移

**部署**:
```bash
docker pull ghcr.io/vivi141/chaoxing:latest
docker compose up -d
```

---

### 大型组织（100+人）

**推荐**: Kubernetes

**理由**:
- 高可用
- 自动扩缩容
- 负载均衡
- 滚动更新

**下载**: `k8s.tar.gz`

**部署**:
```bash
kubectl apply -f k8s/
```

---

## 📊 对比表

| 特性 | Windows包 | Mac包 | Linux包 | Docker | K8s | 源码包 |
|------|----------|-------|---------|--------|-----|--------|
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **部署时间** | 5分钟 | 5分钟 | 5分钟 | 4分钟 | 10分钟 | 15分钟 |
| **需要npm** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **守护进程** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **环境隔离** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **自动扩缩** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **高可用** | ❌ | ❌ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ❌ |
| **适合人数** | 1-5 | 1-5 | 5-50 | 10-100 | 100+ | 开发 |

---

## 🎓 学习建议

### 新手
1. 下载对应平台包（Windows/Mac/Linux）
2. 运行一键安装脚本
3. 先使用命令行模式熟悉

### 进阶用户
1. 尝试Docker部署
2. 配置反向代理（Nginx）
3. 设置守护进程

### 高级用户
1. Kubernetes集群部署
2. CI/CD自动化
3. 监控和日志系统
4. 修改源码自定义

---

## 🔗 相关文档

- [快速部署](QUICK_DEPLOY.md)
- [Docker部署](DOCKER_SETUP.md)
- [K8s部署](../k8s/README.md)
- [守护进程](DAEMON.md)
- [完整文档](INDEX.md)

---

**还有疑问？** 查看 [FAQ](FAQ.md) 或提交 [Issue](https://github.com/ViVi141/chaoxing/issues)

**GPL-3.0** 开源协议 | 完全免费使用

