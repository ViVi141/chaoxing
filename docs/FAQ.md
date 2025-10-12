# ❓ 常见问题

## 安装相关

### Q: Python版本要求？
**A:** Python 3.10、3.11或3.12。不支持3.13（ddddocr限制）。

### Q: 如何安装依赖？
**A:** 
```bash
pip install -r requirements.txt  # 后端
cd web/frontend && npm install   # 前端
```

### Q: 虚拟环境如何创建？
**A:** 
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

---

## 使用相关

### Q: 如何启动服务？
**A:** 
```bash
# 方式1：一键启动（Windows）
启动Refine完整版.bat

# 方式2：分别启动
cd web/backend && python app.py         # 终端1
cd web/backend && celery -A celery_app worker  # 终端2
cd web/frontend && npm run dev          # 终端3
```

### Q: 默认管理员密码是什么？
**A:** 
- 用户名：`admin`
- 密码：`Admin@123`
- 请登录后立即修改！

### Q: 任务为什么不执行？
**A:** 检查：
1. Celery worker是否启动
2. 是否配置了超星账号
3. 超星密码是否正确
4. 查看任务日志

### Q: 如何查看日志？
**A:**
- 后端日志：`web/backend/logs/`
- Celery日志：控制台输出
- 任务日志：Web界面任务详情页

---

## 错误处理

### Q: 登录失败怎么办？
**A:**
1. 检查超星账号密码
2. 查看后端日志错误信息
3. 尝试清除cookies重新登录

### Q: 任务一直显示running？
**A:**
1. 检查Celery worker是否正常
2. 查看任务日志
3. 重启后端会自动标记为failed
4. 然后可以重试

### Q: WebSocket连接失败？
**A:**
1. 检查JWT token是否有效
2. 检查后端是否启动
3. 查看浏览器控制台错误

---

## 性能相关

### Q: 支持多少并发用户？
**A:**
- 简单模式：50-100用户
- 标准模式：500-1000用户

### Q: 一个用户可以同时运行多少任务？
**A:** 默认3个，可在配置中修改`MAX_CONCURRENT_TASKS_PER_USER`

---

## 其他问题

### Q: 可以商用吗？
**A:** 不可以。项目遵循GPL-3.0协议，禁止商业使用。

### Q: 如何贡献代码？
**A:** 
1. Fork项目
2. 创建功能分支
3. 提交Pull Request

### Q: 遇到bug怎么办？
**A:** 
1. 查看日志文件
2. 搜索已有Issues
3. 提交新Issue并附上日志

