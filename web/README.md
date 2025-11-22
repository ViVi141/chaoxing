# 超星学习通多用户Web管理平台

> FastAPI + React 全栈Web应用
> 
> 🆕 **v2.5.4**: Docker镜像启动修复 + JWT认证服务补全 + 安全模块完善

---

## 🎯 功能特性

### 用户功能
- 注册/登录系统（JWT认证）
- 超星账号配置管理
- 创建和管理学习任务
- 实时查看任务进度
- 查看详细任务日志
- 6种题库支持（含AI/DeepSeek/硅基流动）
- 4种通知方式（含SMTP邮件）

### 管理员功能
- 用户管理（查看/编辑/删除/详情）✨
- 全局任务监控
- 系统统计数据（实时准确）✨
- 强制停止任务
- 🆕 **在线配置管理**（无需重启）⚡
- 🆕 **图形化数据库迁移**（SQLite → PostgreSQL + Redis）

### 实时功能
- WebSocket实时进度推送
- 视频播放进度显示（时间轴）
- 任务状态实时更新
- 详细日志滚动显示

---

## 🚀 快速启动

### 方式1：一键启动（Windows）
```batch
启动后端和Celery.bat
cd frontend && npm run dev
```

### 方式2：分别启动

**后端：**
```bash
cd backend
python app.py
```

**Celery Worker：**
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

**前端：**
```bash
cd frontend
npm install  # 首次运行
npm run dev
```

访问：http://localhost:5173

---

## 📦 部署模式

### 简单模式（推荐，零依赖）
- SQLite数据库
- 文件系统消息队列
- 适合50人以下

**配置：**
```bash
DEPLOY_MODE=simple
DATABASE_URL=sqlite+aiosqlite:///data/chaoxing.db
CELERY_BROKER_URL=filesystem://localhost/
```

### 标准模式（生产环境）
- PostgreSQL数据库
- Redis消息队列
- 适合500人以上

**Docker部署：**
```bash
docker-compose up -d
```

详见：[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

## 🔧 环境配置

### 后端环境变量（.env）

```bash
# 部署模式
DEPLOY_MODE=simple

# 数据库
DATABASE_URL=sqlite+aiosqlite:///data/chaoxing.db

# Celery
CELERY_BROKER_URL=filesystem://localhost/
CELERY_RESULT_BACKEND=file://data/celery_results

# 安全密钥
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# 默认管理员
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Admin@123
DEFAULT_ADMIN_EMAIL=admin@example.com
```

配置示例：[env.example](env.example)

---

## 📡 API接口

### 完整接口列表
- **认证**: 8个接口（注册/登录/密码重置等）
- **用户**: 5个接口（配置/资料管理）
- **任务**: 11个接口（CRUD + 操作控制）
- **课程**: 1个接口（课程列表）
- **管理员**: 8个接口（用户/任务管理）
- **WebSocket**: 实时通信

**总计：** 33个RESTful API + 1个WebSocket

**Swagger文档：** http://localhost:8000/api/docs

详见：[../docs/API.md](../docs/API.md)

---

## 🗄️ 数据库

### 数据表（5个）
- `users` - 用户表
- `user_configs` - 用户配置
- `tasks` - 任务表
- `task_logs` - 任务日志
- `email_verifications` - 邮箱验证

详见：[../docs/DATABASE.md](../docs/DATABASE.md)

---

## 🔒 安全性

- ✅ JWT令牌认证
- ✅ bcrypt密码加密
- ✅ 用户数据完全隔离
- ✅ 防横向攻击（user_id过滤）
- ✅ 防纵向攻击（role验证）
- ✅ WebSocket消息隔离

详见：[../docs/SECURITY.md](../docs/SECURITY.md)

---

## 📈 性能指标

### 简单模式
- 支持用户：50-100
- 并发任务：10-20
- 推荐配置：2核4GB

### 标准模式
- 支持用户：500-1000
- 并发任务：100+
- 推荐配置：4核8GB

---

## 🛠️ 开发

### 项目结构
```
web/
├── backend/           # FastAPI后端
│   ├── app.py         # 主应用
│   ├── models.py      # 数据模型
│   ├── routes/        # API路由
│   ├── tasks/         # Celery任务
│   └── data/          # 数据文件(gitignore)
└── frontend/          # React前端
    ├── src/
    │   ├── pages/     # 页面组件
    │   └── providers/ # 数据提供者
    └── package.json
```

### 运行测试
```bash
# 安全测试
cd backend
python test_security.py

# API测试  
python test_all_apis.py
```

详见：[../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)

---

## 📝 更新日志

查看：[../docs/CHANGELOG.md](../docs/CHANGELOG.md)

---

## 🎉 v2.2.0 升级亮点

### 技术栈现代化
- ✅ 升级到Refine v5架构
- ✅ 升级到React Router v7
- ✅ 使用最新Ant Design 5.27
- ✅ 集成React Query 5.x

### 新增功能
- ✅ 图形化数据库迁移（SQLite → PostgreSQL）
- ✅ 8个新增迁移API端点
- ✅ 自动重启脚本（Windows/Linux）

### 代码质量
- ✅ TypeScript错误：0个
- ✅ Linter警告：0个
- ✅ 警告修复率：75%

详细报告：
- [Refine v5升级完整报告](../REFINE_V5_UPGRADE_COMPLETE.md)
- [数据库迁移指南](../docs/DATABASE_MIGRATION.md)
- [升级指南](../docs/UPGRADE_GUIDE.md)

---

## ⚠️ 免责声明

- 本代码遵循GPL-3.0协议
- 仅用于学习讨论
- 禁止用于商业盈利
- 使用后果自负

---

**版本：** 2.2.0 🆕  
**更新：** 2025-10-13
