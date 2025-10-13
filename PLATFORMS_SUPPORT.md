# 🌍 全平台支持矩阵

**版本**: v2.3.0  
**最后更新**: 2025-10-13

---

## 📦 Release包类型总览

| # | 类型 | 文件名格式 | 平台 | 大小 | 包含前端 | 用途 |
|---|------|----------|------|------|----------|------|
| 1 | Windows包 | `chaoxing-vX.X.X-windows-x64.zip` | Windows 10+ | ~50MB | ✅ | 个人/小团队 |
| 2 | macOS包 | `chaoxing-vX.X.X-macos-x64.tar.gz` | macOS 10.15+ | ~50MB | ✅ | 个人/开发 |
| 3 | Linux包 | `chaoxing-vX.X.X-linux-x64.tar.gz` | Linux(任意发行版) | ~50MB | ✅ | 服务器/生产 |
| 4 | Docker镜像 | `ghcr.io/vivi141/chaoxing:vX.X.X` | 多平台 | ~200MB | ✅ | 容器化部署 |
| 5 | K8s配置 | `chaoxing-vX.X.X-k8s.tar.gz` | Kubernetes | ~50KB | - | 大规模生产 |
| 6 | 源码包 | `chaoxing-vX.X.X-source.tar.gz` | 跨平台 | ~30MB | ❌ | 开发/定制 |
| 7 | 前端包 | `chaoxing-vX.X.X-frontend-only.tar.gz` | 跨平台 | ~5MB | ✅ | 更新前端 |

---

## 🖥️ 操作系统支持

### Windows 🪟

| 版本 | 支持 | 推荐 | Release包 |
|------|------|------|-----------|
| Windows 11 | ✅ | ⭐⭐⭐⭐⭐ | windows-x64.zip |
| Windows 10 | ✅ | ⭐⭐⭐⭐⭐ | windows-x64.zip |
| Windows Server 2022 | ✅ | ⭐⭐⭐⭐ | windows-x64.zip |
| Windows Server 2019 | ✅ | ⭐⭐⭐⭐ | windows-x64.zip |
| Windows 8.1 | ⚠️ | ⭐⭐⭐ | windows-x64.zip |

**安装方式**:
- ✅ 一键安装.bat
- ✅ 守护进程（NSSM）
- ✅ 任务计划程序

---

### macOS 🍎

| 版本 | 支持 | 推荐 | Release包 |
|------|------|------|-----------|
| macOS Sonoma (14) | ✅ | ⭐⭐⭐⭐⭐ | macos-x64.tar.gz |
| macOS Ventura (13) | ✅ | ⭐⭐⭐⭐⭐ | macos-x64.tar.gz |
| macOS Monterey (12) | ✅ | ⭐⭐⭐⭐ | macos-x64.tar.gz |
| macOS Big Sur (11) | ✅ | ⭐⭐⭐ | macos-x64.tar.gz |
| macOS Catalina (10.15) | ✅ | ⭐⭐⭐ | macos-x64.tar.gz |

**架构支持**:
- ✅ Intel (x86_64)
- ⚠️ Apple Silicon (M1/M2) - 通过Rosetta 2

**安装方式**:
- ✅ 一键安装.sh
- ✅ launchd守护进程
- ✅ Docker

---

### Linux 🐧

| 发行版 | 版本 | 支持 | 推荐 | Release包 |
|--------|------|------|------|-----------|
| Ubuntu | 20.04+ | ✅ | ⭐⭐⭐⭐⭐ | linux-x64.tar.gz |
| Debian | 11+ | ✅ | ⭐⭐⭐⭐⭐ | linux-x64.tar.gz |
| CentOS | 8+ | ✅ | ⭐⭐⭐⭐ | linux-x64.tar.gz |
| Rocky Linux | 8+ | ✅ | ⭐⭐⭐⭐ | linux-x64.tar.gz |
| AlmaLinux | 8+ | ✅ | ⭐⭐⭐⭐ | linux-x64.tar.gz |
| Fedora | 35+ | ✅ | ⭐⭐⭐⭐ | linux-x64.tar.gz |
| Arch Linux | Rolling | ✅ | ⭐⭐⭐ | linux-x64.tar.gz |

**架构支持**:
- ✅ x86_64 (amd64)
- ✅ ARM64 (Docker镜像)
- ⚠️ ARM32 - 需要从源码编译

**安装方式**:
- ✅ 一键安装.sh
- ✅ systemd守护进程
- ✅ supervisor
- ✅ Docker
- ✅ K8s

---

## 🐳 容器化支持

### Docker

