# 🔄 升级指南

---

## 升级到 v2.2.3

```bash
# 1. 更新代码
git pull

# 2. 更新Python依赖
cd web/backend
pip install -r requirements.txt

# 3. 更新Node.js依赖
cd web/frontend
npm install

# 4. 重启服务
cd ../..
cd web
python run_simple.py
```

### 可选步骤

访问 `/admin/system-config` → "在线配置" → "初始化配置"

---

## v2.2.3 更新内容

- ✅ 在线配置管理
- ✅ 用户详情/编辑
- ✅ 仪表盘数据修复
- ✅ 任务暂停修复
- ✅ Vite 7 + 依赖更新
- ✅ 开源声明

详见 [CHANGELOG.md](CHANGELOG.md)
