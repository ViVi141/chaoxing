# :globe_with_meridians: 超星学习通多用户Web管理平台

> 基于 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 原项目的增强版  
> 生产级Web管理平台，支持多用户同时注册登录并管理刷课任务

## :bookmark_tabs: 项目信息

- **原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)
- **增强版本**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)
- **增强开发**: ViVi141 (747384120@qq.com)
- **更新日期**: 2025-10-12
- **开源协议**: GPL-3.0

## 特性

- 🌐 多用户注册/登录（JWT认证）
- 📊 任务管理（创建/启动/暂停/取消/监控）
- ⚡ 实时进度推送（WebSocket）
- 👥 管理员后台（用户管理、任务监控、数据统计）
- 🔄 异步任务队列（Celery + Redis）
- 🐳 Docker一键部署

## 快速开始

### Docker方式（推荐）

```bash
# 1. 进入web目录
cd web

# 2. 复制并编辑环境配置
cp env.example .env
nano .env  # 修改SECRET_KEY、数据库密码等

# 3. 启动所有服务
docker-compose up -d

# 4. 访问服务
# API文档: http://localhost:8000/api/docs
# 健康检查: http://localhost:8000/api/health
# 默认管理员: admin / Admin@123
```

### 手动部署

```bash
# 后端
cd web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Celery Worker（新终端）
cd web/backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

详细说明：[START_GUIDE.md](START_GUIDE.md)

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  用户界面    │  │  管理员后台  │  │  实时监控    │      │
│  │  (Vue 3)     │  │  (Admin)     │  │  (WebSocket) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────┼─────────────────────────────────┐
│                    后端API层 (Backend)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Flask/FastAPI│  │  JWT认证    │  │  Socket.IO   │      │
│  │  RESTful API │  │  权限控制   │  │  实时推送    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    业务逻辑层 (Service)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  用户管理    │  │  任务调度    │  │  进度监控    │      │
│  │  服务        │  │  服务        │  │  服务        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    任务队列层 (Task Queue)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Celery      │  │  Redis       │  │  任务池      │      │
│  │  Worker      │  │  Broker      │  │  管理        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    数据层 (Data Layer)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SQLite/     │  │  Redis       │  │  日志文件    │      │
│  │  PostgreSQL  │  │  缓存        │  │  存储        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 功能模块

### 用户端功能
1. ✅ 用户注册/登录
2. ✅ 账号配置管理
3. ✅ 课程任务创建
4. ✅ 任务启动/暂停/取消
5. ✅ 实时进度查看
6. ✅ 题库配置
7. ✅ 通知配置

### 管理员端功能
1. ✅ 用户管理（查看、禁用、删除）
2. ✅ 全局任务监控
3. ✅ 系统资源监控
4. ✅ 日志查看
5. ✅ 数据统计和报表

## 技术栈（主流生产级方案）

### 后端
- **Web框架**: FastAPI 0.100+ (高性能、自动文档、类型提示)
- **ORM**: SQLAlchemy 2.0 + Alembic (数据库迁移)
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **任务队列**: Celery 5.3+ + Redis 7.0+
- **认证**: JWT (python-jose) + OAuth2
- **实时通信**: WebSocket (FastAPI原生)
- **API文档**: Swagger UI + ReDoc (自动生成)
- **数据验证**: Pydantic 2.0
- **部署**: Uvicorn + Gunicorn

### 前端
- **框架**: Vue 3.3+ (Composition API)
- **UI组件**: Element Plus 2.4+ (成熟稳定)
- **状态管理**: Pinia (Vue官方推荐)
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **构建工具**: Vite 5.0
- **图表**: ECharts 5.4+
- **实时通信**: Socket.IO Client

### DevOps
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **进程管理**: Supervisor
- **监控**: Prometheus + Grafana (可选)
- **日志**: Loguru + ELK Stack (可选)

## 目录结构

```
web/
├── backend/
│   ├── app.py                 # Flask应用入口
│   ├── models.py              # 数据库模型
│   ├── auth.py                # 认证和权限
│   ├── routes/
│   │   ├── user.py            # 用户API
│   │   ├── task.py            # 任务API
│   │   └── admin.py           # 管理员API
│   ├── services/
│   │   ├── user_service.py    # 用户服务
│   │   ├── task_service.py    # 任务服务
│   │   └── monitor_service.py # 监控服务
│   ├── celery_app.py          # Celery配置
│   └── config.py              # 配置文件
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue      # 登录页
│   │   │   ├── Dashboard.vue  # 用户仪表盘
│   │   │   └── Admin.vue      # 管理员后台
│   │   ├── components/        # 组件
│   │   ├── api/               # API调用
│   │   └── store/             # Vuex状态管理
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 数据库设计

### 用户表 (users)
- id: 主键
- username: 用户名（唯一）
- password_hash: 密码哈希
- email: 邮箱
- role: 角色（user/admin）
- is_active: 是否激活
- created_at: 创建时间

### 配置表 (user_configs)
- id: 主键
- user_id: 用户ID（外键）
- cx_username: 超星账号
- cx_password_encrypted: 加密的超星密码
- speed: 播放倍速
- notopen_action: 未开放章节处理方式
- tiku_config: 题库配置（JSON）
- notification_config: 通知配置（JSON）

### 任务表 (tasks)
- id: 主键
- user_id: 用户ID（外键）
- name: 任务名称
- course_ids: 课程ID列表（JSON）
- status: 状态（pending/running/paused/completed/failed）
- progress: 进度（0-100）
- celery_task_id: Celery任务ID
- start_time: 开始时间
- end_time: 结束时间
- error_msg: 错误信息

### 日志表 (task_logs)
- id: 主键
- task_id: 任务ID（外键）
- level: 日志级别
- message: 日志消息
- created_at: 创建时间

## API接口

### 认证接口
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/logout - 用户登出
- GET /api/auth/profile - 获取用户信息

### 用户配置接口
- GET /api/config - 获取配置
- PUT /api/config - 更新配置

### 任务接口
- GET /api/tasks - 获取任务列表
- POST /api/tasks - 创建任务
- GET /api/tasks/:id - 获取任务详情
- PUT /api/tasks/:id/start - 启动任务
- PUT /api/tasks/:id/pause - 暂停任务
- PUT /api/tasks/:id/cancel - 取消任务
- DELETE /api/tasks/:id - 删除任务

### 管理员接口
- GET /api/admin/users - 获取所有用户
- PUT /api/admin/users/:id - 更新用户
- DELETE /api/admin/users/:id - 删除用户
- GET /api/admin/tasks - 获取所有任务
- GET /api/admin/statistics - 获取统计数据
- GET /api/admin/logs - 获取系统日志

### WebSocket事件
- task_progress - 任务进度更新
- task_status - 任务状态变化
- system_notification - 系统通知

## 部署说明

### 开发环境
```bash
# 后端
cd web/backend
pip install -r requirements.txt
python app.py

# Celery Worker
celery -A celery_app worker --loglevel=info

# 前端
cd web/frontend
npm install
npm run dev
```

### 生产环境
```bash
# 使用Docker Compose
docker-compose up -d
```

## 安全性

1. ✅ 密码使用bcrypt加密
2. ✅ JWT令牌认证
3. ✅ CORS跨域保护
4. ✅ SQL注入防护
5. ✅ XSS防护
6. ✅ CSRF保护
7. ✅ 请求频率限制
8. ✅ 敏感信息加密存储

