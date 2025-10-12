# 🚀 一键启动脚本使用指南

> **让部署和运行变得极其简单！**

---

## 📋 脚本总览

本项目提供了多个便捷脚本，让你无需手动配置环境，一键启动所有服务。

### 核心脚本

| 脚本 | Windows | Linux/Mac | 说明 |
|------|---------|-----------|------|
| **环境设置** | `setup_env.bat` | `setup_env.sh` | 自动设置虚拟环境和依赖 |
| **一键启动** | `start_all.bat` | `start_all.sh` | 一次启动所有Web服务 |
| **后端启动** | `web\start_backend.bat` | `web/start_backend.sh` | 单独启动后端服务 |
| **Celery启动** | `web\start_celery.bat` | `web/start_celery.sh` | 单独启动Celery Worker |

---

## 🎯 使用场景

### 场景一：首次使用（新用户）

**最简单的方式：**

```batch
# Windows
start_all.bat
```

```bash
# Linux/Mac
chmod +x start_all.sh
./start_all.sh
```

**它会自动**：
1. ✅ 检测虚拟环境（没有则自动创建）
2. ✅ 安装所有依赖
3. ✅ 启动后端、Celery、前端三个服务
4. ✅ 打开浏览器访问页面

### 场景二：日常开发

**推荐使用分别启动：**

```batch
# Windows - 三个终端分别运行
web\start_backend.bat
web\start_celery.bat
cd web\frontend && npm run dev
```

```bash
# Linux/Mac - 三个终端分别运行
./web/start_backend.sh
./web/start_celery.sh
cd web/frontend && npm run dev
```

**优势**：
- ✅ 每个服务独立终端，方便查看日志
- ✅ 可以单独重启某个服务
- ✅ 开发时更灵活

### 场景三：只用命令行版

```bash
# 1. 设置环境（首次）
./setup_env.sh  # Linux/Mac
# 或 setup_env.bat  # Windows

# 2. 运行
python main.py -c config.ini
```

---

## 📖 详细说明

### 1. setup_env.bat / setup_env.sh

**功能**：一键设置开发环境

**做了什么**：
```
[1/4] 检查虚拟环境
  - 如果存在：使用现有环境 ✅
  - 如果不存在：创建新环境 🆕

[2/4] 激活虚拟环境
  - Windows: venv\Scripts\activate.bat
  - Linux/Mac: source venv/bin/activate

[3/4] 升级pip
  - python -m pip install --upgrade pip

[4/4] 安装所有依赖
  - pip install -r requirements.txt
  - 包含命令行版 + Web平台所有依赖
```

**使用方法**：

Windows：
```batch
# 方式1：双击运行
双击 setup_env.bat

# 方式2：命令行
setup_env.bat
```

Linux/Mac：
```bash
# 添加执行权限（首次）
chmod +x setup_env.sh

# 运行
./setup_env.sh
```

**智能特性**：
- ✅ 自动检测虚拟环境（避免重复创建）
- ✅ 错误提示友好
- ✅ 显示安装进度

---

### 2. start_all.bat / start_all.sh

**功能**：一键启动所有Web服务

**做了什么**：
```
[检查] 虚拟环境状态
  - 未检测到 → 自动运行 setup_env 设置环境

[1/3] 启动后端服务
  - 使用：python run_app.py
  - 端口：8000
  - API文档：http://localhost:8000/api/docs

[2/3] 启动Celery Worker
  - 使用：python run_celery.py
  - 处理异步任务
  - 自动适配Windows/Linux

[3/3] 启动前端服务
  - 使用：npm run dev
  - 端口：5173
  - 访问：http://localhost:5173
```

**使用方法**：

Windows：
```batch
# 方式1：双击运行（推荐）
双击 start_all.bat

# 方式2：命令行
start_all.bat
```

Linux/Mac：
```bash
# 添加执行权限（首次）
chmod +x start_all.sh

# 运行
./start_all.sh

# 后台运行并查看日志
./start_all.sh &
tail -f logs/backend.log    # 查看后端日志
tail -f logs/celery.log     # 查看Celery日志
tail -f logs/frontend.log   # 查看前端日志
```

**Windows特点**：
- ✅ 每个服务在独立窗口运行
- ✅ 关闭窗口即停止服务
- ✅ 便于查看各服务日志

**Linux/Mac特点**：
- ✅ 后台运行所有服务
- ✅ 日志输出到logs/目录
- ✅ 显示每个服务的PID

**停止服务**：

Windows：
```batch
# 关闭所有打开的服务窗口
```

Linux/Mac：
```bash
# 方式1：使用PID（脚本输出的）
kill <backend_pid> <celery_pid> <frontend_pid>

# 方式2：查找并杀死进程
pkill -f "python app.py"
pkill -f "celery"
pkill -f "npm run dev"
```

---

### 3. web/start_backend.bat / web/start_backend.sh

**功能**：单独启动后端API服务

**做了什么**：
```
[1/3] 检查项目虚拟环境（根目录）
  - 未检测到 → 提示运行 setup_env

[2/3] 激活虚拟环境

[3/3] 启动后端服务
  - 运行：python run_app.py
  - 端口：8000
```

**使用方法**：

Windows：
```batch
# 双击运行或命令行
web\start_backend.bat
```

Linux/Mac：
```bash
chmod +x web/start_backend.sh
./web/start_backend.sh
```

**访问**：
- API文档：http://localhost:8000/api/docs
- 健康检查：http://localhost:8000/api/health
- 默认管理员：admin / Admin@123