| 架构 | 支持 | 镜像标签 |
|------|------|----------|
| linux/amd64 | ✅ | :latest, :2.3.0 |
| linux/arm64 | ✅ | :latest, :2.3.0 |
| linux/arm/v7 | ❌ | - |

**镜像源**:
- ✅ GitHub Container Registry (ghcr.io)
- ✅ Docker Hub

**基础镜像**: `python:3.11-slim`

---

### Kubernetes ☸️

| K8s版本 | 支持 | 测试 |
|---------|------|------|
| 1.28+ | ✅ | ✅ |
| 1.27 | ✅ | ✅ |
| 1.26 | ✅ | ⚠️ |
| 1.25 | ✅ | ⚠️ |
| 1.20-1.24 | ⚠️ | ❌ |

**包含配置**:
- ✅ Deployment
- ✅ Service
- ✅ Ingress
- ✅ ConfigMap
- ✅ Secret
- ✅ PVC
- ✅ HPA (自动扩缩容)

**支持的Ingress Controller**:
- ✅ Nginx Ingress
- ✅ Traefik
- ⚠️ HAProxy (需要修改)

---

## 🏗️ 架构支持

### CPU架构

| 架构 | 平台包 | Docker | 说明 |
|------|--------|--------|------|
| x86_64 (amd64) | ✅ | ✅ | 全面支持 |
| ARM64 (aarch64) | ⚠️ | ✅ | Docker支持 |
| ARM32 | ❌ | ❌ | 需源码编译 |

### Python版本

| Python版本 | 支持 | 推荐 | 测试 |
|-----------|------|------|------|
| 3.12 | ✅ | ⭐⭐⭐⭐⭐ | ✅ |
| 3.11 | ✅ | ⭐⭐⭐⭐⭐ | ✅ |
| 3.10 | ✅ | ⭐⭐⭐⭐ | ✅ |
| 3.9 | ⚠️ | ⭐⭐⭐ | ❌ |
| 3.8 | ❌ | - | ❌ |

---

## 📊 功能支持矩阵

| 功能 | Windows | macOS | Linux | Docker | K8s |
|------|---------|-------|-------|--------|-----|
| 命令行模式 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Web平台 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 守护进程 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 自动重启 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 开机自启 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 自动扩缩容 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 负载均衡 | ❌ | ❌ | ⚠️ | ⚠️ | ✅ |
| 高可用 | ❌ | ❌ | ⚠️ | ⚠️ | ✅ |
| 滚动更新 | ❌ | ❌ | ❌ | ⚠️ | ✅ |

---

## 🎯 使用场景推荐

### 个人学习（1人）

**推荐**: 平台特定包

| 平台 | Release包 | 部署时间 | 难度 |
|------|-----------|----------|------|
| Windows | windows-x64.zip | 5分钟 | ⭐ |
| macOS | macos-x64.tar.gz | 5分钟 | ⭐ |
| Linux | linux-x64.tar.gz | 5分钟 | ⭐ |

---

### 小团队（5-20人）

**推荐**: Linux包 + 守护进程 或 Docker

| 方案 | 部署时间 | 维护难度 | 可靠性 |
|------|----------|----------|--------|
| Linux包 | 5分钟 | ⭐⭐ | ⭐⭐⭐⭐ |
| Docker | 4分钟 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

### 中型团队（20-100人）

**推荐**: Docker Compose 或 简单K8s

| 方案 | 部署时间 | 维护难度 | 可靠性 | 可扩展性 |
|------|----------|----------|--------|----------|
| Docker Compose | 5分钟 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| K8s (单副本) | 10分钟 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

### 大型组织（100+人）

**推荐**: Kubernetes + HPA

| 方案 | 部署时间 | 维护难度 | 可靠性 | 可扩展性 | 高可用 |
|------|----------|----------|--------|----------|--------|
| K8s完整方案 | 20分钟 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |

---

## 🔗 相关资源

### 下载
- [GitHub Releases](https://github.com/ViVi141/chaoxing/releases)
- [Docker Hub](https://hub.docker.com/r/vivi141/chaoxing)
- [GitHub Container Registry](https://github.com/ViVi141/chaoxing/pkgs/container/chaoxing)

### 文档
- [Release下载指南](RELEASE_DOWNLOAD.md)
- [Release选择指南](docs/RELEASE_GUIDE.md)
- [快速部署](docs/QUICK_DEPLOY.md)
- [Docker部署](docs/DOCKER_SETUP.md)
- [K8s部署](k8s/README.md)

---

**说明**:
- ✅ = 完全支持
- ⚠️ = 部分支持或需要额外配置
- ❌ = 不支持
- ⭐ = 推荐程度（越多越推荐）

**GPL-3.0** 开源协议 | 完全免费使用

