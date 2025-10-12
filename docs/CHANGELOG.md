# 📝 更新日志

## v2.2.1 (2025-10-12)

### ✨ 新功能

#### 5种题库全面支持（Web + 命令行）
- ✅ **言溪题库**（TikuYanxi） - Token-based
- ✅ **LIKE知识库**（TikuLike） - Token-based + AI模型
- ✅ **TikuAdapter** - 开源自建服务
- ✅ **AI大模型** - OpenAI兼容API（DeepSeek、Moonshot等）
- ✅ **硅基流动AI**（SiliconFlow）⚡ - 性价比最高，推荐使用

#### 4种通知方式完整支持
- ✅ **Server酱** - 多平台推送
- ✅ **Qmsg酱** - QQ推送
- ✅ **Bark** - iOS推送
- ✅ **SMTP邮件** 📧 - 新增支持（Gmail、QQ、163等）

#### Web平台配置界面
- ✅ 题库配置页面 - 动态表单，根据选择显示对应配置项
- ✅ 通知配置页面 - 支持所有通知方式的可视化配置
- ✅ 系统配置页面 - 完善管理员系统设置标签页

### 🔧 技术实现

#### 后端更新
- ✅ `api/notification.py` - 新增SMTP邮件通知类（+200行）
  - 支持TLS/SSL加密
  - HTML格式美化邮件
  - 完整错误处理
- ✅ `web/backend/schemas.py` - 扩展题库和通知配置字段
  - TikuConfig：支持所有AI题库配置
  - NotificationConfig：支持SMTP配置

#### 前端更新
- ✅ `web/frontend/src/pages/config/full.tsx` - 配置界面重构（+300行）
  - 5种题库配置表单
  - 4种通知配置表单
  - 动态渲染、智能提示
- ✅ `web/frontend/src/pages/admin/SystemConfig.tsx` - 系统设置完善
  - 功能列表展示
  - 系统信息显示

#### 配置文件更新
- ✅ `config_template.ini` - 添加SMTP配置示例
- ✅ 支持硅基流动AI完整配置

### 📚 文档新增
- ✅ `docs/NEW_FEATURES.md` - 详细功能说明文档（320行）
  - 5种题库完整配置指南
  - 4种通知方式使用说明
  - 常见问题和故障排查
  - 使用场景推荐

### 🎯 代码修改统计
- **5个文件**更新
- **500+行**代码新增
- **1个新文档**（NEW_FEATURES.md）
- **TypeScript错误**: 0个
- **代码质量**: 通过所有检查

### 💡 推荐配置
```ini
[tiku]
provider=SiliconFlow
siliconflow_key=sk-你的密钥
siliconflow_model=deepseek-ai/DeepSeek-R1

[notification]
provider=SMTP
smtp_host=smtp.gmail.com
smtp_port=587
smtp_username=your_email@gmail.com
smtp_password=your_app_password
smtp_to_email=recipient@example.com
```

---

## v2.2.0 (2025-10-13)

### 🎉 重大技术升级

#### 前端架构现代化（3个大版本升级）
- ✅ **Refine 4.53.0 → 5.0.4**（v5架构）
- ✅ **React Router 6.27.0 → 7.0.2**（v7架构）
- ✅ **@refinedev/antd 5.42.0 → 6.0.2**（v6架构）
- ✅ **Ant Design 5.21.6 → 5.27.4**（最新稳定版）
- ✅ 新增 **React Query 5.81.5**（现代状态管理）

### ✨ 新功能

#### 图形化数据库迁移系统
- ✅ Web管理界面（管理员专用）
- ✅ SQLite → PostgreSQL一键迁移
- ✅ 实时进度显示（6步骤进度条）
- ✅ 连接测试机制
- ✅ 自动备份验证
- ✅ 跨平台重启脚本（Windows/Linux）
- ✅ 详细迁移文档

#### 后端迁移API（8个端点）
- `GET /api/migration/status` - 获取当前配置和迁移状态
- `POST /api/migration/test-postgres` - 测试PostgreSQL连接
- `POST /api/migration/test-redis` - 测试Redis连接
- `POST /api/migration/start` - 启动迁移
- `GET /api/migration/progress` - 获取迁移进度
- `POST /api/migration/restart` - 重启服务
- `POST /api/migration/rollback` - 回滚到SQLite
- `POST /api/migration/reset` - 重置迁移状态

### 🔧 API重构（Refine v5兼容）

