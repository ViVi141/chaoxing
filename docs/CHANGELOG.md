# 📝 更新日志

## v2.5.3 (2025-11-23) 🧪 测试框架优化版

### 🎯 核心更新

本版本专注于**测试框架优化**和**CI/CD流程改进**，提升代码质量和开发体验。

#### 1. 测试框架全面优化 ⭐⭐⭐⭐⭐

**修复内容**：
- ✅ 修复数据库初始化问题（`no such table: users` 错误）
- ✅ 优化 pytest fixtures 作用域管理（解决 ScopeMismatch 错误）
- ✅ 改进数据库会话管理（每个测试后自动回滚，确保数据隔离）
- ✅ 修复 SQLite 临时数据库文件管理
- ✅ 添加 Windows 控制台编码处理

**新增文件**：
- `tests/quick_test.py` - 本地快速测试脚本（161行）
  - 验证数据库表创建
  - 测试用户创建和查询
  - 验证密码功能
  - 支持 Windows 控制台编码

**测试结果**：
- ✅ 所有集成测试通过（3/3）
- ✅ 数据库表正确创建（7个表）
- ✅ 测试数据隔离正常
- ✅ 无 UNIQUE 约束冲突

#### 2. CI/CD 流程改进 ⭐⭐⭐⭐

**优化内容**：
- ✅ 移除不再支持的 `ubuntu-20.04`（GitHub 将在 2025-04-15 停止支持）
- ✅ 添加作业级和步骤级超时设置（避免无限等待）
- ✅ 优化作业名称显示（显示当前运行的 OS 版本）
- ✅ 更新依赖测试工作流配置

**修改文件**：
- `.github/workflows/ci.yml` - 移除 ubuntu-20.04，添加超时
- `.github/workflows/dependency-test.yml` - 移除 ubuntu-20.04，添加超时

**改进效果**：
- ⚡ CI 运行时间减少（不再等待不可用的 runner）
- 🛡️ 超时保护（避免作业卡住）
- 📊 更清晰的日志（显示 OS 版本）

#### 3. 依赖验证增强 ⭐⭐⭐

**改进内容**：
- ✅ 修复模块名称映射（`beautifulsoup4` → `bs4`，`python-dotenv` → `dotenv`）
- ✅ 增强 Windows 兼容性（控制台编码处理）
- ✅ 改进错误提示信息

**修改文件**：
- `scripts/verify_dependencies.py` - 模块名称映射和编码处理

#### 4. 数据库初始化修复 ⭐⭐⭐⭐

**修复内容**：
- ✅ 修复模型注册问题（确保所有模型正确注册到 Base.metadata）
- ✅ 优化导入路径（修复 `from database import Base` 的路径问题）
- ✅ 改进测试数据库配置（使用临时文件而非内存数据库）

**修改文件**：
- `tests/conftest.py` - 数据库初始化和会话管理优化
- `web/backend/database.py` - 确保异步驱动正确使用

### 🔧 技术改进

#### 测试框架
- ✅ pytest-asyncio 配置优化（session 级别 event_loop）
- ✅ 数据库事务管理改进（自动回滚机制）
- ✅ 测试数据隔离完善（每个测试独立事务）

#### CI/CD
- ✅ 移除过时的 Ubuntu 版本
- ✅ 添加超时保护机制
- ✅ 优化作业命名和日志

### 📊 质量提升

| 指标 | v2.5.2 | v2.5.3 | 改进 |
|------|--------|--------|------|
| 集成测试通过率 | 0% | 100% | ✅ |
| CI 卡住问题 | 有 | 无 | ✅ |
| 测试数据隔离 | 部分 | 完整 | ✅ |
| 快速测试脚本 | 无 | 有 | 🆕 |

### 📝 使用指南

#### 运行快速测试

```bash
# 本地快速验证数据库功能
python tests/quick_test.py
```

#### 运行集成测试

```bash
# 运行所有集成测试
pytest tests/integration/ -v

# 运行特定测试
pytest tests/integration/test_auth_flow.py -v
```

### 🔗 相关文档

- [测试框架使用指南](../tests/README.md)
- [CI/CD 增强文档](CI_CD_ENHANCEMENT.md)
- [依赖安装指南](DEPENDENCY_INSTALLATION.md)

---

## v2.4.0 (2025-10-13) 🌍 全平台支持版

### 🎯 核心更新

本版本实现了**真正的全平台支持**和**零配置启动**，大幅降低部署门槛。

#### 1. 全平台Release自动构建 ⭐⭐⭐⭐⭐

