# :rocket: 快速启动指南

> 基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)  
> 开发: ViVi141 (747384120@qq.com) | 更新: 2025-10-12

## 🎯 一分钟快速体验（开发模式）

### 前置要求
- Python 3.10+
- Redis (可选，用于Celery)
- Node.js 18+ (前端开发需要)

### 后端快速启动

```bash
# 1. 进入后端目录
cd web/backend

# 2. 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux/Mac激活
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动后端服务（开发模式 - SQLite）
python app.py
```

**访问**:
- API文档: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/api/health
- 默认管理员: `admin` / `Admin@123`

### Celery Worker启动（可选）

如果需要运行异步任务：

```bash
# 新开一个终端
cd web/backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 启动Worker
celery -A celery_app worker --loglevel=info --pool=solo  # Windows需要--pool=solo

# 或者在Linux/Mac上
celery -A celery_app worker --loglevel=info --concurrency=4
```

**注意**: Windows上Celery需要使用`--pool=solo`参数

### 前端快速启动（待实现）

```bash
# 1. 创建Vue 3项目
cd web
pnpm create vite frontend --template vue

# 2. 进入前端目录
cd frontend

# 3. 安装依赖
pnpm install

# 4. 安装UI库和其他依赖
pnpm add element-plus @element-plus/icons-vue
pnpm add vue-router pinia
pnpm add axios
pnpm add echarts vue-echarts

# 5. 启动开发服务器
pnpm dev
```

访问: http://localhost:5173

---

## 📦 生产环境部署（Docker）

### 使用Docker Compose

```bash
# 1. 进入web目录
cd web

# 2. 复制环境配置
cp env.example .env

# 3. 编辑.env文件（重要！）
nano .env

# 必须修改的配置：
# - POSTGRES_PASSWORD=your_secure_password
# - REDIS_PASSWORD=your_redis_password
# - SECRET_KEY=your_random_secret_key_here
# - JWT_SECRET_KEY=your_jwt_secret_key_here

# 4. 启动所有服务
docker-compose up -d

# 5. 查看服务状态
docker-compose ps

# 6. 查看日志
docker-compose logs -f backend
```

### 生成安全密钥

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔑 默认账号

### 管理员账号
- **用户名**: `admin`
- **密码**: `Admin@123`

**⚠️ 重要**: 首次登录后立即修改密码！

### 普通用户
需要注册创建

---

## 📝 API测试

### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "email": "test@example.com"
  }'
```

### 2. 登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123456"
```

返回的`access_token`用于后续请求。

### 3. 获取用户信息

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. 创建任务

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个任务",
    "course_ids": ["123456"]
  }'
```

### 5. 启动任务

```bash
curl -X POST "http://localhost:8000/api/tasks/1/start" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔍 故障排查

### 后端无法启动

**问题**: `ModuleNotFoundError`

**解决**:
```bash
# 确保在虚拟环境中
pip install -r requirements.txt

# 检查Python版本
python --version  # 需要3.10+
```

### 数据库错误

**问题**: 数据库连接失败

**解决**:
```bash
# 检查数据库URL配置
# 开发模式默认使用SQLite，无需额外配置

# 如果使用PostgreSQL，检查连接字符串
echo $DATABASE_URL
```

### Celery无法启动

**问题**: `ConnectionError: Error connecting to Redis`

**解决**:
```bash
# 检查Redis是否运行
redis-cli ping  # 应该返回PONG

# Windows用户可以下载Redis for Windows
# 或者使用WSL2
```

**Windows Celery问题**:
```bash
# Windows上必须使用solo池
celery -A celery_app worker --loglevel=info --pool=solo
```

### 端口占用

**问题**: `Address already in use`

**解决**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## 📖 API文档

启动后端服务后，访问：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

所有API接口都有详细说明和交互式测试功能。

---

## 🎨 前端开发

### 推荐IDE设置

**VS Code插件**:
- Volar (Vue 3官方)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier

### 项目结构（推荐）

```
frontend/
├── src/
│   ├── views/              # 页面组件
│   │   ├── Login.vue       # 登录页
│   │   ├── Register.vue    # 注册页
│   │   ├── Dashboard.vue   # 用户仪表盘
│   │   ├── Tasks.vue       # 任务管理
│   │   ├── Config.vue      # 配置页面
│   │   └── Admin.vue       # 管理后台
│   ├── components/         # 通用组件
│   ├── api/                # API调用
│   │   └── index.ts        # API封装
│   ├── store/              # Pinia状态管理
│   │   └── user.ts         # 用户状态
│   ├── router/             # 路由配置
│   │   └── index.ts
│   └── utils/              # 工具函数
│       └── request.ts      # Axios封装
├── package.json
└── vite.config.ts
```

### API调用示例

```typescript
// src/api/index.ts
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 用户API
export const userAPI = {
  login: (username: string, password: string) => 
    request.post('/auth/login', `username=${username}&password=${password}`, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  
  register: (data: any) => 
    request.post('/auth/register', data),
  
  getProfile: () => 
    request.get('/auth/me'),
  
  updateConfig: (data: any) => 
    request.put('/user/config', data)
}

// 任务API
export const taskAPI = {
  getTasks: (params: any) => 
    request.get('/tasks', { params }),
  
  createTask: (data: any) => 
    request.post('/tasks', data),
  
  startTask: (id: number) => 
    request.post(`/tasks/${id}/start`),
  
  pauseTask: (id: number) => 
    request.post(`/tasks/${id}/pause`)
}
```

---

## 🎯 下一步

1. **完成用户配置** - 在前端添加超星账号配置
2. **创建任务** - 添加要学习的课程ID
3. **启动任务** - 开始自动学习
4. **查看进度** - 实时监控任务状态

---

## 📞 获取帮助

- **文档**: web/WEB_PLATFORM_GUIDE.md
- **部署指南**: web/DEPLOYMENT_GUIDE.md
- **GitHub Issues**: https://github.com/Samueli924/chaoxing/issues

---

**祝您使用愉快！** 🎉

