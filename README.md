# 超星学习通自动化完成任务点（增强版）

<p align="center">
  <a href="https://github.com/Samueli924/chaoxing"><img src="https://img.shields.io/github/stars/Samueli924/chaoxing" alt="Stars" /></a>
  <a href="https://github.com/ViVi141/chaoxing"><img src="https://img.shields.io/badge/version-2.2.1-blue" alt="Version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-green" alt="License" /></a>
  <img src="https://img.shields.io/badge/Refine-v5-orange" alt="Refine v5" />
  <img src="https://img.shields.io/badge/React_Router-v7-blue" alt="React Router v7" />
</p>

> 基于[Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)的增强版本，提供命令行和Web两种使用方式
> 
> 🆕 **v2.2.1更新**: 新增5种题库（含硅基流动AI）+ 4种通知方式（含SMTP邮件）

---

## ✨ 特性

### 命令行版
- ✅ 视频/音频自动播放（1.0-2.0倍速）
- ✅ 文档自动阅读
- ✅ 章节测验自动答题
- ✅ 5种题库支持（含AI大模型）
- ✅ 4种通知方式（含SMTP邮件）
- ✅ 配置文件加密
- ✅ 日志自动脱敏

### Web平台版
- ✅ 多用户注册/登录系统
- ✅ 任务管理（创建/启动/暂停/取消/重试）
- ✅ 实时进度展示（WebSocket）
- ✅ 任务详细日志查看
- ✅ 管理员后台（系统配置/用户管理）
- ✅ 零依赖部署（SQLite+文件队列）
- 🆕 **5种题库**（言溪/LIKE/TikuAdapter/AI/硅基流动）
- 🆕 **4种通知**（Server酱/Qmsg/Bark/SMTP邮件）
- 🆕 **图形化数据库迁移**（SQLite → PostgreSQL + Redis）

---

## 🚀 快速开始

### Web平台（推荐）

**一键启动（Windows）：**
```batch
启动Refine完整版.bat
```

**手动启动：**
```bash
# 终端1 - 后端
cd web/backend
python app.py

# 终端2 - Celery
cd web/backend  
celery -A celery_app worker --loglevel=info

# 终端3 - 前端
cd web/frontend
npm run dev
```

访问：http://localhost:5173

### 命令行版

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py -c config.ini
```

---

## 📦 安装要求

- **Python**: 3.10 / 3.11 / 3.12
- **Node.js**: 18+ (Web版)
- **数据库**: SQLite (默认) / PostgreSQL (可选)
- **消息队列**: 文件系统 (默认) / Redis (可选)

---

## 📚 文档

- **快速开始**: [docs/QUICK_START.md](docs/QUICK_START.md)
- **新增功能**: [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md) ⚡
- **文档索引**: [docs/INDEX.md](docs/INDEX.md)
- **API文档**: [docs/API.md](docs/API.md)
- **架构说明**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **配置指南**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **安全指南**: [docs/SECURITY.md](docs/SECURITY.md)
- **常见问题**: [docs/FAQ.md](docs/FAQ.md)

---

## 🎯 使用场景

### 个人使用
- 使用**命令行版** + **硅基流动AI** ⚡
- 简单快速，成本低，效果好

### 小团队(<50人)
- 使用**Web平台简单模式** + **言溪/LIKE题库**
- 零依赖部署，易于管理

### 大规模部署(>50人)
- 使用**Web平台标准模式** + **AI大模型** + Docker
- 高性能，支持集群

---

## 🔐 安全特性

- ✅ JWT令牌认证
- ✅ bcrypt密码哈希
- ✅ 数据加密存储
- ✅ 用户数据隔离
- ✅ 权限严格控制
- ✅ 日志自动脱敏

---

## 📊 技术栈

### 后端
- FastAPI 0.115.0
- SQLAlchemy 2.0.35
- Celery 5.4.0
- WebSocket 13.1

### 前端（v2.2.0更新）
- React 18.3.1
- **Refine 5.0.4** 🆕
- **Ant Design 5.27.4** ⬆️
- **React Router 7.0.2** 🆕
- Vite 5.4.10

---

## ⚖️ 开源协议

GPL-3.0 License

- ✅ 允许开源/免费使用
- ✅ 允许修改和衍生
- ❌ 禁止闭源商业使用
- ❌ 禁止用于盈利

---

## 🙏 致谢

- 原项目：[Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)
- 增强开发：ViVi141 (747384120@qq.com)

---

## 🆕 v2.2.0 & v2.2.1 更新内容

### 技术栈升级
- ✅ Refine v4 → **v5**（大版本升级）
- ✅ React Router v6 → **v7**（大版本升级）
- ✅ Ant Design 5.21 → **5.27**（最新稳定版）
- ✅ 新增 React Query 5.x（现代化状态管理）

### 新增功能
- ✅ **5种题库支持**
  - 言溪题库（TikuYanxi）
  - LIKE知识库（TikuLike）
  - TikuAdapter（开源）
  - AI大模型（OpenAI兼容）
  - 硅基流动AI（SiliconFlow）⚡ 推荐
  
- ✅ **4种通知方式**
  - Server酱（多平台推送）
  - Qmsg酱（QQ推送）
  - Bark（iOS推送）
  - SMTP邮件 📧 新增
  
- ✅ **图形化数据库迁移系统**
  - Web界面一键迁移SQLite到PostgreSQL
  - 实时进度显示
  - 自动备份和验证
  - 跨平台重启脚本

### 代码质量
- ✅ TypeScript错误：0个
- ✅ 修复75%的第三方库警告
- ✅ API迁移到最新标准

### 详细说明
查看完整功能说明：[docs/NEW_FEATURES.md](docs/NEW_FEATURES.md)

---

## 📞 技术支持

- **原项目Issues**: https://github.com/Samueli924/chaoxing/issues
- **增强版Issues**: https://github.com/ViVi141/chaoxing/issues
- **邮箱**: 747384120@qq.com
- **数据库迁移文档**: [docs/DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md)

---

**⭐ 觉得有帮助？给个Star吧！**