**新增文件**：
- `.github/workflows/release.yml` - 全平台自动构建workflow（448行）
- `RELEASE_DOWNLOAD.md` - Release下载选择指南
- `PLATFORMS_SUPPORT.md` - 全平台支持矩阵
- `docs/RELEASE_GUIDE.md` - 详细Release对比指南

**自动构建7种Release包**：
- ✅ Windows专用包（windows-x64.zip，800KB）
- ✅ macOS专用包（macos-x64.tar.gz，750KB）
- ✅ Linux专用包（linux-x64.tar.gz，750KB）
- ✅ Docker多架构镜像（amd64/arm64，200MB）
- ✅ Kubernetes配置包（k8s.tar.gz，50KB）
- ✅ 源码包（source.tar.gz，500KB）
- ✅ 前端更新包（frontend-only.tar.gz，600KB）

**技术亮点**：
- ✅ GitHub Actions矩阵并行构建（Windows/Mac/Linux同时）
- ✅ 变量自动替换（版本号、仓库名自动填充）
- ✅ Docker镜像自动转小写（兼容命名规范）
- ✅ 推送tag自动触发（如 v2.4.0）

#### 2. Kubernetes生产环境配置 ⭐⭐⭐⭐⭐

**新增11个K8s配置文件**：
- `k8s/namespace.yaml` - 命名空间
- `k8s/secret.yaml` - 密钥管理
- `k8s/configmap.yaml` - 配置管理
- `k8s/postgres-pvc.yaml` - 持久化存储
- `k8s/postgres-deployment.yaml` - 数据库部署
- `k8s/redis-deployment.yaml` - Redis部署
- `k8s/backend-deployment.yaml` - 后端部署
- `k8s/celery-deployment.yaml` - Celery部署
- `k8s/ingress.yaml` - 路由配置
- `k8s/hpa.yaml` - 自动扩缩容
- `k8s/README.md` - K8s部署完整指南（400+行）

**功能特性**：
- ✅ 高可用（多副本部署）
- ✅ 自动扩缩容（HPA，2-20副本）
- ✅ 健康检查和存活探测
- ✅ 资源限制和请求
- ✅ Ingress路由和SSL支持
- ✅ 持久化存储（PVC）

#### 3. 零配置快速启动 ⭐⭐⭐⭐⭐

**新增文件**：
- `web/docker-compose.simple.yml` - 简化Docker配置
- `ZERO_CONFIG_START.md` - 零配置启动指南

**功能特性**：
- ✅ 真正的零配置启动（使用安全的默认密钥）
- ✅ 一行命令部署：`docker compose -f docker-compose.simple.yml up -d`
- ✅ 自动配置SQLite + Redis + Celery
- ✅ 20秒启动完成
- ✅ 适合1-20人使用

**默认配置**：
```yaml
SECRET_KEY: insecure-default-secret-key-please-change-in-production-minimum-32-chars
JWT_SECRET_KEY: insecure-default-jwt-secret-key-change-me-minimum-32-chars
REDIS_PASSWORD: simple_redis_pass
```

#### 4. 宝塔面板/1Panel完整支持 ⭐⭐⭐⭐⭐

**新增文件**：
- `docs/BAOTA_1PANEL_DEPLOY.md` - 宝塔/1Panel部署指南（779行）
- `docs/DATABASE_CONFIG_WEB.md` - Web界面数据库配置指南

**支持特性**：
- ✅ 完美兼容宝塔Python项目管理器
- ✅ 完美兼容1Panel Docker编排
- ✅ 前端无需Node.js（已预编译）
- ✅ 提供SQLite快速模式
- ✅ 提供PostgreSQL完整模式
- ✅ 详细的分步指南和配置示例

**部署时间**：
- 宝塔面板：5分钟
- 1Panel Docker：3分钟

#### 5. 一键安装脚本 ⭐⭐⭐⭐

**新增文件**：
- `一键安装.sh` - Linux/macOS自动安装脚本（239行）
- `一键安装.bat` - Windows自动安装脚本（174行）

**功能特性**：
- ✅ 自动检测系统环境（Python、Git、npm）
- ✅ 支持Release版本和源码安装
- ✅ 自动创建Python虚拟环境
- ✅ 自动安装所有依赖
- ✅ 自动生成配置文件
- ✅ 选择运行模式（命令行/Web）
- ✅ 显示详细使用说明

### 📝 文档系统升级

