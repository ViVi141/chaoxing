# 环境配置指南

> **重要原则：一个项目，一个环境，所有模块共享**

## 📋 虚拟环境设置

本项目**所有模块统一使用根目录的虚拟环境**，包括：
- ✅ 命令行版
- ✅ Web后端
- ✅ Celery Worker
- ✅ 所有启动脚本
- ✅ Docker构建

### 为什么使用统一虚拟环境？

- ✅ **简化依赖管理** - 一次安装，处处使用
- ✅ **避免重复安装** - 节省时间和磁盘空间
- ✅ **确保版本一致性** - 避免环境差异导致的问题
- ✅ **简化维护** - 只需管理一个环境
- ✅ **自动检测** - 所有启动脚本自动使用统一环境

---

## 🚀 安装步骤

### 1. 创建虚拟环境

**在项目根目录**（chaoxing/）执行：

```bash
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

### 2. 激活虚拟环境

**Windows（PowerShell）**：
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows（CMD）**：
```batch
.\.venv\Scripts\activate.bat
```

**Linux/Mac**：
```bash
source .venv/bin/activate
```

### 3. 安装依赖

```bash
# 升级pip
python -m pip install --upgrade pip

# 安装所有依赖（命令行版 + Web平台）
pip install -r requirements.txt
```

### 4. 验证安装

```bash
# 验证关键依赖
python -c "import fastapi; import requests; import celery; print('✅ 所有依赖安装成功！')"
```

---

## 📦 依赖说明

### 统一的requirements.txt

项目根目录的`requirements.txt`包含：
- 命令行版所有依赖
- Web平台所有依赖
- 开发工具（可选）

### web/backend/requirements.txt

此文件仅用于Docker构建，本地开发**不需要使用**。

---

## 💻 使用方式

### 命令行版

```bash
# 确保在项目根目录且已激活虚拟环境
python main.py -c config.ini
```

### Web平台开发

**方式一：使用启动脚本（推荐）**

Windows：
```batch
# 分别在三个终端运行
web\start_backend.bat     # 终端1：后端
web\start_celery.bat      # 终端2：Celery
web\frontend\start.bat    # 终端3：前端
```

Linux/Mac：
```bash
# 添加执行权限（首次）
chmod +x web/start_backend.sh web/start_celery.sh

# 分别在三个终端运行
./web/start_backend.sh    # 终端1：后端
./web/start_celery.sh     # 终端2：Celery
cd web/frontend && npm run dev  # 终端3：前端
```

**方式二：手动启动**

```bash
# 确保在项目根目录
source .venv/bin/activate  # Linux/Mac
# 或 .\.venv\Scripts\Activate.ps1  # Windows

# 启动后端（终端1）
cd web/backend
python run_app.py

# 启动Celery（终端2）
cd web/backend
python run_celery.py

# 启动前端（终端3）
cd web/frontend
npm install  # 首次需要
npm run dev
```

**说明**：
- ✅ 所有启动脚本自动使用统一的虚拟环境
- ✅ 自动检查环境是否就绪
- ✅ 提供友好的错误提示

---

## 🐳 Docker部署

Docker部署**不需要**创建虚拟环境，直接使用：

```bash
cd web
docker-compose -f docker-compose.simple.yml up -d
```

Docker会自动：
1. 使用项目根目录作为build context
2. 复制根目录的`requirements.txt`
3. 在容器内安装所有依赖
4. 设置正确的PYTHONPATH

---

## 🔧 常见问题

### Q: web/backend/requirements.txt是干什么的？

**A**: 仅用于Docker构建时的引用。本地开发使用根目录的`requirements.txt`。

### Q: 我需要在web/backend创建虚拟环境吗？

**A**: **不需要！**所有模块使用根目录的虚拟环境。

### Q: 为什么我的IDE提示找不到模块？

**A**: 确保：
1. IDE的Python解释器设置为根目录的虚拟环境
2. 项目根目录添加到PYTHONPATH

**VS Code配置示例**（`.vscode/settings.json`）：
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.extraPaths": ["${workspaceFolder}"]
}
```

### Q: 我可以使用conda吗？

**A**: 可以！使用conda替代venv：
```bash
# 创建conda环境
conda create -n chaoxing python=3.11

# 激活环境
conda activate chaoxing

# 安装依赖
pip install -r requirements.txt
```

### Q: 如何更新依赖？

**A**: 在根目录执行：
```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或 .\venv\Scripts\Activate.ps1  # Windows

# 更新依赖
pip install --upgrade -r requirements.txt
```

### Q: 我遇到依赖冲突怎么办？

**A**: 
1. 删除虚拟环境：`rm -rf .venv` (Linux/Mac) 或 `rmdir /s .venv` (Windows)
2. 重新创建虚拟环境：`python -m venv .venv`
3. 重新安装依赖：`pip install -r requirements.txt`

---

## 📊 依赖树

```
chaoxing/  (项目根目录)
├── .venv/  (虚拟环境 - 所有模块共用)
├── requirements.txt  (统一依赖文件)
├── main.py  (命令行版，使用根虚拟环境)
├── api/  (核心逻辑模块)
└── web/
    ├── backend/
    │   ├── app.py  (使用根虚拟环境)
    │   └── requirements.txt  (仅Docker用)
    └── frontend/
        └── node_modules/  (Node.js依赖，独立管理)
```

---

## ✅ 检查清单

开发前确保：

- [ ] 在项目根目录创建了虚拟环境（.venv/）
- [ ] 虚拟环境已激活（命令行提示符有`(.venv)`前缀）
- [ ] 已安装`requirements.txt`中的所有依赖
- [ ] IDE的Python解释器指向根目录的虚拟环境
- [ ] 项目根目录在PYTHONPATH中

---

## 🎯 快速开始

### 方式一：一键设置（推荐）

**Windows**：
```batch
# 双击运行或命令行执行
setup_env.bat
```

**Linux/Mac**：
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**特性**：
- ✅ 自动检测虚拟环境（存在则使用，不存在才创建）
- ✅ 自动安装/更新所有依赖
- ✅ 智能错误处理和提示

### 方式二：一键启动所有服务

**Windows**：
```batch
# 自动设置环境并启动所有服务
start_all.bat
```

**Linux/Mac**：
```bash
chmod +x start_all.sh
./start_all.sh
```

**说明**：
- 会自动检查并设置环境
- 一次启动后端、Celery、前端所有服务
- 适合快速开发和测试

---

**原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
**增强版**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)  
**开发者**: ViVi141 (747384120@qq.com)

