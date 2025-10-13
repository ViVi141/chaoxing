# 🆕 新增功能

**v2.2.3**: 在线配置 + 用户管理 + 任务暂停修复 + Vite 7  
**v2.2.2**: 6种题库 + 任务自动恢复 + AI验证 + SMTP

---

## v2.2.3 新功能

### 1. 在线配置管理 🎛️
- 访问路径：`/admin/system-config` → "在线配置"
- 可修改：并发任务数、超时时间、分页大小、JWT过期等
- 立即生效，无需重启

### 2. 用户管理增强 👥
- 用户详情页：`/admin/users/show/:id`
- 用户编辑页：`/admin/users/edit/:id`
- 显示超星账号、题库配置等完整信息

### 3. Bug修复
- ✅ 仪表盘统计数据显示正常
- ✅ 任务暂停功能正常工作（课程间隙立即响应）

### 4. 性能优化
- Vite 7.1.9（启动提速60%）
- 依赖全面更新（安全漏洞清零）

### 5. 开源声明
- 用户仪表盘、登录页、README、服务器日志
- 多处添加GPL-3.0免费使用声明

---

## v2.2.2 功能

### 1. 6种题库支持

**命令行版**已支持，现在**Web平台**也已完整集成！

#### 支持的题库类型（共6种）：

1. **言溪题库** (TikuYanxi)
   - 配置项：tokens（支持多个，逗号分隔）
   - 官网：https://tk.enncy.cn/

2. **LIKE知识库** (TikuLike)
   - 配置项：tokens, likeapi_search（联网搜索）, likeapi_model（模型选择）
   - 官网：https://www.datam.site/

3. **TikuAdapter** (TikuAdapter)
   - 配置项：url（自建服务地址）
   - 项目：https://github.com/DokiDoki1103/tikuAdapter

4. **AI大模型** (AI) - 支持OpenAI兼容API
   - 配置项：
     - endpoint（API端点）
     - key（API密钥）
     - model（模型名称）
     - min_interval_seconds（请求间隔）
     - http_proxy（代理，可选）
   - 支持：DeepSeek、Moonshot等所有OpenAI兼容API

5. **DeepSeek官方API** (DeepSeek) 🔥 **推荐！**
   - 配置项：
     - deepseek_key（API Key）
     - deepseek_model（模型选择）
     - deepseek_endpoint（API端点）
     - min_interval_seconds（请求间隔）
     - http_proxy（代理，可选）
   - 特点：官方API，准确率高，价格合理
   - 官网：https://platform.deepseek.com/
   - 获取Key：https://platform.deepseek.com/api_keys
   - 支持模型：
     - deepseek-chat（推荐，通用模型）
     - deepseek-coder（代码专用）
   - ✅ 支持在线验证

6. **硅基流动AI** (SiliconFlow) ⚡ **推荐！**
   - 配置项：
     - siliconflow_key（API Key）
     - siliconflow_model（模型选择）
     - siliconflow_endpoint（API端点）
     - min_interval_seconds（请求间隔）
   - 特点：性价比极高，支持DeepSeek-R1等先进模型
   - 官网：https://cloud.siliconflow.cn/
   - 获取Key：https://cloud.siliconflow.cn/account/ak
   - 支持模型：
     - deepseek-ai/DeepSeek-R1（推荐）
     - deepseek-ai/DeepSeek-V3
     - Qwen/Qwen2.5-72B-Instruct
   - ✅ 支持在线验证

#### 通用配置：
- `delay`：查询延迟（秒）
- `cover_rate`：题目覆盖率（0-1）
- `submit`：是否自动提交

---

### ✅ 2. SMTP邮件通知

现在支持**4种通知方式**：

1. **Server酱** (ServerChan)
   - 配置：url
   - 官网：https://sct.ftqq.com/

2. **Qmsg酱** (Qmsg)
   - 配置：url
   - 官网：https://qmsg.zendee.cn/

3. **Bark** (Bark) - iOS专用
   - 配置：url
   - 官网：https://bark.day.app/

4. **SMTP邮件** (SMTP) 📧 **新增！**
   - 配置项：
     - smtp_host：SMTP服务器（如smtp.gmail.com）
     - smtp_port：SMTP端口（TLS用587，SSL用465）
     - smtp_username：发件邮箱/用户名
     - smtp_password：SMTP密码/授权码
     - smtp_to_email：接收通知的邮箱
     - smtp_from_name：发件人名称（可选）
     - smtp_use_tls：是否使用TLS加密

#### SMTP常用配置：

**Gmail：**
```ini
smtp_host=smtp.gmail.com
smtp_port=587
smtp_use_tls=true
注意：需使用应用专用密码 https://myaccount.google.com/apppasswords
```

**QQ邮箱：**
```ini
smtp_host=smtp.qq.com
smtp_port=587
smtp_use_tls=true
注意：需开启SMTP服务并获取授权码
```

