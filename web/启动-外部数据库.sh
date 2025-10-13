#!/bin/bash
# 使用外部数据库启动脚本

echo "========================================="
echo "  超星学习通 - 外部数据库模式启动"
echo "========================================="
echo ""
echo "此模式使用你已有的PostgreSQL和Redis"
echo "不会创建新的数据库容器"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 检测到首次启动，创建配置文件..."
    cp "你的配置.env" ".env"
    echo ""
    echo "⚠️  已创建 .env 配置文件"
    echo "请检查配置是否正确，然后重新运行此脚本"
    echo ""
    echo "配置文件位置：web/.env"
    echo ""
    exit 0
fi

echo "✅ 找到配置文件 .env"
echo ""

# 停止旧容器
echo "🧹 停止旧容器..."
docker compose -f docker-compose.external-db.yml down 2>/dev/null

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p backend/data backend/logs
chmod 777 backend/data backend/logs

# 拉取最新镜像
echo "📥 拉取最新Docker镜像..."
docker compose -f docker-compose.external-db.yml pull

# 启动容器
echo "🚀 启动容器..."
docker compose -f docker-compose.external-db.yml up -d

# 等待启动
echo "⏳ 等待服务启动（30秒）..."
sleep 30

# 检查状态
echo ""
echo "📊 容器状态："
docker compose -f docker-compose.external-db.yml ps

# 查看日志
echo ""
echo "📋 后端日志（最后20行）："
docker logs chaoxing_backend --tail 20

# 健康检查
echo ""
echo "🔍 服务健康检查..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务启动中，请稍等..."
    echo ""
    echo "💡 查看完整日志："
    echo "   docker logs chaoxing_backend -f"
fi

echo ""
echo "========================================="
echo "  🎉 启动完成！"
echo "========================================="
echo ""
echo "访问地址：http://localhost:8000"
echo ""
echo "使用的数据库："
echo "  PostgreSQL: 1Panel-postgresql-LEsZ"
echo "  Redis: 1Panel-redis-71AP"
echo ""
echo "查看日志："
echo "  docker logs chaoxing_backend -f"
echo "  docker logs chaoxing_celery -f"
echo ""
echo "停止服务："
echo "  docker compose -f docker-compose.external-db.yml down"
echo ""