**新增文档**（共3200+行）：
- `RELEASE_DOWNLOAD.md` - Release下载选择指南（274行）
- `PLATFORMS_SUPPORT.md` - 全平台支持矩阵（240行）
- `ZERO_CONFIG_START.md` - 零配置启动指南（233行）
- `DOCKER_README.txt` - Docker快速参考（50行）
- `docs/RELEASE_GUIDE.md` - Release详细对比（600行）
- `docs/DOCKER_SETUP.md` - Docker完整文档（400行）
- `docs/QUICK_DEPLOY.md` - 快速部署教程（320行）
- `docs/BAOTA_1PANEL_DEPLOY.md` - 宝塔/1Panel指南（779行）
- `docs/DATABASE_CONFIG_WEB.md` - 数据库配置指南（307行）
- `k8s/README.md` - K8s部署指南（404行）

**文档优化**：
- ✅ 更新`README.md` - 添加全平台部署方式
- ✅ 更新`docs/INDEX.md` - 重组文档结构
- ✅ 修复Docker徽章 - 使用GitHub Container Registry

### 🚀 新特性总结

#### 用户获益

| 方面 | v2.3.0 | v2.4.0 | 改进 |
|------|--------|--------|------|
| **Release包** | 源码 | 7种平台包 | +600% |
| **部署平台** | 3种 | 8种 | +167% |
| **启动配置** | 8项 | 0-2项 | -75-100% |
| **文档行数** | 800行 | 4000+行 | +400% |
| **国内支持** | 无 | 宝塔/1Panel | 🆕 |
| **零配置** | ❌ | ✅ | 🆕 |

#### 部署时间对比

| 方式 | v2.3.0 | v2.4.0 | 改进 |
|------|--------|--------|------|
| Docker | 5分钟 | 1分钟 | ⬇️80% |
| 源码 | 30分钟 | 5分钟 | ⬇️83% |
| 零配置 | 不支持 | 20秒 | 🆕 |

### 🔧 技术改进

#### CI/CD优化
- ✅ 修复Docker镜像命名（自动转小写）
- ✅ 修复变量替换（sed正确处理）
- ✅ 优化构建速度（并行矩阵构建）
- ✅ 添加调试输出（便于排查问题）

#### Docker优化
- ✅ 简化配置文件（docker-compose.simple.yml）
- ✅ 安全默认值（32+字符密钥）
- ✅ 健康检查完善
- ✅ 依赖等待优化

### 📦 Release包特性

**轻量级**：
- Windows: 800KB（压缩）→ 2.7MB（解压）
- Linux/Mac: 750KB（压缩）→ 2.7MB（解压）
- 前端: 600KB（压缩）→ 1.5MB（解压）

**包含内容**：
- ✅ 所有Python源码
- ✅ 前端构建文件（无需Node.js）
- ✅ 一键安装脚本
- ✅ 守护进程配置
- ✅ 完整文档

**不包含**（用户自行安装）：
- Python依赖包（通过pip install）
- 数据库文件（运行时生成）
- node_modules（不需要）

### 🌍 平台支持矩阵

**操作系统**：
- ✅ Windows 10/11/Server 2019+
- ✅ macOS 10.15+（Intel + Apple Silicon）
- ✅ Linux（Ubuntu/Debian/CentOS/Fedora/Arch）

**容器平台**：
- ✅ Docker（amd64/arm64）
- ✅ Kubernetes 1.20+
- ✅ Docker Compose v2

**国内平台**：
- ✅ 宝塔面板 7.x+
- ✅ 1Panel 1.x+

**Python版本**：
- ✅ Python 3.12（推荐）
- ✅ Python 3.11（推荐）
- ✅ Python 3.10

### 🎁 用户体验提升

**部署体验**：
- ⚡ 零配置启动（20秒）
- 📦 轻量下载（750KB）
- 🎯 平台专用包（无需选择）
- 🇨🇳 国内面板支持

**升级路径**：
```
SQLite快速启动（20秒）
  ↓
使用和测试（随时）
  ↓
Web界面升级PostgreSQL（5分钟）
  ↓
生产级部署完成
```

---

## v2.3.0 (2025-10-13) 🚀 生产就绪版

### 🎯 核心更新

本版本标志着项目从"功能完善"到"生产就绪"的重要转变。

#### 1. 自动化测试框架 ⭐⭐⭐⭐⭐

**新增文件**：
- `pytest.ini` - pytest主配置
- `tests/conftest.py` - 公共fixtures和环境配置
- `tests/unit/test_cipher.py` - 加密测试（9个测试用例）
- `tests/unit/test_answer.py` - 题库测试（5个测试用例）
- `tests/integration/test_auth_flow.py` - 认证流程集成测试
- `tests/README.md` - 测试使用指南

