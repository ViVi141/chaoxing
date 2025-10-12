# 📡 API接口文档

> 所有API接口说明（v2.1.0）

**Base URL:** `http://localhost:8000/api`

---

## 认证接口

### POST /auth/register
注册新用户

**请求：**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST /auth/login
用户登录

### POST /auth/logout
退出登录

### GET /auth/me
获取当前用户信息

### POST /auth/forgot-password
忘记密码

### POST /auth/reset-password
重置密码

---

## 用户接口

### GET /user/config
获取用户配置

### PUT /user/config
更新用户配置

**请求：**
```json
{
  "cx_username": "13800138000",
  "cx_password": "your_password",
  "speed": 1.5,
  "notopen_action": "retry"
}
```

### PUT /user/password
修改密码

### GET /user/profile
获取用户资料和统计

---

## 任务接口

### GET /tasks
获取任务列表（分页）

**参数：**
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `status`: 状态过滤（可选）

### POST /tasks
创建新任务

**请求：**
```json
{
  "name": "学习任务",
  "course_ids": ["123456", "789012"]
}
```

### GET /tasks/{id}
获取任务详情（包含日志）

**响应：**
```json
{
  "id": 1,
  "name": "学习任务",
  "status": "running",
  "progress": 35,
  "logs": [
    {
      "id": 1,
      "level": "INFO",
      "message": "当前任务: 视频...",
      "created_at": "2025-10-12T12:00:00"
    }
  ]
}
```

### POST /tasks/{id}/start
启动任务

### POST /tasks/{id}/pause
暂停任务

### POST /tasks/{id}/resume
恢复任务

### POST /tasks/{id}/cancel
取消任务

### POST /tasks/{id}/retry
重试失败的任务

### DELETE /tasks/{id}
删除任务

### GET /tasks/{id}/logs
获取任务日志

---

## 课程接口

### GET /courses/list
获取超星课程列表

**响应：**
```json
[
  {
    "courseId": "123456",
    "courseName": "课程名称",
    "teacherName": "教师",
    "progress": 50
  }
]
```

---

## 管理员接口

**权限要求：** 管理员

### GET /admin/users
获取所有用户

### GET /admin/users/{id}
获取用户详情

### PUT /admin/users/{id}
更新用户

### DELETE /admin/users/{id}
删除用户

### GET /admin/tasks
监控所有任务

### POST /admin/tasks/{id}/force-stop
强制停止任务

### GET /admin/statistics
系统统计数据

---

## WebSocket

### WS /ws/connect?token={jwt_token}
WebSocket连接

**发送消息：**
```json
{
  "type": "subscribe_task",
  "task_id": 1
}
```

**接收消息：**
```json
{
  "type": "task_update",
  "task_id": 1,
  "data": {
    "progress": 35,
    "current_item": "🎬 视频名称",
    "item_progress": 50,
    "item_current_time": 120,
    "item_total_time": 1800
  }
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

**Swagger文档：** http://localhost:8000/api/docs