---

### 4. web/start_celery.bat / web/start_celery.sh

**功能**：单独启动Celery任务队列

**做了什么**：
```
[1/3] 检查项目虚拟环境（根目录）
  - 未检测到 → 提示运行 setup_env

[2/3] 激活虚拟环境

[3/3] 启动Celery Worker
  - Windows: 使用solo池模式
  - Linux/Mac: 使用默认池模式
```

**使用方法**：

Windows：
```batch
web\start_celery.bat
```

Linux/Mac：
```bash
chmod +x web/start_celery.sh
./web/start_celery.sh
```

**注意事项**：
- ✅ 使用 `run_celery.py` 统一入口
- ✅ 自动适配Windows（solo池）和Linux（多进程池）
- ✅ 需要先启动后端服务

---

## 🔧 常见问题

### Q1: 首次使用应该运行哪个脚本？

**A**: 运行 `start_all.bat`（Windows）或 `start_all.sh`（Linux/Mac）

它会自动检测并设置环境，然后启动所有服务。

### Q2: 脚本提示"未检测到虚拟环境"怎么办？

**A**: 运行环境设置脚本：

```bash
# Windows
setup_env.bat

# Linux/Mac
chmod +x setup_env.sh && ./setup_env.sh
```

### Q3: 如何只启动某个服务？

**A**: 使用对应的单独启动脚本：

```bash
# 只启动后端
web\start_backend.bat  # Windows
./web/start_backend.sh # Linux/Mac

# 只启动Celery
web\start_celery.bat   # Windows
./web/start_celery.sh  # Linux/Mac
```

### Q4: 虚拟环境在哪里？

**A**: 在项目根目录的 `.venv/` 文件夹（隐藏文件夹）

所有脚本都使用这个统一的虚拟环境。

### Q5: 如何更新依赖？

**A**: 重新运行环境设置脚本：

```bash
# 它会自动检测到虚拟环境并更新依赖
setup_env.bat  # Windows
./setup_env.sh # Linux/Mac
```

### Q6: Linux/Mac脚本没有执行权限？

**A**: 添加执行权限：

```bash
chmod +x setup_env.sh start_all.sh
chmod +x web/start_backend.sh web/start_celery.sh
```

### Q7: 如何查看服务是否正常运行？

**A**: 访问以下地址：

- 后端健康检查：http://localhost:8000/api/health
- 前端页面：http://localhost:5173
- API文档：http://localhost:8000/api/docs

### Q8: 端口被占用怎么办？

**A**: 

Windows查找并关闭占用端口的进程：
```batch
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

Linux/Mac查找并关闭占用端口的进程：
```bash
lsof -i :8000
kill -9 <进程ID>
```

---

## 🎯 最佳实践

### 开发环境（推荐）

1. **首次设置**：
   ```bash
   ./setup_env.sh  # 或 setup_env.bat
   ```

2. **日常开发**：
   ```bash
   # 三个终端分别运行
   ./web/start_backend.sh
   ./web/start_celery.sh
   cd web/frontend && npm run dev
   ```

3. **优势**：
   - 每个服务独立终端
   - 方便查看日志
   - 可以单独重启

### 快速演示（推荐）

1. **一键启动**：
   ```bash
   ./start_all.sh  # 或 start_all.bat
   ```

2. **优势**：
   - 最快速度启动
   - 适合演示和测试
   - 一个命令搞定

### 生产环境（推荐）

使用Docker部署：
```bash
cd web
docker-compose -f docker-compose.simple.yml up -d
```

---

## 📊 脚本关系图

```
项目根目录/
│
├── setup_env.bat/sh        → 设置统一虚拟环境
│                              ↓
├── .venv/                   → 所有模块共享（隐藏文件夹）
│   ├── Scripts/bin/         → Python解释器
│   └── Lib/lib/             → 所有依赖包
│                              ↓
├── start_all.bat/sh         → 调用 .venv，启动所有服务
│   ├── 后端    ←──┐
│   ├── Celery  ←──┼── 都使用 .venv/
│   └── 前端    ←──┘
│
└── web/
    ├── start_backend.bat/sh → 调用 .venv，启动后端
    └── start_celery.bat/sh  → 调用 .venv，启动Celery
```

**核心理念**：
- 🎯 **一个项目，一个环境**
- 🎯 **所有脚本，统一虚拟环境**
- 🎯 **自动检测，智能处理**

---

## ✅ 快速检查清单

启动前确保：

- [ ] 已安装Python 3.10+
- [ ] 已安装Node.js 16+（仅Web平台需要）
- [ ] 项目完整（包含所有文件）
- [ ] 网络正常（首次需要下载依赖）

使用脚本：

- [ ] Windows用户：双击.bat文件或命令行运行
- [ ] Linux/Mac用户：先 `chmod +x` 再运行
- [ ] 首次使用：运行 `start_all`
- [ ] 日常开发：分别启动各服务

---

## 🎉 总结

有了这些一键启动脚本，你可以：

✅ **3秒启动** - 双击脚本即可  
✅ **零配置** - 自动设置所有环境  
✅ **统一管理** - 一个虚拟环境，所有模块共享  
✅ **智能检测** - 自动判断环境状态  
✅ **友好提示** - 清晰的错误信息和帮助  

**再也不用担心环境配置问题！**

---

**原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
**增强版**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)  
**开发者**: ViVi141 (747384120@qq.com)