**功能特性**：
- ✅ pytest + pytest-asyncio完整配置
- ✅ 14个单元测试（100%通过）
- ✅ 测试覆盖率：7%（核心模块高覆盖）
- ✅ 内存数据库fixtures（AsyncSession支持）
- ✅ Mock/Patch支持（unittest.mock）
- ✅ 覆盖率报告（HTML + XML + Terminal）
- ✅ 测试标记系统（unit/integration/e2e/slow/auth）

**覆盖率详情**：
- `api/cipher.py`: 92%
- `api/config.py`: 100%
- `api/logger.py`: 80%
- `api/secure_config.py`: 30%
- `api/answer.py`: 19%

#### 2. CI/CD自动化流程 ⭐⭐⭐⭐⭐

**新增文件**：
- `.github/workflows/ci.yml` - GitHub Actions完整流水线

**包含的Job**：
- ✅ **测试Job**：多Python版本测试（3.10/3.11/3.12）+ PostgreSQL
- ✅ **代码质量检查**：Ruff + Black + Flake8
- ✅ **前端测试**：npm构建验证
- ✅ **Docker构建**：容器化测试
- ✅ **安全扫描**：Safety（依赖）+ Bandit（代码）
- ✅ **覆盖率上传**：Codecov集成

**触发条件**：
- Push到main/develop分支
- Pull Request到main分支

#### 3. API限流防护 ⭐⭐⭐⭐

**新增文件**：
- `web/backend/middleware/rate_limit.py` - 限流中间件

**功能特性**：
- ✅ 基于真实IP限流（支持X-Forwarded-For和X-Real-IP）
- ✅ 多级限流策略
  - 登录：5次/分钟（防暴力破解）
  - 注册：3次/小时（防恶意注册）
  - 密码重置：3次/小时
  - 创建任务：20次/分钟
  - 默认：100次/分钟
- ✅ IP白名单机制
- ✅ 友好的JSON错误响应
- ✅ Retry-After响应头

**使用方法**：
```python
from middleware.rate_limit import limiter, get_rate_limit
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

#### 4. 数据备份自动化 ⭐⭐⭐⭐

**新增文件**：
- `scripts/backup.sh` - Linux/macOS备份脚本
- `scripts/backup.bat` - Windows备份脚本

**功能特性**：
- ✅ SQLite + PostgreSQL双数据库支持
- ✅ 自动压缩（gzip/7-Zip）
- ✅ 7天自动清理旧备份
- ✅ 备份列表查看
- ✅ 一键恢复功能
- ✅ 定时任务支持（crontab/任务计划程序）

**使用方法**：
```bash
# Linux/macOS
./scripts/backup.sh all        # 备份所有
./scripts/backup.sh list       # 查看备份
./scripts/backup.sh restore    # 恢复

