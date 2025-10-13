# 超星学习通自动化完成任务点（增强版）

<p align="center">
  <a href="https://github.com/ViVi141/chaoxing"><img src="https://img.shields.io/badge/version-2.3.0-blue" alt="Version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-green" alt="License" /></a>
  <img src="https://img.shields.io/badge/Refine-v5-orange" alt="Refine v5" />
  <img src="https://img.shields.io/badge/React_Router-v7-blue" alt="React Router v7" />
  <img src="https://img.shields.io/badge/Vite-v7-purple" alt="Vite v7" />
  <img src="https://img.shields.io/badge/Tests-14_passing-brightgreen" alt="Tests" />
</p>

> 基于[Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)的增强版本，提供命令行和Web两种使用方式
> 
> 🆕 **v2.3.0更新**: 测试框架 + CI/CD + API限流 + 数据备份 + 守护进程完整方案

---

## ⚠️ 声明

> 本项目采用 **GPL-3.0** 开源协议，完全免费使用。  
> 禁止任何形式的强制收费或未授权商业化运营。

---

## ✨ 特性

### 命令行版
- ✅ 视频/音频自动播放（1.0-2.0倍速）
- ✅ 文档自动阅读
- ✅ 章节测验自动答题
- ✅ 6种题库支持（含AI大模型）
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
- ✅ **6种题库**（言溪/LIKE/TikuAdapter/AI/DeepSeek/硅基流动）
- ✅ **4种通知**（Server酱/Qmsg/Bark/SMTP邮件）
- ✅ **图形化数据库迁移**（SQLite → PostgreSQL + Redis）
- 🆕 **自动化测试**（pytest + 14个测试用例）
- 🆕 **CI/CD流程**（GitHub Actions + 自动部署）
- 🆕 **API限流**（多级防护 + 暴力破解防护）
- 🆕 **数据备份**（自动化脚本 + 定时任务）
- 🆕 **守护进程**（6种部署方案 + 统一管理）

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

### 快速入门
- [快速开始](docs/QUICK_START.md) - 5分钟快速上手
- [完整文档索引](docs/INDEX.md) - 所有文档列表

### v2.3.0新增 🆕
- [守护进程部署](docs/DAEMON.md) - 生产环境部署（systemd/supervisor/Docker）
- [测试指南](tests/README.md) - 自动化测试框架
- [守护进程命令](DAEMON_QUICK_REF.md) - 快速参考

### 更多文档
- [更新日志](docs/CHANGELOG.md) - 版本历史（含v2.3.0详情）
- [常见问题](docs/FAQ.md) - FAQ
- [配置指南](docs/CONFIGURATION.md) - 详细配置

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
- ✅ 权限严格控制（RBAC）
- ✅ 日志自动脱敏
- ✅ CORS动态配置（生产环境限制）
- ✅ LIKE注入防护
- ✅ SQL注入防护（ORM）
- ✅ XSS防护（输入清理）

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

## 🆕 版本更新

## 📅 更新日志

### v2.3.0 (2025-10-13) 🚀 生产就绪版
- ✅ **自动化测试框架**（pytest + 14个测试用例）
- ✅ **CI/CD流程**（GitHub Actions自动化）
- ✅ **API限流防护**（多级限流 + 暴力破解防护）
- ✅ **数据备份方案**（自动化脚本 + 双平台）
- ✅ **守护进程部署**（6种方案 + 统一管理）
- ✅ **代码优化**（清理冗余代码 + 性能提升）

### v2.2.3 (2025-10-13)
- 在线配置管理 + 用户管理增强
- 仪表盘数据、任务暂停修复  
- Vite 7 + 依赖更新 + 开源声明

### v2.2.2 (2025-10-12)
- 6种题库（DeepSeek/硅基流动）
- SMTP邮件 + 任务自动恢复

[完整日志](docs/CHANGELOG.md)

---

## 📞 支持

[Issues](https://github.com/ViVi141/chaoxing/issues) | [原始项目](https://github.com/Samueli924/chaoxing)
