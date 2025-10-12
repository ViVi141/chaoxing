# :zap: 快速启动指南

> 基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)

---

## 选择你的使用方式

本项目提供**两种**完整的使用方式：

### 方式一：命令行版（单用户，本地运行）

**适合**：个人使用、快速上手、不需要Web界面

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置
cp config_template.ini config.ini
# 编辑config.ini填入超星账号

# 3. 运行
python main.py -c config.ini
```

[详细说明 →](README.md#books-使用方法)

### 方式二：Web多用户平台（多用户，生产级）

**适合**：多人使用、需要管理监控、对外提供服务

#### 简单模式（推荐 - 零依赖）⭐

**特点**：
- ✅ 无需安装PostgreSQL
- ✅ 无需安装Redis
- ✅ 只需Python和Node.js
- ✅ 适合<50用户使用

**Windows一键启动**：

```batch
REM 1. 后端（窗口1）
web\start_backend.bat

REM 2. Celery Worker（窗口2）
web\start_celery.bat

REM 3. 前端（窗口3）
web\frontend\start.bat
```

访问: http://localhost:5173

**Linux/Mac启动**：

```bash
# 后端
cd web/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Celery（新终端）
celery -A celery_app worker --loglevel=info

# 前端（新终端）
cd web/frontend
npm install
npm run dev
```

#### 标准模式（生产环境 - 需要依赖）

**特点**：
- 使用PostgreSQL数据库
- 使用Redis缓存和队列
- 适合>50用户使用

**Docker一键启动**：

```bash
cd web
cp env.example .env
# 编辑.env修改DEPLOY_MODE=standard和其他配置
docker-compose up -d
```

访问: http://localhost:3000

[详细说明 →](web/START_GUIDE.md)

---

## :star2: Web平台首次使用

### 步骤1：启动服务

选择上述任一方式启动Web平台。

### 步骤2：访问安装向导

浏览器访问前端地址，会自动进入**安装向导**：

1. **欢迎页**
   - 了解平台特性
   - 阅读使用须知

2. **管理员配置**
   - 选择使用默认账号：`admin` / `Admin@123`
   - 或创建新管理员账号

3. **系统配置**
   - 平台名称
   - 最大任务数
   - 用户注册开关
   - 其他可选配置

4. **完成**
   - 查看配置摘要
   - 点击"进入系统"

### 步骤3：登录系统

使用管理员账号登录：
- 用户名：`admin`
- 密码：`Admin@123`

⚠️ **首次登录后立即修改密码！**

### 步骤4：配置超星账号

1. 点击侧边栏"个人配置"
2. 在"超星账号"标签页填写：
   - 手机号
   - 密码（会加密存储）
3. 配置学习参数（可选）：
   - 播放倍速
   - 未开放章节处理方式
4. 配置题库（可选）
5. 配置通知（可选）
6. 点击"保存配置"

### 步骤5：创建任务

1. 点击"任务管理"
2. 点击"创建任务"
3. 填写：
   - 任务名称
   - 课程ID（可选，留空则学习所有课程）
4. 点击"创建"

### 步骤6：启动任务

1. 在任务列表中找到刚创建的任务
2. 点击"启动"按钮
3. 任务开始执行，进度条实时更新
4. 可随时"暂停"或"取消"

### 步骤7：查看日志

点击任务的"日志"按钮，查看详细执行日志。

---

## :busts_in_silhouette: 管理员功能

### 进入管理后台

1. 使用管理员账号登录
2. 点击侧边栏"管理后台"

### 功能说明

#### 数据统计
- 总用户数、活跃用户
- 任务统计（运行、完成、失败）
- ECharts图表展示

#### 用户管理
- 查看所有用户
- 启用/禁用用户
- 删除用户
- 搜索用户

#### 任务监控
- 查看所有用户的任务
- 按用户过滤
- 强制停止任务

#### 系统日志
- 查看系统日志
- 按级别过滤
- 分页查看

---

## :gear: 配置说明

### 后端配置（web/.env）

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# 安全密钥（必须修改！）
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# 管理员默认账号
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Admin@123
```

### 前端配置（web/frontend/env.example）

```env
# API地址
VITE_API_URL=http://localhost:8000/api

# WebSocket地址
VITE_WS_URL=ws://localhost:8000
```

---

## :package: 功能特性

### 命令行版特性
- ✅ 视频/文档/测验自动完成
- ✅ 倍速播放（1.0-2.0倍）
- ✅ 5种题库集成
- ✅ 3种通知方式
- ✅ 配置加密存储
- ✅ 日志自动脱敏

### Web平台特性
- ✅ 多用户注册/登录
- ✅ **安装向导引导配置** 🌟
- ✅ 任务管理（创建/启动/暂停/取消）
- ✅ 实时进度推送（WebSocket）
- ✅ 管理员后台监控
- ✅ 数据统计和图表
- ✅ 异步任务队列

---

## :warning: 常见问题

### Q: 后端无法启动？
**A**: 检查Python版本（需要3.10+），确保已安装依赖：
```bash
pip install -r web/backend/requirements.txt
```

### Q: 前端无法访问后端API？
**A**: 检查：
1. 后端是否正常运行（http://localhost:8000/api/health）
2. 前端代理配置是否正确（vite.config.js）
3. CORS配置是否正确

### Q: Celery任务不执行？
**A**: 检查：
1. Redis是否运行（`redis-cli ping`）
2. Celery Worker是否启动
3. 查看Celery日志排查错误

### Q: 忘记管理员密码？
**A**: 
1. 删除 localStorage 中的 `setup_completed`
2. 重新访问会进入安装向导
3. 或直接在数据库重置密码

### Q: WebSocket连接失败？
**A**: 检查：
1. 后端WebSocket路由是否正常
2. 浏览器是否支持WebSocket
3. 代理配置是否正确

---

## :link: 相关链接

- **原项目**: https://github.com/Samueli924/chaoxing
- **增强版本**: https://github.com/ViVi141/chaoxing
- **Issues**: https://github.com/ViVi141/chaoxing/issues
- **开发者**: ViVi141 (747384120@qq.com)

---

## :trophy: 致谢

感谢原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 及所有贡献者！

详见: [docs/CREDITS.md](docs/CREDITS.md)

---

**祝您使用愉快！** 🎉

有问题欢迎提Issue或发邮件：747384120@qq.com