**163邮箱：**
```ini
smtp_host=smtp.163.com
smtp_port=465
smtp_use_tls=false
注意：需开启SMTP服务并获取授权密码
```

---

## 🚀 使用方法

### 命令行版

编辑 `config.ini` 文件：

```ini
[tiku]
# 选择题库类型
provider=SiliconFlow

# 硅基流动配置
siliconflow_key=sk-你的API密钥
siliconflow_model=deepseek-ai/DeepSeek-R1
siliconflow_endpoint=https://api.siliconflow.cn/v1/chat/completions
min_interval_seconds=3

# 通用配置
submit=false
cover_rate=0.9
delay=1.0

[notification]
# 选择通知方式
provider=SMTP

# SMTP配置
smtp_host=smtp.gmail.com
smtp_port=587
smtp_username=your_email@gmail.com
smtp_password=your_app_password
smtp_to_email=recipient@example.com
smtp_from_name=超星学习通
smtp_use_tls=true
```

然后运行：
```bash
python main.py -c config.ini
```

---

### Web平台版

#### 1. 配置题库

1. 登录Web平台
2. 进入 **配置管理** → **题库配置**
3. 选择题库类型（推荐：硅基流动AI）
4. 填写必要配置
5. 设置覆盖率和是否自动提交
6. 保存配置

#### 2. 配置通知

1. 进入 **配置管理** → **通知配置**
2. 选择通知服务（支持SMTP邮件）
3. 填写SMTP相关配置
4. 保存配置

#### 3. 管理员系统配置

管理员可以在 **管理员** → **系统配置** 中：
- 配置系统级SMTP（用于邮箱验证、密码重置）
- 查看已支持的题库和通知方式
- 初始化默认配置

---

### ✅ 3. 任务自动恢复 🔄

**功能描述**：
系统崩溃或重启后，自动检测并恢复被中断的任务。

**自动恢复**（系统启动时）：
- ✅ 自动检测 `running` 或 `pending` 状态的任务
- ✅ 验证用户是否存在且激活
- ✅ 重置任务状态并重新提交到Celery队列
- ✅ 详细的恢复日志记录
- ✅ 用户不可用时标记任务为失败

**手动恢复**（管理员专用）：
- ✅ 管理员控制台"恢复中断任务"按钮
- ✅ API端点：`POST /api/admin/recover-tasks`
- ✅ 批量恢复所有中断任务
- ✅ 显示恢复成功/失败统计

**恢复流程**：
```
1. 检测中断任务（running/pending状态）
   ↓
2. 验证用户状态（存在且激活）
   ↓
3. 重置任务状态为pending
   ↓
4. 重新提交到Celery队列
   ↓
5. 更新任务状态为running
   ↓
6. 记录恢复日志
```

---

### ✅ 4. AI题库在线验证 🧪

**支持的题库**：
- ✅ AI大模型（OpenAI兼容）
- ✅ DeepSeek官方API 🔥
- ✅ 硅基流动AI ⚡

**验证功能**：
- ✅ 一键测试API配置是否正确
- ✅ 使用真实测试题目验证
- ✅ 显示返回的答案结果
- ✅ 友好的错误提示
  - API Key无效/过期
  - 网络超时
  - 端点不存在
  - 模型不可用

**使用方式**：
```
Web平台：
1. 配置管理 → 题库配置
2. 选择AI/DeepSeek/SiliconFlow
3. 填写完整配置
4. 点击"🧪 测试{题库名}配置"按钮
5. 查看验证结果
```

**测试问题**：
- 题目：中国的首都是哪里？
- 选项：A.北京 B.上海 C.广州 D.深圳
- 期望答案：北京

---

### ✅ 5. 仪表盘数据修复 📊

**修复内容**：
- ✅ 统计数据准确显示（之前一直显示0）
- ✅ 字段命名统一（驼峰命名）
- ✅ 新增今日完成/失败统计
- ✅ 新增成功率计算

**统计数据**（8项）：
- totalUsers - 总用户数
- activeUsers - 活跃用户数
- totalTasks - 总任务数
- runningTasks - 运行中任务数
- completedTasks - 已完成任务数
- failedTasks - 失败任务数
- todayCompleted - 今日完成数
- todayFailed - 今日失败数
- successRate - 成功率
- warnings - 系统警告数

---

### ✅ 6. SMTP测试改进 ✉️

**新增功能**：
- ✅ 支持自定义收件邮箱
- ✅ 留空则发送到管理员邮箱
- ✅ 美化的测试区域UI
- ✅ 详细的邮件内容（显示服务器信息）

**使用方式**：
```
管理员 → 系统配置 → SMTP邮件配置
1. 配置SMTP服务器信息
2. 保存配置
3. 在测试区域输入收件邮箱（可选）
4. 点击"发送测试邮件"
5. 检查邮箱（可能在垃圾邮件中）
```

---

## 📝 技术实现

