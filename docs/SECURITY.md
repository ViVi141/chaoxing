# 🔒 安全指南

## 安全特性

### 1. 身份认证
- JWT令牌认证（有效期24小时）
- bcrypt密码哈希存储
- 邮箱验证机制
- 密码重置功能

### 2. 数据加密
- 用户密码：bcrypt哈希（不可逆）
- 超星密码：Fernet加密（可逆）
- JWT密钥：环境变量配置
- 敏感日志自动脱敏

### 3. 权限控制
- 基于角色的访问控制(RBAC)
- 用户数据完全隔离
- 管理员权限严格验证
- WebSocket消息用户级隔离

### 4. 攻击防护
- SQL注入：SQLAlchemy ORM
- XSS：输入验证和过滤
- CSRF：JWT无状态认证
- 横向攻击：user_id强制过滤
- 纵向攻击：role严格验证

---

## 安全配置建议

### 生产环境必须

1. **使用强密钥**
```bash
# 生成强密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **启用HTTPS**
- 配置SSL证书
- 强制HTTPS重定向

3. **修改默认密码**
- 登录后立即修改admin密码
- 使用强密码（至少8字符，包含大小写字母和数字）

4. **限制CORS**
```python
CORS_ORIGINS=https://your-domain.com
```

5. **定期备份**
- 数据库文件
- 配置文件
- 用户数据

### 可选但推荐

1. **启用速率限制**
- 防止暴力破解
- 防止API滥用

2. **配置防火墙**
- 只开放必要端口
- 限制IP访问

3. **日志监控**
- 监控异常登录
- 监控API访问模式

---

## 数据隔离机制

### API层面
所有数据查询都包含用户ID过滤：

```python
# 示例：获取任务
select(Task).where(
    Task.id == task_id,
    Task.user_id == current_user.id  # 强制过滤
)
```

### WebSocket层面
消息订阅验证所有权：

```python
# 只能订阅自己的任务
if task.user_id != user.id:
    raise HTTPException(404, "任务不存在")
```

---

## 安全检查清单

### 部署前
- [ ] 修改所有默认密码
- [ ] 配置强密钥
- [ ] 启用HTTPS
- [ ] 配置正确的CORS
- [ ] 禁用DEBUG模式

### 运行中
- [ ] 定期备份数据库
- [ ] 监控日志异常
- [ ] 检查用户活动
- [ ] 更新依赖包

---

## 报告安全问题

如发现安全漏洞，请发送邮件至：747384120@qq.com

