# :computer: 超星学习通自动化完成任务点 (增强版)

<p align="center">
    <a href="https://github.com/Samueli924/chaoxing" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/stars/Samueli924/chaoxing" alt="Github Stars" />
    </a>
    <a href="https://github.com/Samueli924/chaoxing" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/forks/Samueli924/chaoxing" alt="Github Forks" />
    </a>
    <a href="https://github.com/Samueli924/chaoxing" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/languages/code-size/Samueli924/chaoxing" alt="Code-size" />
    </a>
    <a href="https://github.com/Samueli924/chaoxing" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/v/release/Samueli924/chaoxing?display_name=tag&sort=semver" alt="version" />
    </a>
</p>

:muscle: 本项目基于 **[Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)** 原项目进行增强开发

:star: 觉得有帮助的朋友可以给个Star

## :zap: 快速导航

- **:rocket: 新用户？** → [QUICK_START.md](QUICK_START.md) 快速启动指南
- **:wrench: 环境设置** → [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) 虚拟环境配置
- **:zap: 一键启动** → 使用 `start_all.bat` (Windows) 或 `start_all.sh` (Linux/Mac)
- **:computer: 命令行版？** → 本文档下方的"使用方法"部分
- **:globe_with_meridians: Web平台？** → [web/README.md](web/README.md) + [web/START_GUIDE.md](web/START_GUIDE.md)
- **:package: 部署生产？** → [web/DEPLOYMENT_GUIDE.md](web/DEPLOYMENT_GUIDE.md)
- **:books: 查看文档？** → [docs/INDEX.md](docs/INDEX.md) 文档索引
- **:white_check_mark: 项目总览** → [docs/SUMMARY.md](docs/SUMMARY.md) 查看项目详情

## :bookmark_tabs: 项目信息

- **原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) (GPL-3.0)
- **增强版本**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)
- **增强开发**: ViVi141
- **联系方式**: 747384120@qq.com
- **更新日期**: 2025-10-12

## :point_up: 增强版更新通知

**🎉 20251012 重大更新 - Web版本核心功能100%完成！**

✅ **Web版本现已完全集成命令行版本的所有核心学习功能！**

**新增功能**：
- :globe_with_meridians: **Web多用户管理平台** - FastAPI + Vue 3，完整学习逻辑
- :rocket: **核心功能集成** - 视频/文档/测验/阅读，所有任务点自动完成
- :gear: **Web界面配置** - 安装向导，无需手动编辑配置文件
- :package: **零依赖部署** - 简单模式支持SQLite + 文件队列
- :lock: **安全性增强** - 密码加密、日志脱敏
- :chart_with_upwards_trend: **性能优化** - HTTP智能重试、日志轮转
- :white_check_mark: **配置验证** - 自动验证配置参数
- :books: **完善文档** - 详细的使用和部署指南

**详见**：[docs/SUMMARY.md](docs/SUMMARY.md) 项目完整总览