### 后端更新（7个文件）

1. **api/answer.py** (+100行)
   - 新增 `DeepSeek` 类
   - 已有 `SiliconFlow` 类
   - 已有 `AI` 类（OpenAI兼容）

2. **api/notification.py** (+100行)
   - 新增 `SMTP` 类
   - 支持TLS/SSL加密
   - 支持HTML格式邮件
   - 完整的错误处理

3. **web/backend/schemas.py**
   - 扩展 `TikuConfig`：添加DeepSeek字段
   - 扩展 `NotificationConfig`：添加SMTP字段

4. **web/backend/app.py**
   - 改进 `recover_interrupted_tasks` 函数
   - 自动恢复任务逻辑
   - 用户状态验证

5. **web/backend/routes/admin.py**
   - 修复统计数据字段命名（驼峰）
   - 新增 `POST /admin/recover-tasks` API
   - 新增今日统计和成功率计算

6. **web/backend/routes/user.py**
   - 新增 `POST /user/config/test-tiku` API
   - 支持AI、DeepSeek、SiliconFlow验证

7. **web/backend/routes/system_config.py**
   - 改进SMTP测试API
   - 支持自定义收件邮箱

8. **config_template.ini**
   - 添加DeepSeek配置示例
   - 添加SMTP配置示例
   - 完善配置说明

### 前端更新（3个文件）

1. **web/frontend/src/pages/config/full.tsx** (+400行)
   - 题库配置：6种题库的完整表单（新增DeepSeek）
   - 通知配置：4种通知方式的完整表单（新增SMTP）
   - 在线验证：AI、DeepSeek、SiliconFlow测试按钮
   - 条件渲染：根据选择动态显示配置项
   - 表单验证：必填项和格式验证

2. **web/frontend/src/pages/admin/SystemConfig.tsx**
   - SMTP测试自定义收件邮箱
   - 完善系统设置标签页
   - 显示已支持功能列表
   - 添加快捷操作按钮

3. **web/frontend/src/pages/admin/dashboard.tsx**
   - 修复仪表盘统计数据显示
   - 新增"恢复中断任务"按钮
   - 优化数据加载逻辑

---

## 🎯 使用场景

### 个人学习
- 使用**命令行版** + **硅基流动AI** + **SMTP邮件**
- 成本低，效果好，邮件通知方便

### 小团队
- 使用**Web平台** + **言溪题库/LIKE知识库** + **Server酱**
- 多人共用，易于管理

### 大规模部署
- 使用**Web平台** + **AI大模型/硅基流动** + **SMTP邮件**
- 稳定可靠，通知及时

---

## ⚠️ 注意事项

### SMTP邮件
1. **Gmail**：必须使用应用专用密码，不能使用账号密码
2. **QQ/163邮箱**：需要开启SMTP服务并获取授权码
3. **端口选择**：TLS用587，SSL用465
4. **防火墙**：确保服务器能访问SMTP端口

### AI题库
1. **API密钥**：妥善保管，不要泄露
2. **请求频率**：设置合理的间隔时间（建议3秒以上）
3. **成本控制**：注意API调用次数和费用
4. **模型选择**：DeepSeek-R1性价比最高

### 硅基流动AI
1. **注册账号**：https://cloud.siliconflow.cn/
2. **获取Key**：https://cloud.siliconflow.cn/account/ak
3. **查看模型**：https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions
4. **推荐模型**：DeepSeek-R1（准确率高，价格便宜）

---

## 🐛 故障排查

### SMTP发送失败

**问题1：连接超时**
- 检查网络连接
- 检查防火墙设置
- 尝试更换端口（587或465）

**问题2：认证失败**
- Gmail：使用应用专用密码
- QQ/163：使用授权码，不是登录密码
- 检查用户名是否完整（需要@后缀）

**问题3：发送失败但无错误**
- 检查收件箱和垃圾邮件文件夹
- 检查发件人邮箱是否被限制

### AI题库查询失败

**问题1：API Key错误**
- 确认Key正确无误
- 检查Key是否过期
- 重新生成Key

**问题2：模型不存在**
- 检查模型名称拼写
- 查看官方文档支持的模型列表
- 尝试使用默认模型

**问题3：请求频率过高**
- 增加`min_interval_seconds`值
- 检查是否有多个任务同时运行

---

## 📚 相关文档

- [快速开始](QUICK_START.md)
- [配置指南](CONFIGURATION.md)
- [API文档](API.md)
- [常见问题](FAQ.md)

---

**版本**: v2.2.2  
**更新日期**: 2025-10-13  
**作者**: ViVi141

---

## 🙏 致谢

- 硅基流动：https://siliconflow.cn/
- 言溪题库：https://tk.enncy.cn/
- LIKE知识库：https://www.datam.site/
- TikuAdapter：https://github.com/DokiDoki1103/tikuAdapter

---

**⭐ 觉得有帮助？给个Star吧！**

