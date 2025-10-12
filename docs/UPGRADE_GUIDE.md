# 📦 升级指南

> 从v2.1.0升级到v2.2.0

---

## 🎯 升级概览

v2.2.0是一个**重大技术升级版本**，包含：
- 前端框架升级（Refine v4 → v5）
- 新增图形化数据库迁移功能
- 修复所有可修复的警告

---

## ⚠️ 兼容性说明

### 完全向后兼容 ✅

- ✅ 数据库结构不变
- ✅ API端点不变
- ✅ 配置文件不变
- ✅ 所有功能正常工作

### 前端变化

- React Router v6 → v7（自动兼容）
- Refine v4 → v5（API已更新）
- 新增管理员页面：数据库迁移

---

## 🚀 升级步骤

### 方法1：Git Pull（推荐）

如果您从GitHub克隆的项目：

```bash
# 1. 备份当前数据
cd web/backend/data
cp chaoxing.db chaoxing.db.backup

# 2. 拉取最新代码
cd C:\Users\ViVi141\Desktop\chaoxing
git pull origin main

# 3. 更新前端依赖
cd web/frontend
npm install

# 4. 重启服务
# 停止当前服务（Ctrl+C）
# 然后重新启动
cd ../backend
python app.py

# 新终端启动Celery
celery -A celery_app worker --loglevel=info

# 新终端启动前端
cd ../frontend
npm run dev
```

### 方法2：手动更新

如果您修改了大量代码：

#### 后端（无需更新）
```bash
# 后端代码向后兼容，无需修改
```

#### 前端更新

```bash
cd web/frontend

# 1. 更新依赖
npm install @refinedev/core@5.0.4 \
  @refinedev/antd@6.0.2 \
  @refinedev/react-router@2.0.1 \
  antd@5.27.4 \
  react-router-dom@7.0.2 \
  react-router@7.0.2 \
  @tanstack/react-query@5.81.5

# 2. 删除旧依赖
npm uninstall @refinedev/react-router-v6

# 3. 重新安装
npm install
```

#### 代码迁移（如果自定义了页面）

如果您自定义了前端页面，需要更新以下API：

**1. AuthProvider**
```typescript
// 旧代码
import { AuthBindings } from '@refinedev/core';
const authProvider: AuthBindings = { ... };

// 新代码
import { AuthProvider } from '@refinedev/core';
const authProvider: AuthProvider = { ... };
```

**2. useTable返回值**
```typescript
// 旧代码
const { tableQueryResult } = useTable();
tableQueryResult?.refetch();

// 新代码
const { query } = useTable();
query?.refetch();
```

**3. useShow返回值**
```typescript
// 旧代码
const { queryResult } = useShow();
const data = queryResult?.data;

// 新代码
const { query } = useShow();
const data = query?.data;
```

**4. dataProvider分页**
```typescript
// 旧代码
pagination: {
  current: 1,
  pageSize: 10
}

// 新代码（兼容两种方式）
pagination: {
  page: 1,        // 新
  current: 1,     // 兼容旧的
  perPage: 10,    // 新
  pageSize: 10    // 兼容旧的
}
```

**5. Ant Design组件**
```typescript
// 旧代码
<Tabs>
  <TabPane tab="标签1" key="1">内容1</TabPane>
  <TabPane tab="标签2" key="2">内容2</TabPane>
</Tabs>

// 新代码
<Tabs items={[
  { key: '1', label: '标签1', children: '内容1' },
  { key: '2', label: '标签2', children: '内容2' },
]} />
```

---

## 🆕 新功能使用

### 图形化数据库迁移

升级后，管理员可以通过Web界面迁移数据库：

1. 登录管理员账号
2. 访问：`管理员控制台 > 数据库迁移`
3. 配置PostgreSQL和Redis连接
4. 点击"测试连接"
5. 开始迁移
6. 等待完成并重启服务

详细文档：[DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)

---

## 🔧 常见问题

### Q1: 升级后前端报错怎么办？

**A**: 清除缓存并重新安装：

```bash
cd web/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Q2: 升级后看到警告怎么办？

**A**: 预期剩余2个第三方库警告（不影响功能）：
- Menu children deprecated（来自Refine内部）
- findDOMNode deprecated（来自Ant Design内部）

这些需要等待库作者更新。

### Q3: 如何回滚到v2.1.0？

**A**: 
```bash
git checkout v2.1.0
cd web/frontend
npm install
```

### Q4: 数据会丢失吗？

**A**: 不会。升级前建议备份数据库：
```bash
cd web/backend/data
cp chaoxing.db chaoxing.db.backup
```

### Q5: 需要修改配置文件吗？

**A**: 不需要。所有配置向后兼容。

---

## 🎯 验证升级成功

### 1. 启动服务
```bash
# 后端
cd web/backend
python app.py

# Celery
celery -A celery_app worker --loglevel=info

# 前端
cd web/frontend
npm run dev
```

### 2. 检查浏览器控制台
- 打开 http://localhost:5173
- 按F12打开控制台
- **预期**: 仅有0-2个第三方库警告

### 3. 测试功能
- [ ] 登录功能正常
- [ ] 任务创建正常
- [ ] 实时进度正常
- [ ] 管理员控制台正常
- [ ] 🆕 数据库迁移页面可访问

---

## 📊 升级收益

### 性能提升
- ✅ React Router v7性能优化
- ✅ Refine v5减少重渲染
- ✅ React Query优化数据缓存

### 开发体验
- ✅ TypeScript错误清零
- ✅ 更少的警告信息
- ✅ 更现代的API

### 功能增强
- ✅ 图形化数据库迁移
- ✅ 更好的错误处理
- ✅ 更详细的日志

### 长期维护
- ✅ 使用最新稳定版本
- ✅ 更好的社区支持
- ✅ 更快的安全更新

---

## 🆘 获取帮助

如果升级遇到问题：

1. **查看文档**: 
   - [CHANGELOG.md](CHANGELOG.md)
   - [REFINE_V5_UPGRADE_COMPLETE.md](../REFINE_V5_UPGRADE_COMPLETE.md)

2. **提交Issue**: https://github.com/ViVi141/chaoxing/issues

3. **邮件联系**: 747384120@qq.com

---

## 🎊 升级完成

恭喜您升级到v2.2.0！

您的系统现在运行在：
- ✅ Refine v5架构
- ✅ React Router v7
- ✅ Ant Design 5.27（最新）
- ✅ 零TypeScript错误
- ✅ 最少的警告

享受最新的技术栈和新功能吧！ 🚀

---

**最后更新**: 2025-10-13  
**版本**: v2.1.0 → v2.2.0

