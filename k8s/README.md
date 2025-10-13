# Kubernetes 部署指南

**版本**: v2.3.0  
**适用**: Kubernetes集群部署

---

## 📋 前置要求

- ✅ Kubernetes 1.20+
- ✅ kubectl已配置
- ✅ Ingress Controller（推荐Nginx Ingress）
- ✅ StorageClass（用于PVC）
- ✅ 可选：Helm 3+
- ✅ 可选：cert-manager（SSL证书）

---

## 🚀 快速部署

### 方式1：一键部署（推荐）

```bash
# 1. 应用所有配置
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f celery-deployment.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# 2. 等待Pod就绪
kubectl wait --for=condition=ready pod -l app=chaoxing-backend -n chaoxing --timeout=300s

# 3. 查看状态
kubectl get all -n chaoxing

# 4. 查看服务
kubectl get ingress -n chaoxing
```

### 方式2：使用脚本

```bash
# 创建部署脚本
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 开始部署Chaoxing到Kubernetes..."

# 应用配置
for file in namespace.yaml secret.yaml configmap.yaml postgres-pvc.yaml postgres-deployment.yaml redis-deployment.yaml backend-deployment.yaml celery-deployment.yaml ingress.yaml hpa.yaml; do
    echo "应用 $file..."
    kubectl apply -f $file
done

echo "⏳ 等待Pod就绪..."
kubectl wait --for=condition=ready pod -l app=chaoxing-backend -n chaoxing --timeout=300s

echo "✅ 部署完成！"
echo ""
echo "查看状态: kubectl get all -n chaoxing"
echo "查看日志: kubectl logs -f deployment/chaoxing-backend -n chaoxing"
echo "访问地址: https://chaoxing.example.com"
EOF

chmod +x deploy.sh
./deploy.sh
```

---

## 🔧 配置修改

### 1. 修改Secrets（重要！）

**生成安全密钥**:
```bash
# 生成SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用OpenSSL
openssl rand -base64 32
```

**编辑secret.yaml**:
```yaml
stringData:
  SECRET_KEY: "你生成的密钥"
  JWT_SECRET_KEY: "你生成的JWT密钥"
  POSTGRES_PASSWORD: "你的数据库密码"
  REDIS_PASSWORD: "你的Redis密码"
```

### 2. 修改Ingress域名

**编辑ingress.yaml**:
```yaml
spec:
  rules:
  - host: your-domain.com  # 改为你的域名
```

### 3. 修改副本数

**编辑backend-deployment.yaml**:
```yaml
spec:
  replicas: 2  # 改为需要的副本数
```

### 4. 修改资源限制

```yaml
resources:
  requests:
    memory: "256Mi"  # 根据实际调整
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

---

## 📊 查看状态

### 查看所有资源

```bash
kubectl get all -n chaoxing
```

### 查看Pod详情

```bash
kubectl describe pod <pod-name> -n chaoxing
```

### 查看日志

```bash
# 后端日志
kubectl logs -f deployment/chaoxing-backend -n chaoxing

# Celery日志
kubectl logs -f deployment/chaoxing-celery -n chaoxing

# 数据库日志
kubectl logs -f deployment/postgres -n chaoxing
```

### 查看事件

```bash
kubectl get events -n chaoxing --sort-by='.lastTimestamp'
```

---

## 🔄 更新部署

### 更新镜像版本

```bash
# 方式1：直接设置镜像
kubectl set image deployment/chaoxing-backend backend=ghcr.io/vivi141/chaoxing:v2.3.0 -n chaoxing

# 方式2：编辑deployment
kubectl edit deployment chaoxing-backend -n chaoxing

# 方式3：应用新的yaml
kubectl apply -f backend-deployment.yaml
```

### 滚动更新

```bash
# 查看滚动更新状态
kubectl rollout status deployment/chaoxing-backend -n chaoxing

# 暂停滚动更新
kubectl rollout pause deployment/chaoxing-backend -n chaoxing

# 继续滚动更新
kubectl rollout resume deployment/chaoxing-backend -n chaoxing

