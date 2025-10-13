# 快速部署指南

**版本**: v2.3.0  
**适用**: 普通用户快速部署

---

## 🚀 三种部署方式

### 方式1：Release版本（最简单）⭐⭐⭐⭐⭐

**优点**：
- ✅ 无需npm，前端已预编译
- ✅ 解压即用
- ✅ 文件小，下载快

**步骤**：

#### Linux/macOS

```bash
# 1. 下载最新Release
wget https://github.com/ViVi141/chaoxing/releases/latest/download/chaoxing-v2.3.0-full.tar.gz

# 2. 解压
tar -xzf chaoxing-v2.3.0-full.tar.gz
cd release-package

# 3. 运行一键安装
chmod +x 一键安装.sh
./一键安装.sh
```

#### Windows

```cmd
1. 访问 https://github.com/ViVi141/chaoxing/releases/latest
2. 下载 chaoxing-vX.X.X-full.zip
3. 解压到任意目录
4. 双击运行: 一键安装.bat
```

---

### 方式2：Git克隆（开发者）⭐⭐⭐

**优点**：
- ✅ 可以获取最新代码
- ✅ 可以自己修改

**步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/ViVi141/chaoxing.git
cd chaoxing

# 2. 运行一键安装
# Linux/macOS
chmod +x 一键安装.sh
./一键安装.sh

# Windows
一键安装.bat
```

---

### 方式3：Docker镜像（最省事）⭐⭐⭐⭐⭐

**优点**：
- ✅ 预构建镜像，无需编译
- ✅ 多架构支持（amd64/arm64）
- ✅ 环境隔离
- ✅ 一键启动

**步骤**：

#### 方式A：直接使用预构建镜像（推荐）

```bash
# 1. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 2. 修改使用预构建镜像
# 编辑docker-compose.yml，将backend的build改为：
#   image: vivi141/chaoxing:latest  # Docker Hub
#   # 或
#   image: ghcr.io/vivi141/chaoxing:latest  # GitHub

# 3. 启动
docker compose up -d

# 4. 访问
http://localhost:8000
```

#### 方式B：从源码构建

```bash
# 1. 克隆仓库
git clone https://github.com/ViVi141/chaoxing.git
cd chaoxing/web

# 2. 完整模式（PostgreSQL + Redis）
docker compose up -d

# 3. 访问
http://localhost:8000
```

---

## 📦 Release下载说明

### 完整包 vs 前端包 vs Docker镜像

| 文件/镜像 | 大小 | 用途 | 适合 |
|------|------|------|------|
| **Docker镜像** | ~200MB | 预构建容器镜像 | 生产环境 |
| **chaoxing-vX.X.X-full.tar.gz** | ~50MB | 所有文件+前端构建 | 新用户 |
| **chaoxing-vX.X.X-frontend-only.tar.gz** | ~5MB | 仅前端dist | 老用户更新 |

### Docker镜像地址

**Docker Hub**（国内可能较慢）:
```bash
docker pull vivi141/chaoxing:latest      # 最新版
docker pull vivi141/chaoxing:2.3.0       # 指定版本
```

**GitHub Container Registry**（推荐）:
```bash
docker pull ghcr.io/vivi141/chaoxing:latest
docker pull ghcr.io/vivi141/chaoxing:2.3.0
```

**支持架构**:
- ✅ linux/amd64（x86_64）
- ✅ linux/arm64（ARM64，如树莓派）

### 下载地址

**最新版本**：
```
https://github.com/ViVi141/chaoxing/releases/latest
```

**指定版本**：
```
https://github.com/ViVi141/chaoxing/releases/tag/v2.3.0
```

---

## 🎯 普通用户推荐流程

### Windows用户（最简单）

```
1. 下载Release完整包（.zip）
   ↓
2. 解压到 D:\chaoxing
   ↓
3. 双击运行: 一键安装.bat
   ↓
4. 选择运行模式（命令行/Web）
   ↓
5. 完成！
```

### Linux服务器部署

```bash
# 1. 下载并解压
wget https://github.com/ViVi141/chaoxing/releases/latest/download/chaoxing-full.tar.gz
tar -xzf chaoxing-full.tar.gz
cd release-package

# 2. 安装
./一键安装.sh

# 3. 守护进程运行
./daemon_control.sh start

# 4. 设置开机自启（可选）
./daemon_control.sh install-systemd
```

---

## ⚡ 超快速部署（1分钟）

### 命令行模式

```bash
# 一条命令完成所有步骤
curl -fsSL https://raw.githubusercontent.com/ViVi141/chaoxing/main/一键安装.sh | bash
```

### Web平台模式（Docker）

```bash
# 一条命令启动完整Web平台
git clone --depth=1 https://github.com/ViVi141/chaoxing.git && \
cd chaoxing/web && \
docker compose up -d

# 访问 http://localhost:8000
```

---

## 📝 部署后配置

### 命令行模式

编辑 `config.ini`：
```ini
[common]
username = 你的手机号
password = 你的密码
speed = 1.5

[tiku]
provider = AI
ai_key = 你的API密钥
```

### Web平台模式

1. 访问 `http://localhost:8000`
2. 注册账号（首个注册用户自动成为管理员）
3. 登录后配置超星账号和题库

---

## 🔧 常见问题

### Q: Release包在哪下载？

A: https://github.com/ViVi141/chaoxing/releases/latest

### Q: 需要安装什么？

A: 
- **必须**：Python 3.10+
- **可选**：Node.js（仅源码安装需要）
- **可选**：Docker（Docker部署需要）

### Q: Docker镜像、Release包、源码有什么区别？

A:
- **Docker镜像**：预构建容器，一键启动，适合生产环境
- **Release包**：前端已构建，解压即用，适合普通用户
- **源码**：需要npm build前端，适合开发者

### Q: 如何更新到新版本？

A:
```bash
# 下载新版本Release
# 解压并覆盖旧文件（保留config.ini和data目录）
# 重启服务
```

---

## 🎁 自动化功能

### Release自动构建

当推送新tag时，GitHub Actions自动：

1. ✅ 构建前端生产版本
2. ✅ 打包所有文件
3. ✅ 构建Docker镜像（多架构）
4. ✅ 推送到Docker Hub + GitHub Container Registry
5. ✅ 创建GitHub Release
6. ✅ 上传预编译包

**触发方式**：
```bash
git tag v2.3.0
git push origin v2.3.0
```

### 用户获益

- ✅ **Docker镜像**：预构建，一键部署，支持ARM64
- ✅ 无需安装Node.js
- ✅ 无需手动构建前端
- ✅ 下载即用，节省时间
- ✅ 减少83%部署时间（30分钟→5分钟）

---

## 📊 部署时间对比

| 方式 | 下载 | 安装 | 配置 | 总计 |
|------|------|------|------|------|
| **Docker镜像** | 2分钟 | 1分钟 | 1分钟 | **4分钟** ⭐ |
| **Release包** | 1分钟 | 2分钟 | 2分钟 | **5分钟** |
| 源码安装 | 2分钟 | 5分钟 | 2分钟 | 9分钟 |
| Docker自构建 | 1分钟 | 5分钟 | 1分钟 | 7分钟 |

---

## 🔗 相关文档

- [一键安装脚本](../一键安装.sh) - Linux/macOS
- [一键安装脚本](../一键安装.bat) - Windows
- [守护进程部署](DAEMON.md) - 生产环境
- [完整文档](INDEX.md) - 所有文档

---

**GPL-3.0** 开源协议 | 完全免费使用

