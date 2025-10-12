# :bar_chart: 项目总览

> **项目状态：✅ 100% 完成！**  
> Web版本已完全集成命令行版本的所有核心功能，包括视频、文档、测验、阅读等所有任务点的自动完成。

## 项目名称
**超星学习通自动化完成任务点（增强版）**

## :link: 项目信息
- **原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)
- **增强版本**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)
- **增强开发**: ViVi141 (747384120@qq.com)
- **更新日期**: 2025-10-12
- **项目状态**: ✅ 已完成
- **开源协议**: GPL-3.0 License

## 提供两种使用方式

### 1. 命令行版本（单用户）
- 本地运行，配置文件或命令行参数
- 适合个人使用
- 快速启动：`python main.py -c config.ini`

### 2. Web多用户平台（生产级）
- 多用户注册登录、任务管理、实时监控
- 适合团队使用或对外提供服务
- 快速启动：`cd web && docker-compose up -d`

---

## 核心功能

### 命令行版
✅ 视频/文档/测验自动完成  
✅ 倍速播放（1.0-2.0倍）  
✅ 5种题库集成  
✅ 3种通知方式  
✅ 配置加密存储  
✅ 日志自动脱敏  

### Web平台版
✅ 100%命令行功能（视频/文档/测验/阅读）  
✅ 用户注册/登录（JWT认证）  
✅ 任务管理（创建/启动/暂停/取消）  
✅ 实时进度推送（WebSocket）  
✅ 管理员后台（用户/任务/日志）  
✅ 异步任务队列（Celery）  
✅ 安装向导（Web界面配置）  
✅ 零依赖部署（SQLite+文件队列）  
✅ Docker一键部署（两种模式）  

---

## 技术栈

### 后端
- **命令行**: Python 3.10+ + requests + beautifulsoup4
- **Web平台**: FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + Celery

### 前端（Web平台）
- Vue 3 + Element Plus + Pinia + Vue Router + ECharts + WebSocket

### 部署
- Docker + Docker Compose + Nginx

---

## 项目统计

### 代码量
- 命令行版：约2500行（Python）
- Web后端：约4000行（Python）
- Web前端：约3200行（Vue/JS）
- **总计**：约9700行

### 文件数
- Python文件：40个
- Vue/JS文件：18个
- 配置文件：15个
- 文档文件：20+个
- **总计**：93个

### API接口（Web平台）
- 认证接口：5个
- 用户接口：5个
- 任务接口：9个
- 管理员接口：9个
- 安装向导接口：3个
- WebSocket接口：1个
- **总计**：32个

### 数据库表（Web平台）
- users - 用户表
- user_configs - 用户配置表
- tasks - 任务表
- task_logs - 任务日志表
- system_logs - 系统日志表
- **总计**：5个表

---

## 快速开始

### 命令行版（3步）
```bash
git clone https://github.com/ViVi141/chaoxing
cd chaoxing
pip install -r requirements.txt
python main.py -c config.ini
```

### Web平台 - 简单模式（零依赖，3步）
```bash
cd web
python backend/app.py                              # 终端1
celery -A backend.celery_app worker --loglevel=info  # 终端2
cd frontend && npm run dev                         # 终端3
```
访问 http://localhost:5173 完成安装向导

### Web平台 - Docker部署（1步）
```bash
cd web
docker-compose -f docker-compose.simple.yml up -d
```
访问 http://localhost:3000 完成安装向导

---

## 文档导航

### 主文档
| 文档 | 说明 | 链接 |
|------|------|------|
| README.md | 项目主文档 | [查看](../README.md) |
| QUICK_START.md | 快速启动指南 | [查看](../QUICK_START.md) |
| docs/INDEX.md | 文档索引 | [查看](INDEX.md) |

### 项目文档（docs/）
| 文档 | 说明 | 链接 |
|------|------|------|
| SUMMARY.md | 项目总览 | 本文档 |
| PROJECT_STRUCTURE.md | 项目结构说明 | [查看](PROJECT_STRUCTURE.md) |
| DEPLOYMENT_MODES.md | 部署模式说明 | [查看](DEPLOYMENT_MODES.md) |
| CHANGELOG.md | 更新日志 | [查看](CHANGELOG.md) |
| CREDITS.md | 贡献与致谢 | [查看](CREDITS.md) |

### Web平台文档（web/）
| 文档 | 说明 | 链接 |
|------|------|------|
| web/README.md | Web平台说明 | [查看](../web/README.md) |
| web/START_GUIDE.md | 启动指南 | [查看](../web/START_GUIDE.md) |
| web/DEPLOYMENT_GUIDE.md | 部署指南 | [查看](../web/DEPLOYMENT_GUIDE.md) |
| web/DOCKER_DEPLOYMENT.md | Docker部署 | [查看](../web/DOCKER_DEPLOYMENT.md) |

---

## 核心特性对比

| 特性 | 命令行版 | Web平台 |
|------|---------|---------|
| 用户数 | 单用户 | 多用户 |
| 界面 | 命令行 | Web界面 |
| 部署 | 本地运行 | 服务器部署 |
| 认证 | 配置文件 | JWT令牌 |
| 任务管理 | 命令行 | Web界面 |
| 实时监控 | 命令行输出 | WebSocket |
| 数据持久化 | 配置文件 | 数据库 |
| 扩展性 | 低 | 高 |
| 适用场景 | 个人使用 | 团队/服务 |

---

## 使用场景

### 命令行版适用于：
- 个人学习刷课
- 本地快速运行
- 不需要界面
- 简单配置即用

### Web平台适用于：
- 多人同时使用
- 需要管理和监控
- 对外提供服务
- 需要权限控制

---

## 安全特性

- 🔐 密码bcrypt加密
- 🔐 配置文件加密存储
- 🔐 JWT令牌认证
- 🔐 日志自动脱敏
- 🔐 SQL注入防护
- 🔐 XSS/CSRF保护

---

## 性能指标

### 命令行版
- 启动时间：<1秒
- 内存占用：~50MB
- CPU占用：低

### Web平台（小规模）
- 支持用户：50-100人
- 并发任务：10-20个
- 响应时间：<100ms
- 推荐配置：2核4GB

---

## 开源协议

GPL-3.0 License

- ✅ 允许开源/免费使用
- ✅ 允许修改和衍生
- ❌ 禁止闭源商业使用
- ❌ 禁止用于盈利

---

## 联系方式

- **原项目**: https://github.com/Samueli924/chaoxing
- **增强版本**: https://github.com/ViVi141/chaoxing
- **开发者**: ViVi141 (747384120@qq.com)
- **Issues**: https://github.com/ViVi141/chaoxing/issues

---

**最后更新**: 2025-10-12

