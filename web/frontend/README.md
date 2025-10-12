# 前端项目说明

> 基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)

## 技术栈

- **框架**: Vue 3.3+ (Composition API)
- **UI库**: Element Plus 2.4+
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios
- **图表**: ECharts 5.4+
- **构建工具**: Vite 5.0
- **语言**: JavaScript

## 快速开始

### 安装依赖

```bash
# 使用pnpm（推荐）
pnpm install

# 或使用npm
npm install

# 或使用yarn
yarn install
```

### 开发模式

```bash
pnpm dev
# 访问: http://localhost:5173
```

### 生产构建

```bash
pnpm build
# 输出目录: dist/
```

### 预览生产构建

```bash
pnpm preview
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API调用
│   │   ├── index.js      # API接口定义
│   │   └── request.js    # Axios封装
│   ├── assets/            # 资源文件
│   ├── components/        # 通用组件
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── store/             # Pinia状态管理
│   │   └── user.js
│   ├── views/             # 页面组件
│   │   ├── Setup.vue     # 安装向导
│   │   ├── Login.vue     # 登录注册
│   │   ├── Dashboard.vue # 用户仪表盘
│   │   ├── Tasks.vue     # 任务管理
│   │   ├── Config.vue    # 配置页面
│   │   └── Admin/        # 管理员后台
│   │       ├── Layout.vue
│   │       ├── Dashboard.vue
│   │       ├── Users.vue
│   │       ├── Tasks.vue
│   │       └── Logs.vue
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
├── package.json           # 项目配置
└── README.md              # 本文档
```

## 核心功能

### 安装向导 ✅
- 首次访问自动引导
- 管理员账号配置
- 系统基础配置
- 完成后自动跳转

### 用户功能 ✅
- 用户注册/登录
- 个人配置管理
  - 超星账号配置
  - 学习配置（倍速等）
  - 题库配置
  - 通知配置
- 任务管理
  - 创建任务
  - 启动/暂停/取消
  - 查看日志
  - 实时进度

### 管理员功能 ✅
- 数据统计仪表盘
- 用户管理
- 任务监控
- 系统日志查看

## 环境变量

创建 `.env` 文件：

```env
# API地址
VITE_API_URL=http://localhost:8000/api

# WebSocket地址
VITE_WS_URL=ws://localhost:8000
```

## 已实现的页面

- [x] Setup.vue - 安装向导（引导初始配置）
- [x] Login.vue - 登录注册页面
- [x] Dashboard.vue - 用户仪表盘
- [x] Tasks.vue - 任务管理
- [x] Config.vue - 个人配置
- [x] Admin/Layout.vue - 管理员布局
- [x] Admin/Dashboard.vue - 管理员仪表盘

## 待实现的页面

- [ ] Admin/Users.vue - 用户管理
- [ ] Admin/Tasks.vue - 任务监控
- [ ] Admin/Logs.vue - 系统日志
- [ ] NotFound.vue - 404页面
- [ ] WebSocket实时通信完善

## 路由配置

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| /setup | Setup | 安装向导 | 公开 |
| /login | Login | 登录注册 | 公开 |
| /dashboard | Dashboard | 用户仪表盘 | 需登录 |
| /tasks | Tasks | 任务管理 | 需登录 |
| /config | Config | 个人配置 | 需登录 |
| /admin/dashboard | Admin/Dashboard | 管理员仪表盘 | 管理员 |
| /admin/users | Admin/Users | 用户管理 | 管理员 |
| /admin/tasks | Admin/Tasks | 任务监控 | 管理员 |
| /admin/logs | Admin/Logs | 系统日志 | 管理员 |

## API调用示例

```javascript
import { taskAPI } from '@/api'

// 获取任务列表
const response = await taskAPI.getTasks({ page: 1, page_size: 20 })

// 创建任务
await taskAPI.createTask({
  name: '我的任务',
  course_ids: ['123456']
})

// 启动任务
await taskAPI.startTask(taskId)
```

## 状态管理

使用Pinia管理全局状态：

```javascript
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 用户信息
userStore.user
userStore.isLoggedIn
userStore.isAdmin

// 方法
userStore.setToken(token)
userStore.setUser(user)
userStore.logout()
```

## Docker部署

### Dockerfile

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 构建命令

```bash
docker build -t chaoxing-frontend .
docker run -p 3000:80 chaoxing-frontend
```

## 开发建议

### VS Code插件
- Volar (Vue 3官方)
- ESLint
- Prettier
- Auto Import

### 代码规范
- 使用Composition API
- 使用setup语法糖
- 响应式数据使用ref/reactive
- 遵循Vue 3最佳实践

## 贡献

欢迎提交Issue和Pull Request！

---

**开发者**: ViVi141 (747384120@qq.com)  
**最后更新**: 2025-10-12
