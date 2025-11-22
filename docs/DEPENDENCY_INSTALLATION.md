# 依赖安装指南

## 问题说明

虽然GitHub CI/CD和打包测试通过，但在服务器安装时可能出现依赖缺失问题。这通常是因为：

1. **系统级依赖缺失**：某些Python包需要系统级库才能编译安装
2. **不同Linux发行版的差异**：Ubuntu/Debian和CentOS/RHEL的包管理器不同
3. **编译工具缺失**：缺少gcc、python3-dev等编译工具

## 解决方案

### 方法1：使用一键安装脚本（推荐）

一键安装脚本已自动处理系统依赖安装：

```bash
# Linux/macOS
./一键安装.sh

# Windows
一键安装.bat
```

脚本会自动：
1. 检测Linux发行版
2. 安装所需的系统级依赖
3. 安装Python依赖
4. 验证依赖安装

### 方法2：手动安装系统依赖

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    python3-pip \
    python3-venv \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    curl \
    wget \
    git
```

#### CentOS/RHEL/Fedora

```bash
# 使用yum (CentOS 7)
sudo yum install -y \
    gcc \
    gcc-c++ \
    make \
    python3-devel \
    python3-pip \
    libffi-devel \
    openssl-devel \
    libxml2-devel \
    libxslt-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    zlib-devel \
    curl \
    wget \
    git

# 或使用dnf (CentOS 8+/Fedora)
sudo dnf install -y \
    gcc \
    gcc-c++ \
    make \
    python3-devel \
    python3-pip \
    libffi-devel \
    openssl-devel \
    libxml2-devel \
    libxslt-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    zlib-devel \
    curl \
    wget \
    git
```

#### 使用系统依赖安装脚本

```bash
# 基础安装
bash scripts/install_system_deps.sh

# 包含PostgreSQL支持
bash scripts/install_system_deps.sh with-postgresql
```

### 方法3：安装Python依赖

安装系统依赖后，安装Python包：

```bash
# 升级pip和构建工具
pip install --upgrade pip setuptools wheel

# 安装项目依赖
pip install -r requirements.txt
```

### 方法4：使用国内镜像源（可选）

如果网络较慢，可以使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 验证依赖安装

安装完成后，运行验证脚本：

```bash
python scripts/verify_dependencies.py
```

脚本会检查所有必需的Python包是否正确安装。

## 常见问题

### 1. lxml安装失败

**错误信息**：
```
Building lxml requires libxml2 and libxslt development packages
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install -y libxml2-dev libxslt1-dev

# CentOS/RHEL
sudo yum install -y libxml2-devel libxslt-devel
```

### 2. cryptography安装失败

**错误信息**：
```
No module named '_cffi_backend'
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install -y libffi-dev python3-dev

# CentOS/RHEL
sudo yum install -y libffi-devel python3-devel
```

### 3. ddddocr安装失败

**错误信息**：
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**解决方案（Windows）**：
1. 安装 Visual C++ Build Tools
2. 下载：https://visualstudio.microsoft.com/downloads/
3. 选择 "Build Tools for Visual Studio"

**解决方案（Linux）**：
```bash
# Ubuntu/Debian
sudo apt-get install -y libjpeg-dev libpng-dev zlib1g-dev

# CentOS/RHEL
sudo yum install -y libjpeg-turbo-devel libpng-devel zlib-devel
```

### 4. psycopg2安装失败

**错误信息**：
```
pg_config executable not found
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install -y libpq-dev postgresql-client

# CentOS/RHEL
sudo yum install -y postgresql-devel postgresql
```

### 5. 依赖版本冲突

如果遇到版本冲突，可以：

1. **使用虚拟环境**（推荐）：
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **清理pip缓存**：
```bash
pip cache purge
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 最小依赖安装

如果只需要命令行功能，可以使用最小依赖：

```bash
pip install -r requirements-minimal.txt
```

## Docker部署

Docker镜像已包含所有系统依赖，无需手动安装：

```bash
docker pull ghcr.io/vivi141/chaoxing:latest
docker-compose up -d
```

## 检查清单

安装前请确认：

- [ ] Python 3.12+ 已安装
- [ ] pip 已升级到最新版本
- [ ] 系统级依赖已安装（Linux）
- [ ] 虚拟环境已创建（推荐）
- [ ] 网络连接正常
- [ ] 依赖验证通过

## 获取帮助

如果仍然遇到问题：

1. 查看详细错误信息
2. 运行 `python scripts/verify_dependencies.py` 检查缺失的依赖
3. 检查系统日志：`/var/log/syslog` (Linux)
4. 提交Issue到GitHub仓库