#### Breaking Changes修复
- ✅ `AuthBindings` → `AuthProvider`
- ✅ `tableQueryResult` → `query`（useTable返回值）
- ✅ `queryResult` → `query`（useShow返回值）
- ✅ `pagination.current` → `pagination.page`
- ✅ `pagination.pageSize` → `pagination.perPage`
- ✅ `ThemedLayoutV2` → `ThemedLayout`
- ✅ `ThemedTitleV2` → `ThemedTitle`
- ✅ `@refinedev/react-router-v6` → `@refinedev/react-router`

#### 组件API更新（Ant Design 5.x）
- ✅ `Tabs.TabPane` → `Tabs items`
- ✅ `Collapse.Panel` → `Collapse items`
- ✅ `Steps.Step` → `Steps items`

### 🐛 Bug修复

#### 代码质量
- ✅ TypeScript错误：**100%修复**（0个错误）
- ✅ Linter警告：**100%清理**（0个警告）
- ✅ 第三方库警告：**75%修复**（6/8个已消除）
- ✅ 清理所有未使用的导入

#### 浏览器兼容
- ✅ React Router v7警告修复
- ✅ Private Network Access警告修复（改用localhost）
- ✅ Menu/Collapse/Tabs弃用警告修复

### 📦 依赖更新

#### 前端
```json
{
  "@refinedev/core": "4.53.0 → 5.0.4",
  "@refinedev/antd": "5.42.0 → 6.0.2",
  "@refinedev/react-router": "4.6.0 → 2.0.1",
  "antd": "5.21.6 → 5.27.4",
  "react-router-dom": "6.27.0 → 7.0.2",
  "@tanstack/react-query": "新增 5.81.5"
}
```

### 🔒 安全优化
- ✅ 禁用Vite的局域网暴露（改为localhost only）
- ✅ 提供HTTPS配置示例
- ✅ 数据库迁移过程自动备份

### 📚 文档完善
- ✅ [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md) - 数据库迁移详细指南
- ✅ [REFINE_V5_UPGRADE_COMPLETE.md](../REFINE_V5_UPGRADE_COMPLETE.md) - 升级完整报告
- ✅ 更新所有README和文档
- ✅ 新增HTTPS配置示例

### 🎯 代码修改统计
- **13个文件**更新
- **200+行**代码重构
- **8个新API**端点
- **1个新管理页面**（DatabaseMigration）
- **2个新后端模块**（database_migration.py, routes/migration.py）
- **2个新脚本**（restart_service.bat/sh）

### 🏆 成就解锁
- ✅ 使用业界最新技术栈
- ✅ 零TypeScript错误
- ✅ 最小化第三方库警告
- ✅ 完整的数据库迁移方案
- ✅ 生产级代码质量

---

## v2.1.0 (2025-10-12)

### 🎉 重大更新
- 全面升级所有依赖到最新稳定版
- 后端依赖40+个包升级
- 前端依赖14个包升级

### ✨ 新功能
- 添加任务恢复(resume)接口
- 实现任务持久化机制（后端重启自动恢复）
- 任务详细日志实时展示
- WebSocket实时推送任务进度

### 🔒 安全增强
- 完整的权限审计
- 防横向攻击机制
- 防纵向攻击机制
- 添加安全测试套件

### 🐛 Bug修复
- 修复任务resume接口404错误
- 修复Ant Design组件弃用警告
- 修复Celery hostname警告
- 修复SQLAlchemy 2.0异步关系加载问题

### 📦 依赖升级
- FastAPI: 0.104.1 → 0.115.0
- SQLAlchemy: 2.0.23 → 2.0.35
- Ant Design: 5.12.0 → 5.21.6
- React: 18.2.0 → 18.3.1
- Vite: 5.0.8 → 5.4.10
- Pydantic: 2.5.0 → 2.9.2
- WebSockets: 12.0 → 13.1

---

## v2.0.0 (2025-10-11)

### 🎉 Web平台完整版发布
- FastAPI后端 + React前端
- 多用户管理系统
- 实时任务监控
- WebSocket实时通信
- Celery异步任务队列

### ✨ 核心功能
- 用户注册/登录系统
- 任务管理（创建/启动/暂停/取消）
- 实时进度展示
- 管理员后台
- 邮箱验证
- 密码重置

---

## v1.0.0 (原项目)

基于 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)

### 功能
- 命令行版自动刷课
- 视频/文档/测验自动完成
- 题库集成
- 通知推送

