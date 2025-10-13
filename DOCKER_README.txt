# Docker快速开始

## 使用预构建镜像（推荐）

```bash
# Docker Hub（全球）
docker pull vivi141/chaoxing:latest

# GitHub Container Registry（推荐）
docker pull ghcr.io/vivi141/chaoxing:latest
```

## 支持架构
- linux/amd64 (x86_64)
- linux/arm64 (ARM64/树莓派)

## 快速启动

```bash
# 1. 创建环境变量文件
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
POSTGRES_PASSWORD=your_password
REDIS_PASSWORD=your_redis_pass
EOF

# 2. 下载docker-compose.yml
wget https://raw.githubusercontent.com/ViVi141/chaoxing/main/web/docker-compose.yml

# 3. 启动
docker compose up -d

# 4. 访问
# http://localhost:8000
```

## 详细文档
查看 docs/DOCKER_SETUP.md 获取完整指南

## 版本标签
- latest - 最新稳定版
- 2.3.0 - 指定版本
- main - 开发版

## 镜像地址
- Docker Hub: vivi141/chaoxing
- GitHub: ghcr.io/vivi141/chaoxing

