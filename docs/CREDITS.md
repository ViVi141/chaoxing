# :trophy: 贡献与致谢

## :star: 原项目

本增强版基于以下优秀的开源项目：

### Samueli924/chaoxing
- **项目地址**: https://github.com/Samueli924/chaoxing
- **开源协议**: GPL-3.0 License
- **Star数量**: 2.4k+ (截至2025-10-12)
- **Fork数量**: 343+
- **贡献者**: 39+

:muscle: 原项目的最终目的是通过开源消灭所谓的付费刷课平台，希望有能力的朋友都可以为这个项目提交代码，支持本项目的良性发展

### 原项目核心贡献者

感谢原项目的所有贡献者：

![Alt](https://repobeats.axiom.co/api/embed/d3931e84b4b2f17cbe60cafedb38114bdf9931cb.svg "Repobeats analytics image")

<a href="https://github.com/Samueli924/chaoxing/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Samueli924/chaoxing" />
</a>

特别感谢：
- **[Samueli924](https://github.com/Samueli924)** - 原项目作者和维护者
- **[sz134055](https://github.com/sz134055)** - 添加题库答题支持 ([PR #360](https://github.com/Samueli924/chaoxing/pull/360))
- 以及所有提交Issue和PR的贡献者

## :rocket: 增强版开发

### 开发者信息
- **GitHub**: ViVi141
- **项目地址**: https://github.com/ViVi141/chaoxing
- **邮箱**: 747384120@qq.com
- **更新日期**: 2025-10-12

### 增强内容

#### 1. Web多用户管理平台 :new:
- FastAPI + Vue 3 架构
- 用户注册/登录/权限管理
- 任务创建/启动/暂停/取消
- WebSocket实时进度推送
- 管理员后台监控
- Celery异步任务队列
- 25个RESTful API接口
- 完整的Swagger API文档
- Docker一键部署

#### 2. 安全性增强 :lock:
- 配置文件密码加密存储（Fernet算法）
- 日志敏感信息自动脱敏
  - 手机号: `138****8000`
  - 密码: `****`
  - Token: `abcdef****xyz9`
- JWT令牌认证
- bcrypt密码加密
- SQL注入防护

#### 3. 配置管理优化 :gear:
- 配置参数自动验证
- 启动时检查配置完整性
- 详细的错误提示
- 配置加密工具

#### 4. 日志系统优化 :page_facing_up:
- 日志自动轮转（每天0点）
- 保留30天历史日志
- 自动压缩为ZIP格式
- 分级日志存储
- 敏感信息自动脱敏

#### 5. 性能优化 :zap:
- HTTP请求智能重试机制
- 指数退避算法
- 连接池优化
- 超时精确控制
- 异步IO支持

#### 6. 文档完善 :books:
- 详细的使用指南
- 生产环境部署指南
- API接口文档
- Docker部署文档
- 项目结构说明

### 技术栈

#### 命令行版增强
- Python 3.10+
- cryptography - 配置加密
- loguru - 日志系统增强
- 自定义验证器和HTTP客户端

#### Web平台
- **后端**: FastAPI 0.104+ + SQLAlchemy 2.0 + PostgreSQL + Redis + Celery
- **前端**: Vue 3.3+ + Element Plus + Pinia + ECharts（待实现）
- **部署**: Docker + Docker Compose + Nginx

### 代码统计
- 新增Python文件: 17个
- 新增代码行数: ~3500行
- 新增API接口: 25个
- 新增数据库表: 5个
- 新增文档: 8份

## :handshake: 致谢

### 开源项目
感谢以下开源项目：
- **FastAPI** - 现代高性能Web框架
- **SQLAlchemy** - Python ORM
- **Celery** - 分布式任务队列
- **Vue.js** - 渐进式前端框架
- **Element Plus** - Vue 3 UI组件库
- **Redis** - 高性能缓存
- **PostgreSQL** - 企业级数据库
- **Loguru** - 优雅的日志库
- **Cryptography** - 密码学库

### 原项目贡献者
再次感谢 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 的所有贡献者！

没有你们的优秀工作，就没有这个增强版本。

## :balance_scale: 开源协议

本项目遵循 **GPL-3.0 License** 协议：

- :white_check_mark: 允许开源/免费使用
- :white_check_mark: 允许修改和衍生
- :x: 禁止闭源商业使用
- :x: 禁止用于盈利
- :warning: 衍生代码必须同样遵守GPL-3.0协议

详见: [LICENSE](../LICENSE)

## :email: 联系方式

### 增强版
- **开发者**: ViVi141
- **邮箱**: 747384120@qq.com
- **GitHub**: https://github.com/ViVi141/chaoxing
- **Issues**: https://github.com/ViVi141/chaoxing/issues

### 原项目
- **GitHub**: https://github.com/Samueli924/chaoxing
- **Issues**: https://github.com/Samueli924/chaoxing/issues

## :pray: 鸣谢

特别感谢：
1. **[Samueli924](https://github.com/Samueli924)** - 创建并维护原项目
2. **所有原项目贡献者** - 提供稳定的核心功能
3. **开源社区** - 提供优秀的技术和工具

---

**本项目仅用于学习交流，请勿用于商业用途！**

:star: 如果觉得有帮助，请给 [原项目](https://github.com/Samueli924/chaoxing) 和 [增强版](https://github.com/ViVi141/chaoxing) 一个Star！

