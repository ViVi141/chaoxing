# VS Code 配置说明

本文件夹包含VS Code的推荐配置。

## 📋 使用方法

### 1. 复制配置文件

```bash
# Windows (PowerShell)
Copy-Item .vscode/settings.json.example .vscode/settings.json
Copy-Item .vscode/launch.json.example .vscode/launch.json

# Linux/Mac
cp .vscode/settings.json.example .vscode/settings.json
cp .vscode/launch.json.example .vscode/launch.json
```

### 2. 重启VS Code

配置会自动生效。

## 📝 配置说明

### settings.json
- Python解释器自动指向 `.venv/`
- 自动激活虚拟环境
- 配置代码格式化（black）
- 配置代码检查（flake8）
- 排除不必要的文件夹

### launch.json
- 命令行版调试配置
- Web后端调试配置
- Celery Worker调试配置

## 🔧 手动配置

如果不想使用示例配置，手动设置Python解释器：

1. 按 `Ctrl+Shift+P`（或 `Cmd+Shift+P`）
2. 输入 "Python: Select Interpreter"
3. 选择 `.venv/Scripts/python.exe`（Windows）或 `.venv/bin/python`（Linux/Mac）

## ✅ 验证配置

打开任意Python文件，检查：
- 左下角显示 `(.venv)` 或 `.venv` 
- 没有导入错误提示
- 代码自动补全正常工作

---

**注意**：实际的 `settings.json` 和 `launch.json` 文件不会被git跟踪（已加入.gitignore）。

