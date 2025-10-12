# 👨‍💻 开发指南

## 开发环境搭建

### 1. 克隆项目
```bash
git clone https://github.com/ViVi141/chaoxing.git
cd chaoxing
```

### 2. 后端开发环境
```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cd web/backend
cp ../env.example .env
# 编辑.env文件

# 启动后端
python app.py

# 启动Celery
celery -A celery_app worker --loglevel=info
```

### 3. 前端开发环境
```bash
cd web/frontend
npm install
npm run dev
```

---

## 项目结构

```
chaoxing/
├── api/                  # 核心API模块（命令行和Web共用）
├── web/
│   ├── backend/          # Web后端
│   │   ├── routes/       # API路由
│   │   ├── tasks/        # Celery任务
│   │   └── data/         # 数据文件（git忽略）
│   └── frontend/         # Web前端
│       └── src/
│           ├── pages/    # 页面组件
│           └── providers/  # 数据提供者
├── docs/                 # 项目文档
├── tools/                # 工具脚本
└── main.py               # 命令行版入口
```

---

## 开发工作流

### 1. 创建功能分支
```bash
git checkout -b feature/your-feature
```

### 2. 开发和测试
```bash
# 后端测试
pytest web/backend/tests/

# 前端测试
cd web/frontend
npm run build  # 构建测试

# 代码检查
black .  # 格式化
flake8 .  # 代码检查
```

### 3. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feature/your-feature
```

---

## 代码规范

### Python
- 遵循 PEP 8
- 使用Google代码风格
- 使用black格式化
- 类型提示（Type Hints）

### TypeScript/React
- 使用函数组件
- Hooks优先
- Props类型定义
- 组件命名：PascalCase

---

## 调试技巧

### 后端调试
```python
# 在代码中添加
from api.logger import logger
logger.debug("调试信息")
```

### 前端调试
```typescript
console.log('[Component]', data);
```

### 数据库查询
```bash
# SQLite
sqlite3 web/backend/data/chaoxing.db
.tables
SELECT * FROM tasks;
```

---

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 等待代码审查

---

## 技术栈升级

查看当前版本：
- `requirements.txt` - Python依赖
- `web/frontend/package.json` - Node依赖

升级流程：
1. 备份代码
2. 升级依赖文件
3. 运行测试
4. 提交更新

