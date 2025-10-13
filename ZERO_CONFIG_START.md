# 零配置快速启动指南

**版本**: v2.3.0  
**目标**: 真正的一行命令启动

---

## 🚀 三种零配置启动方式

### 方式1：Docker Compose Simple（最简单）⭐⭐⭐⭐⭐

```bash
# 一行命令下载并启动
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.simple.yml && \
docker compose -f docker-compose.simple.yml up -d
```

**自动配置**：
- ✅ 使用默认密钥（测试用）
- ✅ SQLite数据库
- ✅ Redis队列
- ✅ Celery支持
- ⚠️ 生产环境需修改密钥

**访问**：`http://localhost:8000`

---

### 方式2：单容器模式（极简）

```bash
# 只运行后端，使用SQLite
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite:///./data/chaoxing.db \
  ghcr.io/vivi141/chaoxing:latest
```

**特点**：
- ✅ 单个容器
- ✅ SQLite数据库
- ❌ 无Celery（无Redis）
- ✅ 10秒启动

---

### 方式3：一键安装脚本

```bash
# 自动检测环境并安装
curl -fsSL https://raw.githubusercontent.com/ViVi141/chaoxing/main/一键安装.sh | bash
```

**自动执行**：
- ✅ 检测Python
- ✅ 创建虚拟环境
- ✅ 安装依赖
- ✅ 生成配置
- ✅ 启动服务

---

## ⚠️ 关于默认密钥的说明

### 测试环境（可以用默认值）
```bash
# docker-compose.simple.yml使用的默认值
SECRET_KEY: insecure-default-secret-key-please-change-in-production
JWT_SECRET_KEY: insecure-default-jwt-secret-key-change-me

适用：
✅ 本地测试
✅ 开发环境
✅ 功能体验
```

### 生产环境（必须修改）
```bash
# 创建.env文件
cat > .env << 'EOF'
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
EOF

# 然后启动
docker compose -f docker-compose.simple.yml up -d
```

---

## 🔄 Web界面配置数据库（规划中）

### 未来功能（v2.4.0计划）

```
访问：http://localhost:8000/admin/settings

1. 数据库配置
   ├─ 当前：SQLite ✅
   ├─ 添加PostgreSQL配置
   ├─ 点击"测试连接"
   ├─ 点击"迁移数据"
   └─ 自动切换

2. Redis配置
   ├─ 当前：未配置
   ├─ 添加Redis连接
   ├─ 点击"测试连接"
   └─ 自动启用Celery

3. 应用重启
   └─ 自动应用新配置
```

**当前状态**：🚧 开发中

---

## 📝 当前的配置方式（v2.3.0）

### 简单版 → 完整版升级

```bash
# 1. 停止简单版
docker compose -f docker-compose.simple.yml down

# 2. 备份数据
docker cp chaoxing_backend:/app/data/chaoxing.db ./backup.db

# 3. 切换到完整版
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 4. 添加数据库配置到.env
cat >> .env << 'EOF'
POSTGRES_PASSWORD=your_password
EOF

# 5. 启动完整版
docker compose up -d

# 6. 导入数据（可选）
# 如果需要迁移旧数据
docker compose exec backend python tools/migrate_sqlite_to_postgres.py
```

---

## 🎯 总结

### 当前版本（v2.3.0）

| 功能 | 状态 |
|------|------|
| **零配置Docker启动** | ✅ 支持（使用默认密钥） |
| **SQLite模式** | ✅ 支持 |
| **Redis + Celery** | ✅ 支持 |
| **手动升级到PostgreSQL** | ✅ 支持 |
| **Web界面配置数据库** | ❌ 未实现（v2.4.0计划） |

### 回答你的问题

**Q**: 可以使用Docker镜像无需修改任何配置就能启动吗？

**A**: ✅ **可以！**
```bash
docker compose -f docker-compose.simple.yml up -d
```
- 使用默认密钥（测试用）
- 自动使用SQLite + Redis
- 支持所有核心功能（包括Celery）

---

**Q**: 能在Web界面启用Redis和PostgreSQL吗？

**A**: ❌ **当前不能，需要手动配置**
- 当前版本：需要修改.env和docker-compose.yml
- 未来版本（v2.4.0）：计划实现Web界面配置

---

**Q**: 启动所有功能？

**A**: ✅ **简化版已包含所有功能！**
- ✅ Web界面
- ✅ 用户认证
- ✅ 课程管理
- ✅ 自动学习
- ✅ Celery后台任务
- ⚠️ 只是性能可能不如PostgreSQL（20人以下没问题）

---

## 💡 实际建议

### 测试/体验
```bash
# 直接启动，使用默认配置
wget docker-compose.simple.yml
docker compose -f docker-compose.simple.yml up -d
# 全功能可用！
```

### 生产环境
```bash
# 生成安全密钥
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
EOF

docker compose -f docker-compose.simple.yml up -d
```

### 需要更高性能时
```bash
# 手动升级到PostgreSQL
# 按照文档操作，5分钟完成
```

---

**当前可以做到：零配置启动（测试用），功能完整！** ✅  
**Web界面配置数据库：需要开发，未来版本实现** 🚧