**原项目更新**: 感谢[sz134055](https://github.com/sz134055)提交代码[PR #360](https://github.com/Samueli924/chaoxing/pull/360)，**添加了对题库答题的支持**

## :books: 使用方法

### 方式一：命令行版（原版功能 + 安全增强）

#### 源码运行
1. `git clone --depth=1 https://github.com/Samueli924/chaoxing` 项目至本地
2. `cd chaoxing`
3. `pip install -r requirements.txt` 或者 `pip install .`(通过 pyproject.toml 安装依赖)
4. (可选直接运行) `python main.py`
5. (可选配置文件运行) 复制config_template.ini文件为config.ini文件，修改文件内的账号密码内容, 执行 `python main.py -c config.ini`
6. (可选命令行运行)`python main.py -u 手机号 -p 密码 -l 课程ID1,课程ID2,课程ID3...(可选) -a [retry|ask|continue](可选)`

#### 配置加密（增强版新增）
```bash
# 加密配置文件中的密码（推荐）
python tools/encrypt_config.py config.ini
```

#### 打包文件运行
1. 从最新[Releases](https://github.com/Samueli924/chaoxing/releases)中下载exe文件
2. (可选直接运行) 双击运行即可
3. (可选配置文件运行) 下载config_template.ini文件保存为config.ini文件，修改文件内的账号密码内容, 执行 `./chaoxing.exe -c config.ini`
4. (可选命令行运行)`./chaoxing.exe -u "手机号" -p "密码" -l 课程ID1,课程ID2,课程ID3...(可选) -a [retry|ask|continue](可选)`

#### Docker运行
1. 构建Docker镜像
   ```bash
   docker build -t chaoxing .
   ```

2. 运行Docker容器
   ```bash
   # 直接运行（将使用默认配置模板）
   docker run -it chaoxing
   
   # 使用自定义配置文件运行
   docker run -it -v /本地路径/config.ini:/config/config.ini chaoxing
   ```

3. 配置说明
   - Docker版本默认使用挂载到 `/config/config.ini` 的配置文件
   - 首次运行时，会自动将 `config_template.ini` 复制到该位置作为模板
   - 可以将本地编辑好的配置文件挂载到容器中，按照上述示例命令操作

### 方式二：Web多用户平台（增强版新增 :new:）

#### 特性
- :globe_with_meridians: 多用户注册/登录（JWT认证）
- :bar_chart: 任务管理（创建/启动/暂停/取消/监控）
- :zap: 实时进度推送（WebSocket）
- :busts_in_silhouette: 管理员后台（用户管理、任务监控、数据统计）
- :arrows_counterclockwise: 异步任务队列（Celery + Redis）
- :whale: Docker一键部署

#### 快速启动（简单模式 - 推荐）⭐

**🚀 方式一：一键启动所有服务（最简单）**

```batch
# Windows - 双击运行或命令行执行
start_all.bat
```

```bash
# Linux/Mac
chmod +x start_all.sh
./start_all.sh
```

**特性**：
- ✅ 自动检测并设置环境
- ✅ 一次启动所有服务（后端+Celery+前端）
- ✅ 自动打开服务窗口
- ✅ 访问 http://localhost:5173

**🛠️ 方式二：分别启动（更灵活）**

```batch
# Windows - 分别在三个终端运行
setup_env.bat             # 首次运行：设置环境
web\start_backend.bat     # 终端1：启动后端
web\start_celery.bat      # 终端2：启动Celery
web\frontend\start.bat    # 终端3：启动前端
```

```bash
# Linux/Mac
chmod +x setup_env.sh && ./setup_env.sh  # 首次运行：设置环境
./web/start_backend.sh    # 终端1：启动后端
./web/start_celery.sh     # 终端2：启动Celery
cd web/frontend && npm run dev  # 终端3：启动前端
```

**🎉 首次访问自动进入安装向导！**
- 无需手动编辑配置文件
- Web界面完成所有配置
- 自动生成安全密钥

**特点**：
- ✅ 使用SQLite数据库（无需安装PostgreSQL）
- ✅ 使用文件系统队列（无需安装Redis）
- ✅ **统一虚拟环境**（一次安装，处处使用）⭐
- ✅ **Web界面配置**（无需编辑.env）⭐
- ✅ 适合小规模使用（<50用户）

#### 标准模式（生产环境）

**使用Docker Compose**（需要PostgreSQL和Redis）：

```bash
cd web
docker-compose up -d

# 访问: http://localhost:3000
# 首次访问自动进入安装向导
```

**使用Docker Compose（简单模式）**：

```bash
cd web
docker-compose -f docker-compose.simple.yml up -d

# 访问: http://localhost:3000
# 首次访问自动进入安装向导
```

**🎉 重要提示：**
- **无需手动编辑.env文件**
- **通过Web界面完成所有配置**
- 自动生成安全密钥
- 配置持久化保存

详细说明请查看：
- [web/README.md](web/README.md)
- [web/DOCKER_DEPLOYMENT.md](web/DOCKER_DEPLOYMENT.md)

### 题库配置说明

在你的配置文件中找到`[tiku]`，按照注释填写想要使用的题库名（即`provider`，大小写要一致），并填写必要信息，如token，然后在启动时添加`-c [你的配置文件路径]`即可。

题库会默认使用根目录下的`config.ini`文件中的配置，所以你可以复制配置模板（参照前面的说明）命名为`config.ini`，并只配置题库项`[tiku]`，这样即使你不填写账号之类的信息，不使用`-c`参数指定配置文件，题库也会根据这个配置文件自动配置并启用。

对于那些有章节检测且任务点需要解锁的课程，必须配置题库。

**提交模式与答题**
不配置题库（既不提供配置文件，也没有放置默认配置文件`config.ini`或填写要使用的题库）视为不使用题库，对于章节检测等需要答题的任务会自动跳过。
题库覆盖率：搜到的题目占总题目的比例
提交模式`submit`值为

- `true`：会答完题，达到题库题目覆盖率提交，没达到只保存，**正确率不做保证**。
- `false`：会答题，但是不会提交，仅保存搜到答案的，随后你可以自行前往学习通查看、修改、提交。**任何填写不正确的`submit`值会被视为`false`**

> 题库名即`answer.py`模块中根据`Tiku`类实现的具体题库类，例如`TikuYanxi`（言溪题库），在填写时，请务必保持大小写一致。

### 已关闭任务点处理配置说明

在配置文件的 `[common]` 部分，可以通过 `notopen_action` 选项配置遇到已关闭任务点时的处理方式:

- `retry` (默认): 遇到关闭的任务点时尝试重新完成上一个任务点，如果连续重试 3 次仍然失败 (或未配置题库及自动提交) 则停止
- `ask`: 遇到关闭的任务点时询问用户是否继续。选择继续后会自动跳过连续的关闭任务点，直到遇到开放的任务点
- `continue`: 自动跳过所有关闭的任务点，继续检查和完成后续任务点

也可以通过命令行参数 `-a` 或 `--notopen-action` 指定处理方式，例如：

```bash
python main.py -a ask  # 使用询问模式
```

### 外部通知配置说明

这功能会在所有课程学习任务结束后，或是程序出现错误时，使用外部通知服务推送消息告知你（~~有用但不多~~）

与题库配置类似，不填写视为不使用，按照注释填写想要使用的外部通知服务（也是`provider`，大小写要一致），并填写必要的`url`

## :file_folder: 项目结构

```
chaoxing/
├── 📂 api/                          # 核心API模块
├── 📂 web/                          # Web多用户平台
├── 📂 tools/                        # 工具脚本
├── 📂 resource/                     # 资源文件
├── 📂 logs/                         # 日志目录
├── 📂 docs/                         # 项目文档
│   ├── SUMMARY.md                  # 项目总览
│   ├── PROJECT_STRUCTURE.md        # 详细结构说明
│   ├── CHANGELOG.md                # 更新日志
│   └── CREDITS.md                  # 贡献者名单
├── 📄 main.py                       # 命令行版主程序
├── 📄 config_template.ini           # 配置模板
├── 📄 requirements.txt              # Python依赖
├── 📄 Dockerfile                    # Docker镜像
└── 📄 README.md                     # 本文档
```

详细结构: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## :books: 文档导航

### :rocket: 快速开始
| 文档 | 说明 | 链接 |
|------|------|------|
| **QUICK_START.md** | **快速启动指南** | [查看](QUICK_START.md) ⭐ |
| WEB_PLATFORM_COMPLETE.md | Web平台完成报告 | [查看](WEB_PLATFORM_COMPLETE.md) |

### :book: 项目文档
| 文档 | 说明 | 链接 |
|------|------|------|
| README.md | 项目主文档 | 本文档 |
| docs/SUMMARY.md | 项目快速总览 | [查看](docs/SUMMARY.md) |
| docs/PROJECT_STRUCTURE.md | 详细结构说明 | [查看](docs/PROJECT_STRUCTURE.md) |
| docs/CHANGELOG.md | 版本更新日志 | [查看](docs/CHANGELOG.md) |
| docs/CREDITS.md | 贡献者致谢 | [查看](docs/CREDITS.md) |

### :globe_with_meridians: Web平台
| 文档 | 说明 | 链接 |
|------|------|------|
| web/README.md | Web平台主文档 | [查看](web/README.md) |
| web/START_GUIDE.md | 后端快速启动 | [查看](web/START_GUIDE.md) |
| web/DEPLOYMENT_GUIDE.md | 生产环境部署 | [查看](web/DEPLOYMENT_GUIDE.md) |
| web/frontend/README.md | 前端项目说明 | [查看](web/frontend/README.md) |

## 🔐 安全特性

### 配置加密
```bash
# 加密配置文件中的密码
python tools/encrypt_config.py config.ini
```

### 日志脱敏
自动脱敏日志中的敏感信息：
- 手机号：`138****8000`
- 密码：`****`
- Token：`abcdef****xyz9`

### 日志轮转
- 每天0点自动轮转
- 保留30天历史日志
- 自动压缩为ZIP格式

## ⚙️ 高级配置

### 未开放章节处理

在配置文件中设置：
```ini
notopen_action = retry    # 重试上一章节（默认）
# notopen_action = ask    # 询问是否继续
# notopen_action = continue  # 自动跳过
```

### 播放倍速

```ini
speed = 1.5  # 1.0-2.0之间
```

### 并发任务限制（Web版）

在`web/backend/config.py`中：
```python
MAX_CONCURRENT_TASKS_PER_USER = 3  # 每用户最大并发任务数
```

## 📊 Web平台功能

### 用户功能
- 用户注册/登录
- 个人配置管理（超星账号、题库、通知）
- 任务创建和管理
- 实时进度查看
- 任务日志查看
- 数据统计

### 管理员功能
- 用户管理（查看/编辑/删除）
- 全局任务监控
- 强制停止任务
- 系统日志查看
- 数据统计和报表

### API接口
- 25个RESTful API接口
- 自动生成的Swagger文档
- WebSocket实时通信
- JWT令牌认证

详细文档：[web/README.md](web/README.md)

## 🔧 开发环境要求

### 命令行版
- Python 3.10+
- 依赖包见 requirements.txt

### Web平台
- Python 3.10+
- Redis 7.0+
- PostgreSQL 15+ (生产环境) 或 SQLite (开发环境)
- Node.js 18+ (前端开发)

## 🐳 Docker部署

### 命令行版
```bash
docker build -t chaoxing .
docker run -it -v $(pwd)/config.ini:/config/config.ini chaoxing
```

### Web平台
```bash
cd web
docker-compose up -d
```

## 📝 更新日志

### v3.3.0 增强版 (2025-10-12)
- 🌐 **新增**: 完整的Web多用户管理平台
  - FastAPI + Vue 3 架构
  - 25个RESTful API接口
  - 用户注册/登录/权限管理
  - 任务创建/启动/暂停/取消
  - WebSocket实时进度推送
  - 管理员后台监控
  - Celery异步任务队列
  - Docker一键部署
- 🔐 **安全性**: 配置文件密码加密存储
- 📊 **日志**: 自动脱敏和轮转
- ✅ **验证**: 配置参数自动验证
- ⚡ **性能**: HTTP请求智能重试
- 📚 **文档**: 完善的使用和部署指南
- **开发者**: ViVi141

### v3.2.0 (2025-10-12)
- ✨ 添加配置文件密码加密
- ✨ 实现日志自动脱敏
- ✨ 添加配置参数验证
- ✨ 优化HTTP请求重试机制
- ✨ 完善日志轮转和归档
- 📚 添加详细的使用文档

### v3.1.3 (原项目)
- ✨ 添加题库答题支持 (感谢 @sz134055)
- 🐛 修复多项已知问题

## :warning: 免责声明

- 本代码基于 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 原项目，遵循 [GPL-3.0 License](https://github.com/Samueli924/chaoxing/blob/main/LICENSE) 协议
- 本代码允许**开源/免费使用和引用/修改/衍生代码的开源/免费使用**，不允许**修改和衍生的代码作为闭源的商业软件发布和销售**，禁止**使用本代码盈利**
- 以此代码为基础的程序**必须**同样遵守 [GPL-3.0 License](https://github.com/Samueli924/chaoxing/blob/main/LICENSE) 协议
- 本代码仅用于**学习讨论**，禁止**用于盈利**
- 他人或组织使用本代码进行的任何**违法行为**与本人无关

## :heart: 致谢与贡献者

### 原项目
感谢 **[Samueli924](https://github.com/Samueli924)** 及所有为原项目贡献的开发者！

![Alt](https://repobeats.axiom.co/api/embed/d3931e84b4b2f17cbe60cafedb38114bdf9931cb.svg "Repobeats analytics image")

<a href="https://github.com/Samueli924/chaoxing/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Samueli924/chaoxing" />
</a>

### 增强版开发
- **ViVi141** - Web平台开发、安全增强、性能优化
- 联系方式: 747384120@qq.com

## :phone: 技术支持

### 文档
- **项目总览**: [docs/SUMMARY.md](docs/SUMMARY.md)
- **项目结构**: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- **更新日志**: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- **Web平台**: [web/README.md](web/README.md)
- **快速启动**: [web/START_GUIDE.md](web/START_GUIDE.md)
- **部署指南**: [web/DEPLOYMENT_GUIDE.md](web/DEPLOYMENT_GUIDE.md)

### 问题反馈
- **原项目Issues**: https://github.com/Samueli924/chaoxing/issues
- **增强版Issues**: https://github.com/ViVi141/chaoxing/issues
- **开发者邮箱**: 747384120@qq.com
- 提供详细的错误日志和环境信息

## :star: Star History

如果觉得有帮助，请给个Star！

### 原项目
[![Star History Chart](https://api.star-history.com/svg?repos=Samueli924/chaoxing&type=Date)](https://star-history.com/#Samueli924/chaoxing&Date)

### 增强版
[![Star History Chart](https://api.star-history.com/svg?repos=ViVi141/chaoxing&type=Date)](https://star-history.com/#ViVi141/chaoxing&Date)

## :page_facing_up: 许可证

本项目遵循 [GPL-3.0 License](LICENSE) 协议

基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 开发

---

**开发不易，请勿用于商业用途！** 🙏
