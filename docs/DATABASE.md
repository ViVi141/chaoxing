# 🗄️ 数据库设计

## 数据库表结构

### users - 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(80) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希(bcrypt) |
| email | VARCHAR(120) | 邮箱（唯一） |
| email_verified | BOOLEAN | 邮箱验证状态 |
| role | VARCHAR(20) | 角色(user/admin) |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| last_login | DATETIME | 最后登录 |

### user_configs - 用户配置表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键→users.id |
| cx_username | VARCHAR(11) | 超星手机号 |
| cx_password_encrypted | TEXT | 加密后的超星密码 |
| use_cookies | BOOLEAN | 是否使用Cookie登录 |
| cookies_data | TEXT | Cookie数据(JSON) |
| speed | FLOAT | 播放倍速(1.0-2.0) |
| notopen_action | VARCHAR(20) | 未开放章节处理策略 |
| tiku_config | TEXT | 题库配置(JSON) |
| notification_config | TEXT | 通知配置(JSON) |
| updated_at | DATETIME | 更新时间 |

### tasks - 任务表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键→users.id |
| name | VARCHAR(200) | 任务名称 |
| course_ids | TEXT | 课程ID列表(JSON) |
| status | VARCHAR(20) | 状态(pending/running/completed/failed/cancelled) |
| progress | INTEGER | 进度(0-100) |
| celery_task_id | VARCHAR(255) | Celery任务ID |
| created_at | DATETIME | 创建时间 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| error_msg | TEXT | 错误信息 |
| completed_courses | INTEGER | 已完成课程数 |
| total_courses | INTEGER | 总课程数 |

### task_logs - 任务日志表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 外键→tasks.id |
| level | VARCHAR(20) | 日志级别(INFO/WARNING/ERROR) |
| message | TEXT | 日志内容 |
| created_at | DATETIME | 创建时间 |

### email_verifications - 邮箱验证表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键→users.id |
| email | VARCHAR(120) | 邮箱 |
| token | VARCHAR(64) | 验证令牌 |
| token_type | VARCHAR(20) | 类型(verify_email/reset_password) |
| expires_at | DATETIME | 过期时间 |
| is_used | BOOLEAN | 是否已使用 |
| created_at | DATETIME | 创建时间 |

## 关系图

```
users (1)───(1) user_configs
  │
  └─(1)───(N) tasks
              │
              └─(1)───(N) task_logs
```

## 索引设计

### 性能优化索引
- `users.username` - 唯一索引
- `users.email` - 唯一索引
- `tasks.user_id` - 普通索引
- `tasks.status` - 普通索引
- `task_logs.task_id` - 普通索引
- `task_logs.created_at` - 普通索引

## 级联删除

- 删除用户 → 自动删除配置和任务
- 删除任务 → 自动删除任务日志
- 使用 `ondelete='CASCADE'` 确保数据一致性

