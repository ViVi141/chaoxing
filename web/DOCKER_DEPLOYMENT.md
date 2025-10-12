# Docker部署指南 - Web界面配置

## 🎯 概述

现在Docker部署支持**Web界面配置**，无需手动编辑`.env`文件！

系统启动后，首次访问会自动引导进入安装向导，通过Web界面完成所有配置。

## 🚀 快速部署步骤

### 1. 准备工作

```bash
cd web
```

### 2. 选择部署模式

#### 简单模式（推荐 - 零依赖）

```bash
docker-compose -f docker-compose.simple.yml up -d
```

**特点**：
- ✅ 无需PostgreSQL
- ✅ 无需Redis
- ✅ 使用SQLite数据库
- ✅ 使用文件系统队列
- ✅ 适合小规模使用（1-10用户）

#### 标准模式（生产环境）

```bash
docker-compose up -d
```

**特点**：
- 🔹 使用PostgreSQL数据库
- 🔹 使用Redis缓存和队列
- 🔹 更高性能
- 🔹 适合中大规模使用（10+用户）

### 3. 访问安装向导

服务启动后，访问：http://localhost:3000

系统会自动检测是否已配置，未配置时自动跳转到安装向导。

### 4. 完成Web配置

按照安装向导的步骤完成配置：

#### 步骤1：欢迎页
了解平台特性和使用须知。

#### 步骤2：管理员配置
- **选项A**：使用默认管理员（admin / Admin@123）
- **选项B**：创建新管理员账号

#### 步骤3：系统配置
- **部署模式**：选择简单模式或标准模式
- **平台名称**：自定义平台名称
- **任务配置**：设置最大并发任务数和超时时间
- **数据库配置**（仅标准模式）：输入PostgreSQL和Redis连接信息

#### 步骤4：完成
配置完成，自动跳转到登录页面。

## 📝 配置文件

### 自动生成的配置文件

完成Web配置后，系统会自动生成：

```
web/backend/web_config.json
```

此文件包含所有系统配置，Docker重启后会自动加载。

### 配置文件示例（简单模式）

```json
{
  "deploy_mode": "simple",
  "platform_name": "超星学习通管理平台",
  "max_tasks_per_user": 3,
  "task_timeout": 120,
  "enable_register": true,
  "log_retention_days": 30,
  "enable_email_notification": false,
  "secret_key": "自动生成的密钥",
  "jwt_secret_key": "自动生成的JWT密钥"
}
```

### 配置文件示例（标准模式）

```json
{
  "deploy_mode": "standard",
  "platform_name": "超星学习通管理平台",
  "max_tasks_per_user": 5,
  "task_timeout": 180,
  "enable_register": true,
  "database_url": "postgresql+asyncpg://user:pass@postgres:5432/chaoxing",
  "redis_url": "redis://redis:6379/0",
  "log_retention_days": 30,
  "enable_email_notification": false,
  "secret_key": "自动生成的密钥",
  "jwt_secret_key": "自动生成的JWT密钥"
}
```

## 🔄 修改配置

### 方法一：重新运行安装向导

1. 删除配置文件：
```bash
docker-compose exec backend rm -f web_config.json
```

2. 重启服务：
```bash
docker-compose restart backend
```

3. 重新访问http://localhost:3000，进入安装向导

### 方法二：直接修改配置文件

1. 编辑配置文件：
```bash
docker-compose exec backend vi web_config.json
```

2. 重启服务：
```bash
docker-compose restart backend
```

## 🛠️ 常见问题

### Q: 部署后无法访问？
**A**: 检查防火墙设置，确保端口3000开放：
```bash
# Linux
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload

# 查看服务状态
docker-compose ps
```

### Q: 忘记管理员密码？
**A**: 可以通过命令行重置：
```bash
docker-compose exec backend python -c "
from auth import get_password_hash
print('新密码哈希:', get_password_hash('NewPassword123'))
"
# 然后手动更新数据库
```

或重新运行安装向导（删除配置文件和数据库）。

### Q: 如何切换部署模式？
**A**: 
1. 停止当前服务
2. 删除配置文件和数据库
3. 使用新的compose文件启动
4. 重新配置

```bash
docker-compose down -v
rm web_config.json chaoxing_web.db
docker-compose -f docker-compose.simple.yml up -d
```

### Q: 配置文件在哪里？
**A**: 配置文件位于容器内的`/app/web_config.json`，也可以挂载到主机：

修改`docker-compose.yml`添加卷挂载：
```yaml
volumes:
  - ./web_config.json:/app/web_config.json
```

### Q: 如何备份配置？
**A**: 
```bash
# 备份配置文件
docker-compose exec backend cat web_config.json > web_config.backup.json

# 备份数据库（简单模式）
docker-compose exec backend cp chaoxing_web.db chaoxing_web.db.backup

# 备份数据库（标准模式）
docker-compose exec postgres pg_dump -U user chaoxing > backup.sql
```

## 📊 监控和日志

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f frontend
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 进入数据库容器（标准模式）
docker-compose exec postgres psql -U user chaoxing
```

## 🎉 总结

使用Web界面配置的优势：
- ✅ 无需手动编辑.env文件
- ✅ 界面友好，不易出错
- ✅ 自动生成安全密钥
- ✅ 配置持久化保存
- ✅ 支持动态切换模式
- ✅ 适合非技术用户

---

**原项目**: [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)  
**增强版**: [ViVi141/chaoxing](https://github.com/ViVi141/chaoxing)  
**开发者**: ViVi141 (747384120@qq.com)  
**协议**: GPL-3.0 License

