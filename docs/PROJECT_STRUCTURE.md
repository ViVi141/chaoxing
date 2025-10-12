# :file_folder: 项目结构说明

## :link: 项目信息
- **原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)
- **增强版本**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)
- **增强开发**: ViVi141 (747384120@qq.com)
- **更新日期**: 2025-10-12

## 整体结构

```
chaoxing/
├── 📂 api/                          # 核心API模块（命令行版）
├── 📂 web/                          # Web多用户平台
├── 📂 tools/                        # 工具脚本
├── 📂 resource/                     # 资源文件
├── 📂 logs/                         # 日志目录
├── 📂 docs/                         # 文档目录
│   ├── SUMMARY.md                  # 项目总览
│   ├── PROJECT_STRUCTURE.md        # 本文档
│   ├── CHANGELOG.md                # 更新日志
│   └── CREDITS.md                  # 贡献致谢
├── 📄 main.py                       # 命令行版主程序
├── 📄 config_template.ini           # 配置模板
├── 📄 requirements.txt              # Python依赖
├── 📄 pyproject.toml                # 项目配置
├── 📄 Dockerfile                    # Docker镜像（命令行版）
├── 📄 .gitignore                    # Git忽略文件
├── 📄 LICENSE                       # 开源协议
└── 📄 README.md                     # 主文档
```

## 核心模块详解

### api/ - 核心API模块

```
api/
├── answer.py               # 题库接口（5种题库集成）
├── answer_check.py         # 答案验证
├── base.py                 # 超星API封装（登录、课程、任务）
├── captcha.py              # 验证码识别
├── cipher.py               # AES加密解密
├── config.py               # 全局配置常量
├── config_validator.py     # 配置参数验证器
├── cookies.py              # Cookie管理
├── cxsecret_font.py        # 超星字体解析
├── decode.py               # 页面数据解析
├── exceptions.py           # 自定义异常
├── font_decoder.py         # 字体解码器
├── http_client.py          # HTTP客户端优化（重试机制）
├── logger.py               # 日志系统（自动脱敏、轮转）
├── notification.py         # 通知推送
├── process.py              # 进度显示
└── secure_config.py        # 配置加密存储
```

### web/ - Web多用户平台

```
web/
├── backend/                        # 后端（FastAPI）
│   ├── app.py                     # FastAPI主应用
│   ├── config.py                  # 配置管理（Pydantic Settings）
│   ├── database.py                # 异步数据库连接
│   ├── models.py                  # 数据模型（5个表）
│   ├── schemas.py                 # Pydantic数据验证
│   ├── auth.py                    # JWT认证系统
│   ├── celery_app.py              # Celery配置
│   │
│   ├── routes/                    # API路由（25个接口）
│   │   ├── __init__.py           # 路由导出
│   │   ├── auth.py               # 认证接口（5个）
│   │   ├── user.py               # 用户接口（4个）
│   │   ├── task.py               # 任务接口（9个）
│   │   ├── admin.py              # 管理员接口（7个）
│   │   └── websocket.py          # WebSocket实时通信
│   │
│   ├── tasks/                     # Celery异步任务
│   │   ├── __init__.py
│   │   └── study_tasks.py        # 学习任务（集成刷课逻辑）
│   │
│   ├── requirements.txt           # Python依赖
│   └── Dockerfile                 # Docker镜像
│
├── frontend/                       # 前端（Vue 3）[待开发]
│   └── （待创建）
│
├── docker-compose.yml              # Docker服务编排
├── env.example                     # 环境变量模板
├── start_backend.bat               # Windows后端启动脚本
├── start_celery.bat                # Windows Celery启动脚本
├── README.md                       # Web平台主文档
├── START_GUIDE.md                  # 快速启动指南
└── DEPLOYMENT_GUIDE.md             # 生产环境部署指南
```

### tools/ - 工具脚本

```
tools/
└── encrypt_config.py               # 配置文件加密工具
```

### resource/ - 资源文件

```
resource/
└── font_map_table.json             # 字体映射表
```

### docs/ - 项目文档

```
docs/
├── SUMMARY.md                      # 项目总览
├── PROJECT_STRUCTURE.md            # 本文档
├── CHANGELOG.md                    # 更新日志
└── CREDITS.md                      # 贡献与致谢
```

## 数据库表结构（Web平台）

### users - 用户表
- id, username, password_hash, email, role, is_active
- created_at, last_login