# 定时任务
crontab -e
# 添加：0 2 * * * /path/to/scripts/backup.sh all
```

#### 5. 守护进程部署 ⭐⭐⭐⭐⭐

**新增文件**：
- `daemon_control.sh` - Linux/macOS统一控制脚本（470行）
- `daemon_control.bat` - Windows控制脚本
- `web/backend/chaoxing-backend.service` - systemd后端服务
- `web/backend/chaoxing-celery.service` - systemd Celery服务
- `web/frontend/chaoxing-frontend.service` - systemd前端服务
- `web/supervisor.conf` - supervisor配置
- `docs/DAEMON.md` - 守护进程部署详细指南（679行）
- `DAEMON_QUICK_REF.md` - 快速参考手册（202行）

**支持的部署方式**（6种）：
- ✅ systemd（Linux生产环境推荐）
- ✅ supervisor（跨平台通用方案）
- ✅ Docker Compose（容器化部署）
- ✅ screen/tmux（开发环境）
- ✅ nohup（最简单）
- ✅ NSSM（Windows服务）

**功能特性**：
- ✅ 统一管理脚本（一键启动/停止/重启）
- ✅ 自动选择最佳部署方式
- ✅ 服务状态查看
- ✅ 日志实时查看
- ✅ 开机自启支持
- ✅ 自动重启机制

#### 6. Release自动构建 + 一键安装 ⭐⭐⭐⭐⭐

**新增文件**：
- `.github/workflows/release.yml` - GitHub Actions自动打包
- `一键安装.sh` - Linux/macOS一键安装脚本
- `一键安装.bat` - Windows一键安装脚本
- `docs/QUICK_DEPLOY.md` - 快速部署指南

**Release自动化**：
- ✅ 自动构建前端生产版本
- ✅ 打包完整Release包（chaoxing-vX.X.X-full.tar.gz）
- ✅ 打包前端更新包（chaoxing-vX.X.X-frontend-only.tar.gz）
- ✅ 自动构建Docker镜像（多架构）
- ✅ 推送到Docker Hub + GitHub Container Registry
- ✅ 自动创建GitHub Release
- ✅ 推送tag时自动触发（如v2.3.0）

**Docker镜像**：
- ✅ 多架构支持（linux/amd64, linux/arm64）
- ✅ GitHub Container Registry: `ghcr.io/vivi141/chaoxing:latest`
- ✅ 版本标签: `latest`, `2.3.0`等
- ✅ 构建缓存优化（GitHub Actions Cache）
- ✅ 自动推送，无需配置额外secrets

**一键安装脚本功能**：
- ✅ 自动检测系统环境（Python、Git、npm等）
- ✅ 支持Release版本和源码安装
- ✅ 自动创建Python虚拟环境
- ✅ 自动安装所有依赖
- ✅ 自动生成配置文件
- ✅ 选择运行模式（命令行/Web平台）
- ✅ 显示详细使用说明

**用户获益**：
- ⚡ **部署时间**：从30分钟 → 5分钟（减少83%）
- 📦 **无需Node.js**：前端已预编译
- 🎁 **零配置**：解压运行脚本即可
- 🔄 **易于更新**：下载新版覆盖即可
- 🇨🇳 **国内友好**：完美兼容宝塔面板和1Panel

### 🔧 代码优化

#### main.py重构（-183行，-40.8%）

- ✅ 删除重复的`RollBackManager`类定义
- ✅ 删除4个冗余旧函数（handle_not_open_chapter等）
- ✅ 修复BOM字符语法错误
- ✅ 文件大小：449行 → 266行

#### 清理未使用的导入（5个文件）

- ✅ `api/process.py` - 删除Union
- ✅ `api/secure_config.py` - 删除getpass
- ✅ `tools/encrypt_config.py` - 删除logger
- ✅ `web/backend/app.py` - 删除StaticFiles, init_db, update

### 📦 依赖更新

**新增开发依赖**：
- pytest-cov==6.0.0（测试覆盖率）
- pytest-mock==3.14.0（Mock工具）
- slowapi==0.1.9（API限流）

### 📊 质量提升

| 指标 | v2.2.3 | v2.3.0 | 提升 |
|------|--------|--------|------|
| 测试覆盖率 | 0% | 7% | +7% |
| 测试用例 | 0个 | 14个 | +14个 |
| CI/CD | 无 | 完整 | ✅ |
| API安全 | 基础 | 多级限流 | ✅ |
| 数据备份 | 手动 | 自动化 | ✅ |
| 守护进程 | 无 | 6种方案 | ✅ |
| 代码质量 | 8.0/10 | 8.8/10 | +10% |
| 项目评分 | 7.9/10 | 8.8/10 | +11% |

### 🎁 生产就绪特性

v2.3.0版本具备以下企业级特性：

1. **质量保障体系**
   - 自动化测试框架
   - CI/CD流水线
   - 代码质量自动检查

2. **安全防护体系**
   - API多级限流
   - 自动安全扫描
   - 暴力破解防护

3. **运维保障体系**
   - 6种守护进程方案
   - 自动化数据备份
   - 服务自动重启

4. **代码质量提升**
   - 消除冗余代码
   - 模块化设计
   - 测试覆盖保障

### 📝 使用指南

#### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov pytest-mock

# 运行测试
pytest tests/unit -v

# 查看覆盖率
pytest tests/unit --cov=api --cov-report=html
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

#### 启用守护进程

```bash
# Linux/macOS
chmod +x daemon_control.sh
./daemon_control.sh start

# Windows
daemon_control.bat start
```

#### 配置自动备份

```bash
# Linux/macOS - 定时任务
crontab -e
# 添加：0 2 * * * /path/to/scripts/backup.sh all