# 回滚到上一版本
kubectl rollout undo deployment/chaoxing-backend -n chaoxing

# 查看历史版本
kubectl rollout history deployment/chaoxing-backend -n chaoxing
```

---

## 🔒 SSL/TLS配置

### 使用cert-manager

```bash
# 1. 安装cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 2. 创建ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# 3. 修改ingress.yaml添加TLS
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: chaoxing-tls
```

---

## 📈 监控

### 查看资源使用

```bash
kubectl top pods -n chaoxing
kubectl top nodes
```

### HPA状态

```bash
kubectl get hpa -n chaoxing
kubectl describe hpa chaoxing-backend-hpa -n chaoxing
```

### Prometheus指标（如果安装）

```yaml
# 添加到Service
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
```

---

## 🔧 进入容器调试

```bash
# 进入后端容器
kubectl exec -it deployment/chaoxing-backend -n chaoxing -- /bin/bash

# 进入数据库
kubectl exec -it deployment/postgres -n chaoxing -- psql -U chaoxing_user -d chaoxing_db

# 进入Redis
kubectl exec -it deployment/redis -n chaoxing -- redis-cli -a $(kubectl get secret chaoxing-secrets -n chaoxing -o jsonpath='{.data.REDIS_PASSWORD}' | base64 -d)
```

---

## 💾 数据备份

### 备份数据库

```bash
# 创建备份Job
kubectl create job --from=cronjob/postgres-backup manual-backup -n chaoxing

# 手动备份
kubectl exec deployment/postgres -n chaoxing -- pg_dump -U chaoxing_user chaoxing_db > backup.sql
```

### 恢复数据库

```bash
kubectl exec -i deployment/postgres -n chaoxing -- psql -U chaoxing_user chaoxing_db < backup.sql
```

---

## 🗑️ 删除部署

### 删除所有资源

```bash
kubectl delete namespace chaoxing
```

### 删除特定资源

```bash
kubectl delete deployment chaoxing-backend -n chaoxing
kubectl delete service chaoxing-backend -n chaoxing
kubectl delete pvc postgres-pvc -n chaoxing
```

---

## 🎯 生产环境建议

### 1. 资源配置

```yaml
# 后端（中等负载）
requests:
  memory: "512Mi"
  cpu: "500m"
limits:
  memory: "2Gi"
  cpu: "2000m"

# Celery Worker（高负载）
requests:
  memory: "512Mi"
  cpu: "500m"
limits:
  memory: "2Gi"
  cpu: "2000m"
```

### 2. 副本数配置

- **后端**: 最少2个，推荐3-5个
- **Celery Worker**: 根据任务量，推荐5-10个
- **Celery Beat**: 固定1个
- **数据库**: 1个（生产环境建议使用托管服务）
- **Redis**: 1个（或使用Redis集群）

### 3. 存储配置

- **数据库**: 至少20GB，使用SSD
- **Redis**: 至少5GB
- **StorageClass**: 使用高性能存储（如gp3、premium-ssd）

### 4. 网络配置

- 启用NetworkPolicy隔离
- 配置Ingress rate limiting
- 使用CDN加速静态资源

### 5. 安全配置

- 使用Kubernetes Secrets
- 启用RBAC
- 定期更新镜像
- 扫描漏洞

---

## 📝 架构图

```
Internet
   │
   ▼
Ingress Controller (Nginx)
   │
   ▼
Service (chaoxing-backend)
   │
   ├──▶ Backend Pod 1 ────┐
   ├──▶ Backend Pod 2 ────┤
   └──▶ Backend Pod 3 ────┤
                           │
                           ├──▶ PostgreSQL
                           └──▶ Redis ◀──── Celery Workers
```

---

## 🔗 相关文档

- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Nginx Ingress文档](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager文档](https://cert-manager.io/docs/)
- [Docker部署](../docs/DOCKER_SETUP.md)
- [完整文档](../docs/INDEX.md)

---

**GPL-3.0** 开源协议 | 完全免费使用

