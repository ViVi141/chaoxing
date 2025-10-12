# 📏 代码规范

## Python代码规范

### 遵循Google Python Style Guide

```python
# ✅ 好的示例
def get_user_tasks(user_id: int, status: Optional[str] = None) -> List[Task]:
    """
    获取用户的任务列表
    
    Args:
        user_id: 用户ID
        status: 任务状态过滤（可选）
    
    Returns:
        List[Task]: 任务列表
    """
    query = select(Task).where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    return query.all()


# ❌ 避免
def getUserTasks(userId,status=None):  # 命名不规范，缺少类型提示
    return select(Task).where(Task.user_id==userId).all()  # 缺少文档字符串
```

### 命名规范
- 函数/变量：`snake_case`
- 类名：`PascalCase`
- 常量：`UPPER_CASE`
- 私有成员：`_leading_underscore`

### 类型提示
```python
from typing import List, Optional, Dict

def process_data(data: Dict[str, any]) -> Optional[str]:
    pass
```

---

## TypeScript/React代码规范

### 组件命名
```typescript
// ✅ 组件名：PascalCase
export const TaskShowFull = () => {
  return <div>...</div>;
};

// ❌ 避免
export const taskShowFull = () => {};  // 应该是PascalCase
```

### Props类型定义
```typescript
// ✅ 定义Props接口
interface TaskCardProps {
  taskId: number;
  onUpdate?: () => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ taskId, onUpdate }) => {
  // ...
};
```

### Hooks使用
```typescript
// ✅ 使用React Hooks
const [loading, setLoading] = useState(false);
const { data, refetch } = useShow();

useEffect(() => {
  // 副作用
}, [dependencies]);
```

---

## 文件组织

### 后端
```
routes/
├── auth.py      # 认证相关
├── user.py      # 用户相关
├── task.py      # 任务相关
└── admin.py     # 管理员相关
```

### 前端
```
pages/
├── auth/        # 认证页面
├── tasks/       # 任务页面
├── admin/       # 管理员页面
└── config/      # 配置页面
```

---

## Git Commit规范

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具

### 示例
```bash
git commit -m "feat(task): 添加任务恢复功能"
git commit -m "fix(auth): 修复JWT过期问题"
git commit -m "docs: 更新API文档"
```

---

## 代码审查清单

### 功能
- [ ] 功能完整实现
- [ ] 边界情况处理
- [ ] 错误处理

### 安全
- [ ] 输入验证
- [ ] 权限检查
- [ ] 数据隔离

### 性能
- [ ] 数据库查询优化
- [ ] 避免N+1查询
- [ ] 合理使用缓存

### 代码质量
- [ ] 符合代码规范
- [ ] 有适当注释
- [ ] 函数长度合理
- [ ] 避免重复代码

