# 测试指南

本目录包含超星学习通项目的所有自动化测试。

## 📁 目录结构

```
tests/
├── conftest.py          # pytest配置和公共fixtures
├── unit/                # 单元测试
│   ├── test_cipher.py   # 加密解密测试
│   ├── test_answer.py   # 题库功能测试
│   └── ...
├── integration/         # 集成测试
│   ├── test_auth_flow.py    # 认证流程测试
│   ├── test_user_api.py     # 用户API测试
│   └── ...
└── e2e/                 # 端到端测试
    └── ...
```

## 🚀 快速开始

### 安装测试依赖

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=api --cov=web/backend --cov-report=html
```

### 运行特定类型的测试

```bash
# 只运行单元测试
pytest tests/unit -v

# 只运行集成测试
pytest tests/integration -v

# 只运行标记为auth的测试
pytest -m auth

# 只运行特定文件
pytest tests/unit/test_cipher.py -v
```

## 📊 测试覆盖率

查看覆盖率报告：

```bash
# 生成HTML报告
pytest --cov=api --cov=web/backend --cov-report=html

# 打开报告（在浏览器中）
# Windows: start htmlcov/index.html
# Linux/macOS: open htmlcov/index.html
```

当前目标：**80%+** 覆盖率

## 🏷️ 测试标记

使用pytest标记来组织测试：

```python
@pytest.mark.unit          # 单元测试
@pytest.mark.integration   # 集成测试
@pytest.mark.e2e           # 端到端测试
@pytest.mark.slow          # 慢速测试
@pytest.mark.auth          # 认证相关
@pytest.mark.api           # API测试
@pytest.mark.database      # 数据库测试
```

运行特定标记的测试：

```bash
pytest -m "unit and not slow"    # 运行快速单元测试
pytest -m "integration or e2e"   # 运行所有集成和E2E测试
```

## 🔧 编写测试

### 单元测试示例

```python
import pytest
from api.cipher import AESCipher

@pytest.mark.unit
def test_encrypt_decrypt():
    """测试加密和解密"""
    cipher = AESCipher()
    text = "测试数据"
    
    encrypted = cipher.encrypt(text)
    decrypted = cipher.decrypt(encrypted)
    
    assert decrypted == text
```

### 集成测试示例

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.integration
@pytest.mark.database
async def test_user_creation(async_db_session: AsyncSession):
    """测试用户创建"""
    user = User(username="test", email="test@example.com")
    async_db_session.add(user)
    await async_db_session.commit()
    
    assert user.id is not None
```

## 🛠️ 常用Fixtures

项目提供了以下常用fixtures（在`conftest.py`中定义）：

- `async_db_session` - 异步数据库会话（测试用内存数据库）
- `sync_db_session` - 同步数据库会话
- `test_user` - 测试用户
- `test_admin` - 测试管理员
- `mock_tiku_response` - 模拟题库响应
- `mock_course_data` - 模拟课程数据

使用示例：

```python
async def test_something(async_db_session, test_user):
    # 使用fixtures
    assert test_user.username == "testuser"
```

## 📈 CI/CD集成

测试自动在以下情况运行：

1. **推送到main/develop分支**
2. **创建Pull Request**
3. **本地运行** `pytest`

GitHub Actions配置：`.github/workflows/ci.yml`

## 🐛 调试测试

### 详细输出

```bash
# 显示详细输出
pytest -v

# 显示print语句
pytest -s

# 详细+print
pytest -vv -s
```

### 只运行失败的测试

```bash
# 第一次运行（会记录失败）
pytest

# 只重跑失败的测试
pytest --lf

# 先跑失败的，再跑其他
pytest --ff
```

### 调试特定测试

```bash
# 在失败时进入pdb调试器
pytest --pdb

# 在第一个失败后停止
pytest -x
```

## 📝 测试最佳实践

1. **测试命名**：使用描述性名称
   ```python
   def test_user_login_with_valid_credentials()
   def test_task_creation_fails_without_authentication()
   ```

2. **AAA模式**：Arrange-Act-Assert
   ```python
   def test_something():
       # Arrange - 准备
       user = User(username="test")
       
       # Act - 执行
       result = user.do_something()
       
       # Assert - 断言
       assert result == expected
   ```

3. **独立性**：每个测试应该独立，不依赖其他测试

4. **清理**：使用fixtures自动清理测试数据

5. **Mock外部依赖**：不要依赖真实的外部API

## 🔗 相关资源

- [pytest文档](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [项目CI/CD配置](.github/workflows/ci.yml)

## 📊 当前状态

- ✅ 测试框架已配置
- ✅ 基础fixtures已创建
- ✅ 单元测试：加密、题库
- ⏳ 集成测试：认证流程
- ⏳ API测试：待完善
- ⏳ E2E测试：待添加

**下一步**：
1. 添加更多单元测试（通知、处理器等）
2. 完善API集成测试
3. 添加E2E测试
4. 提升覆盖率到80%+

---

**贡献者**：欢迎添加更多测试用例！

