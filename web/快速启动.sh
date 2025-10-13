#!/bin/bash
# 快速启动脚本 - 零配置部署

echo "========================================="
echo "  超星学习通自动化工具 - 快速启动"
echo "========================================="
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装！请先安装Docker"
    exit 1
fi

echo "✅ Docker已安装"

# 检查docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose未安装！请先安装Docker Compose v2"
    exit 1
fi

echo "✅ Docker Compose已安装"
echo ""

# 停止并删除旧容器
echo "🧹 清理旧容器..."
docker compose -f docker-compose.simple.yml down -v 2>/dev/null

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p backend/data backend/logs
chmod 777 backend/data backend/logs

# 拉取最新镜像
echo "📥 拉取最新Docker镜像..."
docker compose -f docker-compose.simple.yml pull

# 启动容器
echo "🚀 启动容器..."
docker compose -f docker-compose.simple.yml up -d --force-recreate

# 等待容器启动
echo "⏳ 等待服务启动（30秒）..."
sleep 30

# 检查容器状态
echo ""
echo "📊 容器状态："
docker compose -f docker-compose.simple.yml ps

# 检查后端日志
echo ""
echo "📋 后端日志（最后20行）："
docker logs chaoxing_backend --tail 20

# 检查健康状态
echo ""
echo "🔍 服务健康检查..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能还在启动中，请稍等片刻"
fi

echo ""
echo "========================================="
echo "  🎉 启动完成！"
echo "========================================="
echo ""
echo "访问地址：http://localhost:8000"
echo "或者：http://服务器IP:8000"
echo ""
echo "查看日志："
echo "  docker logs chaoxing_backend -f"
echo "  docker logs chaoxing_celery_lite -f"
echo ""
echo "停止服务："
echo "  docker compose -f docker-compose.simple.yml down"
echo ""