### user_configs - 用户配置表
- id, user_id, cx_username, cx_password_encrypted
- speed, notopen_action, use_cookies
- tiku_config (JSON), notification_config (JSON)

### tasks - 任务表
- id, user_id, name, course_ids (JSON)
- status, progress, celery_task_id
- created_at, start_time, end_time
- error_msg, completed_courses, total_courses

### task_logs - 任务日志表
- id, task_id, level, message, created_at

### system_logs - 系统日志表
- id, level, module, message, user_id, ip_address, created_at

## 配置文件

### config.ini (命令行版)
```ini
[common]         # 通用配置
[tiku]           # 题库配置
[notification]   # 通知配置
```

### .env (Web平台)
```env
DATABASE_URL     # 数据库连接
REDIS_URL        # Redis连接
SECRET_KEY       # 安全密钥
JWT_SECRET_KEY   # JWT密钥
...
```

## 日志文件

### 命令行版
```
logs/
├── chaoxing_YYYY-MM-DD.log       # 当天日志
├── chaoxing_YYYY-MM-DD.log.zip   # 历史日志（压缩）
└── chaoxing_error_YYYY-MM-DD.log # 错误日志
```

### Web平台
```
web/backend/logs/
├── web_app.log                    # 应用日志
└── celery.log                     # Celery日志
```

## Docker镜像

### 命令行版
- 基础镜像：python:3.11-slim
- 入口：python main.py
- 挂载：config.ini

### Web平台
- backend：FastAPI应用
- celery：异步任务Worker
- postgres：PostgreSQL数据库
- redis：缓存和消息队列
- nginx：反向代理（可选）

## API接口分类（Web平台）

### 认证接口 (5个)
- POST /api/auth/register - 注册
- POST /api/auth/login - 登录
- POST /api/auth/logout - 登出
- GET /api/auth/me - 当前用户
- POST /api/auth/refresh - 刷新令牌

### 用户接口 (4个)
- GET /api/user/config - 获取配置
- PUT /api/user/config - 更新配置
- PUT /api/user/password - 修改密码
- GET /api/user/profile - 用户信息

### 任务接口 (9个)
- GET /api/tasks - 任务列表
- POST /api/tasks - 创建任务
- GET /api/tasks/{id} - 任务详情
- PUT /api/tasks/{id} - 更新任务
- POST /api/tasks/{id}/start - 启动
- POST /api/tasks/{id}/pause - 暂停
- POST /api/tasks/{id}/cancel - 取消
- DELETE /api/tasks/{id} - 删除
- GET /api/tasks/{id}/logs - 日志

### 管理员接口 (7个)
- GET /api/admin/users - 用户列表
- GET /api/admin/users/{id} - 用户详情
- PUT /api/admin/users/{id} - 更新用户
- DELETE /api/admin/users/{id} - 删除用户
- GET /api/admin/tasks - 所有任务
- POST /api/admin/tasks/{id}/force-stop - 强制停止
- GET /api/admin/statistics - 统计数据
- GET /api/admin/logs - 系统日志

### WebSocket接口
- /ws/connect?token=JWT - 实时连接

## 技术栈

### 命令行版
- Python 3.10+
- requests, beautifulsoup4, lxml
- loguru, cryptography
- ddddocr (验证码识别)

### Web平台后端
- FastAPI 0.104+
- SQLAlchemy 2.0 (异步ORM)
- PostgreSQL 15+ / SQLite
- Redis 7.0+
- Celery 5.3+
- python-jose (JWT)
- Pydantic 2.0

### Web平台前端（待开发）
- Vue 3.3+
- Element Plus 2.4+
- Pinia (状态管理)
- Vue Router 4
- Axios
- ECharts 5.4+

### 部署
- Docker + Docker Compose
- Nginx (反向代理)
- Uvicorn + Gunicorn

## 开发工具

### 推荐IDE
- VS Code
- PyCharm Professional

### VS Code插件
- Python
- Pylance
- Volar (Vue 3)
- Docker

### 代码规范
- Google Python Style Guide
- PEP 8
- 类型注解完整

## 项目链接

- **原项目**: https://github.com/Samueli924/chaoxing
- **增强版本**: https://github.com/ViVi141/chaoxing
- **Issues**: https://github.com/ViVi141/chaoxing/issues

---

**最后更新**: 2025-10-12

