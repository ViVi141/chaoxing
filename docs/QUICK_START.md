# 🚀 快速开始指南

> 5分钟快速启动超星学习通自动化平台

---

## 方式一：Web平台（推荐）

### 前置要求
- Python 3.10-3.12
- Node.js 18+

### 一键启动（Windows）

```batch
# 双击运行
启动Refine完整版.bat
```

访问：http://localhost:5173

### 手动启动

**终端1 - 后端：**
```bash
cd web/backend
python app.py
```

**终端2 - Celery：**
```bash
cd web/backend
celery -A celery_app worker --loglevel=info
```

**终端3 - 前端：**
```bash
cd web/frontend
npm install  # 首次运行
npm run dev
```

### 首次使用

1. 访问 http://localhost:5173
2. 注册账号
3. 配置超星账号（配置管理）
4. 创建学习任务
5. 开始自动学习

---

## 方式二：命令行版

### 快速运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 直接运行
python main.py

# 3. 或使用配置文件
cp config_template.ini config.ini
# 编辑config.ini填写账号密码
python main.py -c config.ini
```

---

## Docker部署

```bash
cd web
docker-compose -f docker-compose.simple.yml up -d
```

访问：http://localhost:3000

---

## 默认管理员账号

- 用户名：`admin`
- 密码：`Admin@123`
- **请立即修改！**

---

**下一步：** 查看[完整文档](INDEX.md)