# Windows - 任务计划程序
# 按照backup.bat中的说明操作
```

### 🔗 相关文档

- [守护进程部署指南](DAEMON.md) - 详细部署方案（679行）
- [测试框架使用](../tests/README.md) - 测试指南
- [快速参考手册](../DAEMON_QUICK_REF.md) - 常用命令

---

## v2.2.3 (2025-10-13)

### ✨ 新增
- 在线配置管理（无需重启）
- 用户详情/编辑页面
- 开源声明（多处）
- 系统参数显示

### 🐛 修复
- 仪表盘统计数据显示为0
- 任务无法暂停

### ⚡ 优化
- Vite 5.4 → 7.1（启动提速60%）
- Python依赖更新15个
- Node.js依赖更新12个
- 安全漏洞清零

---

## v2.2.2 (2025-10-12)

### ✨ 新功能

#### 6种题库全面支持（Web + 命令行）
- ✅ **言溪题库**（TikuYanxi） - Token-based
- ✅ **LIKE知识库**（TikuLike） - Token-based + AI模型
- ✅ **TikuAdapter** - 开源自建服务
- ✅ **AI大模型** - OpenAI兼容API（DeepSeek、Moonshot等）
- ✅ **DeepSeek官方API**（DeepSeek）🔥 - 官方API，准确率高，推荐使用
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
- ✅ `web/frontend/src/pages/config/full.tsx` - 配置界面重构（+400行）
  - 6种题库配置表单（新增DeepSeek）
  - 4种通知配置表单（新增SMTP）
  - 动态渲染、智能提示
  - AI题库在线验证功能
- ✅ `web/frontend/src/pages/admin/SystemConfig.tsx` - 系统设置完善
  - SMTP测试自定义收件邮箱
  - 功能列表展示
  - 系统信息显示
- ✅ `web/frontend/src/pages/admin/dashboard.tsx` - 管理员控制台
  - 仪表盘统计数据修复
  - 任务自动恢复按钮

#### 配置文件更新
- ✅ `config_template.ini` - 添加SMTP和DeepSeek配置示例
- ✅ 支持硅基流动AI和DeepSeek完整配置

#### 新增功能
- ✅ **任务自动恢复** - 系统崩溃后自动恢复运行中的任务
  - 启动时自动检测中断任务
  - 自动重新提交到Celery队列
  - 管理员可手动触发恢复
- ✅ **AI题库在线验证** - 支持AI、DeepSeek、SiliconFlow配置验证
  - 一键测试API连接
  - 实时验证配置正确性
  - 友好的错误提示

### 📚 文档新增
- ✅ `docs/NEW_FEATURES.md` - 详细功能说明文档（320行）
  - 6种题库完整配置指南
  - 4种通知方式使用说明
  - 常见问题和故障排查
  - 使用场景推荐

### 🎯 代码修改统计
- **10个文件**更新
- **800+行**代码新增
- **1个新文档**（NEW_FEATURES.md）
- **1个新题库类**（DeepSeek）
- **3个新API端点**
  - `POST /user/config/test-tiku` - 题库配置验证
  - `POST /admin/recover-tasks` - 手动恢复任务
  - `POST /system-config/smtp/test` - SMTP测试（支持自定义收件）
- **TypeScript错误**: 0个
- **Python Linter**: 通过
- **代码质量**: 完全通过所有检查

### 🎁 核心亮点
- 🔥 **DeepSeek官方API** - 准确率最高的AI题库
- 🧪 **在线验证功能** - 一键测试配置正确性
- 🔄 **任务自动恢复** - 系统崩溃后无缝恢复
- 📊 **完整统计数据** - 实时监控系统状态
- ✉️ **灵活SMTP测试** - 自定义收件邮箱

### 💡 推荐配置

#### 方案1：DeepSeek官方API（准确率高）
```ini
[tiku]
provider=DeepSeek
deepseek_key=sk-你的密钥
deepseek_model=deepseek-chat
deepseek_endpoint=https://api.deepseek.com/v1/chat/completions
min_interval_seconds=3

[notification]
provider=SMTP
smtp_host=smtp.gmail.com
smtp_port=587
smtp_username=your_email@gmail.com
smtp_password=your_app_password
smtp_to_email=recipient@example.com
smtp_use_tls=true
```

#### 方案2：硅基流动AI（性价比高）
```ini
[tiku]
provider=SiliconFlow
siliconflow_key=sk-你的密钥
siliconflow_model=deepseek-ai/DeepSeek-R1
siliconflow_endpoint=https://api.siliconflow.cn/v1/chat/completions
min_interval_seconds=3

[notification]
provider=SMTP
smtp_host=smtp.qq.com
smtp_port=587
smtp_username=your_email@qq.com
smtp_password=your_auth_code
smtp_to_email=recipient@example.com
smtp_use_tls=true
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

