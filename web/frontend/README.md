# 超星学习通管理平台 - Refine版本

基于 React + Refine + Ant Design 的现代化Web管理界面

## 🚀 快速启动

### 方式1：使用启动脚本（推荐）

```bash
.\启动Refine.bat
```

### 方式2：手动启动

```bash
npm install
npm run dev
```

## 📦 技术栈

- **前端框架**: React 18
- **UI框架**: Ant Design 5
- **管理框架**: Refine 4
- **构建工具**: Vite 5
- **路由**: React Router v6
- **HTTP**: Axios

## 📁 项目结构

```
src/
├── main.tsx              # 入口文件
├── App.tsx               # 主应用（Refine配置）
├── providers/            # 提供者
│   ├── authProvider.ts   # 认证提供者
│   └── dataProvider.ts   # 数据提供者
└── pages/                # 页面组件
    ├── dashboard/        # 仪表盘
    ├── users/            # 用户管理
    ├── tasks/            # 任务管理
    └── config/           # 配置管理
```

## 🎯 功能特性

- ✅ JWT认证系统
- ✅ 用户管理（CRUD）
- ✅ 任务管理（创建/监控）
- ✅ 配置管理
- ✅ 响应式设计
- ✅ 中文界面
- ⏳ WebSocket实时更新（开发中）

## 🔧 配置

后端API地址：`http://localhost:8000/api`

如需修改，编辑 `src/providers/dataProvider.ts`

## 📝 使用说明

1. 启动后端服务
2. 启动Refine前端
3. 访问 http://localhost:5173
4. 登录：admin / Admin@123

## ⚙️ 开发命令

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产构建
```

## 📊 进度

- [x] 项目基础结构
- [x] 认证系统
- [x] 数据提供者
- [x] 用户管理页面
- [x] 任务管理页面
- [x] 配置管理页面
- [ ] WebSocket实时更新
- [ ] 完整测试

---

**版本**: 2.0.0  
**基于**: Refine 4 + React 18 + Ant Design 5

