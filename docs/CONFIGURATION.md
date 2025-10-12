# ⚙️ 配置指南

## 命令行版配置

### config.ini

```ini
[common]
# 超星账号
username = 13800138000
password = your_password
password_encrypted = false  # 加密后改为true

# 课程列表（可选，留空则学习所有课程）
course_list = 课程ID1,课程ID2

# 播放倍速（1.0-2.0）
speed = 1.5

# 未开放章节处理
notopen_action = retry  # retry/ask/continue

[tiku]
# 题库配置（可选）
provider = TikuYanxi
token = your_token
delay = 1.0
cover_rate = 0.8
submit = true

[notification]
# 通知配置（可选）
provider = ServerChan
url = https://...
```

### 密码加密

```bash
python tools/encrypt_config.py config.ini
```

---

## Web平台配置

### 环境变量（.env）

```bash
# 部署模式
DEPLOY_MODE=simple  # simple/standard

# 数据库
DATABASE_URL=sqlite+aiosqlite:///data/chaoxing.db

# Celery
CELERY_BROKER_URL=filesystem://localhost/
CELERY_RESULT_BACKEND=file://data/celery_results

# 安全密钥（必须修改！）
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# 生成密钥：
# python -c "import secrets; print(secrets.token_urlsafe(32))"

# 默认管理员
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Admin@123

# 任务配置
MAX_CONCURRENT_TASKS_PER_USER=3
TASK_TIMEOUT=7200

# 日志
LOG_LEVEL=INFO
```

### 生产环境配置

```bash
# 使用PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# 使用Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 强密钥
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# CORS
CORS_ORIGINS=https://your-domain.com

# 邮件（可选）
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your-app-password
```

---

## 配置项说明

### 播放倍速 (speed)
- 范围：1.0-2.0
- 推荐：1.5
- 过快可能被检测

### 未开放章节处理 (notopen_action)
- `retry` - 重试上一章节（默认）
- `ask` - 询问是否继续
- `continue` - 自动跳过

### 题库配置
- `provider` - 题库名称
- `token` - API密钥
- `cover_rate` - 覆盖率阈值
- `submit` - 是否自动提交

---

## 配置示例

查看：
- `config_template.ini` - 命令行版配置模板
- `web/env.example` - Web版配置示例

