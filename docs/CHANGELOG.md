# :memo: 更新日志

> 基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 的增强版  
> 增强版本: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)

---

## [v3.3.0] 增强版 - 2025-10-12

### :sparkles: 新增功能

#### Web多用户管理平台 :new:
- :globe_with_meridians: 完整的Web管理平台
  - 多用户注册/登录系统
  - JWT令牌认证
  - 基于角色的权限控制（user/admin）
- :bar_chart: 任务管理系统
  - 创建/启动/暂停/取消任务
  - 实时进度监控
  - 任务日志查看
  - 并发任务数限制
- :busts_in_silhouette: 管理员后台
  - 用户管理（查看/编辑/删除）
  - 全局任务监控
  - 系统统计数据
  - 日志查看
- :zap: 实时通信
  - WebSocket连接管理
  - 任务进度实时推送
  - 系统通知推送
- :arrows_counterclockwise: 异步任务队列
  - Celery + Redis
  - 分布式任务处理
  - 任务状态追踪

#### 技术架构
- **后端**: FastAPI 0.104+ (高性能异步框架)
- **ORM**: SQLAlchemy 2.0 (异步ORM)
- **数据库**: PostgreSQL 15 / SQLite
- **缓存**: Redis 7.0+
- **任务队列**: Celery 5.3+
- **认证**: JWT (python-jose)
- **数据验证**: Pydantic 2.0

#### API接口
- 25个RESTful API接口
- 自动生成Swagger文档
- ReDoc文档
- 完整的请求/响应验证

### :lock: 安全性增强

#### 配置加密
- 使用Fernet对称加密算法
- PBKDF2密钥派生
- 自动密钥管理
- 配置加密工具: `tools/encrypt_config.py`

#### 日志脱敏
- 手机号自动脱敏: `138****8000`
- 密码自动脱敏: `****`
- Token自动脱敏: `abcdef****xyz9`
- Cookie自动脱敏: `****`

#### Web平台安全
- JWT令牌认证
- bcrypt密码加密
- SQL注入防护
- XSS/CSRF保护
- 敏感信息加密存储

### :chart_with_upwards_trend: 性能优化

#### HTTP客户端优化
- 智能重试机制（指数退避）
- 连接池优化（10/20连接）
- 精确超时控制（连接10s，读取30s）
- 自动处理临时性错误

#### 日志系统优化
- 日志自动轮转（每天0点）
- 保留30天历史日志
- 自动压缩为ZIP格式
- 分级日志存储（普通+错误）

### :white_check_mark: 配置管理

#### 参数验证
- 启动时自动验证配置
- 手机号格式验证
- 密码强度验证
- 播放倍速范围验证
- 题库配置完整性验证

#### 错误提示改进
- 详细的错误信息
- 配置修正建议
- 提前发现配置问题

### :books: 文档完善

新增文档：
- `README.md` - 主文档（已更新）
- `docs/SUMMARY.md` - 项目总览
- `docs/PROJECT_STRUCTURE.md` - 项目结构
- `docs/CREDITS.md` - 贡献与致谢
- `docs/CHANGELOG.md` - 本文档
- `web/README.md` - Web平台文档
- `web/START_GUIDE.md` - 快速启动指南
- `web/DEPLOYMENT_GUIDE.md` - 部署指南

### :wrench: 其他改进

- 统一依赖管理（requirements.txt + pyproject.toml）
- 完善.gitignore配置
- 添加Windows启动脚本
- 创建工具脚本目录

### :package: 文件清单

新增文件：
- `api/secure_config.py` - 配置加密模块
- `api/config_validator.py` - 配置验证器
- `api/http_client.py` - HTTP客户端优化
- `tools/encrypt_config.py` - 配置加密工具
- `web/backend/` - 完整的Web后端（17个文件）
- 8份详细文档

---

## [v3.2.0] - 2025-01-11

### 新增
- 配置文件密码加密
- 日志自动脱敏
- 配置参数验证
- HTTP请求重试优化
- 日志轮转和归档

---

## [v3.1.3] - 原项目版本

### 新增
- 添加题库答题支持 (感谢 @sz134055)

### 修复
- 修复多项已知问题

---

## :link: 参考链接

- **原项目**: https://github.com/Samueli924/chaoxing
- **增强版本**: https://github.com/ViVi141/chaoxing
- **原项目Releases**: https://github.com/Samueli924/chaoxing/releases
- **原项目Issues**: https://github.com/Samueli924/chaoxing/issues

---

## :copyright: 版权说明

本增强版基于原项目 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 开发，遵循 GPL-3.0 License 协议。

- **原项目作者**: Samueli924
- **原项目地址**: https://github.com/Samueli924/chaoxing
- **增强开发**: ViVi141 (747384120@qq.com)
- **增强版地址**: https://github.com/ViVi141/chaoxing
- **开源协议**: GPL-3.0 License

---

**最后更新**: 2025-10-12

