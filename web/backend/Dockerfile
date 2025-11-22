FROM python:3.12.8-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 安装系统依赖（完整版，确保所有Python包都能正确编译）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    postgresql-client \
    libpq-dev \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目根目录的requirements.txt（context为项目根目录）
COPY requirements.txt .

# 安装Python依赖（先升级pip和构建工具）
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 验证关键依赖是否正确安装
RUN python -c "import requests, httpx, fastapi, sqlalchemy, cryptography, lxml" || \
    (echo "依赖验证失败！" && exit 1)

# 复制整个项目到/app
COPY . .

# 设置工作目录为web/backend
WORKDIR /app/web/backend

# 创建必要的目录
RUN mkdir -p logs celery_broker celery_results data

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 默认命令（可被docker-compose覆盖）
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
