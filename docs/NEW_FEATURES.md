# 🆕 新增功能说明

> 新增AI题库支持（含硅基流动）和SMTP邮件通知功能

---

## 📊 功能概览

本次更新完成了以下功能：

### ✅ 1. AI题库支持（包括硅基流动）

**命令行版**已支持，现在**Web平台**也已完整集成！

#### 支持的题库类型（共5种）：

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

5. **硅基流动AI** (SiliconFlow) ⚡ **推荐！**
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

## 📝 技术实现

### 后端更新

1. **api/notification.py**
   - 新增 `SMTP` 类
   - 支持TLS/SSL加密
   - 支持HTML格式邮件
   - 完整的错误处理

2. **api/answer.py**
   - 已有 `SiliconFlow` 类（命令行版已实现）
   - 已有 `AI` 类（OpenAI兼容）

3. **web/backend/schemas.py**
   - 扩展 `TikuConfig`：添加AI题库字段
   - 扩展 `NotificationConfig`：添加SMTP字段

4. **config_template.ini**
   - 添加SMTP配置示例
   - 完善硅基流动配置说明

### 前端更新

1. **web/frontend/src/pages/config/full.tsx**
   - 题库配置：5种题库的完整表单
   - 通知配置：4种通知方式的完整表单
   - 条件渲染：根据选择动态显示配置项
   - 表单验证：必填项和格式验证

2. **web/frontend/src/pages/admin/SystemConfig.tsx**
   - 完善系统设置标签页
   - 显示已支持功能列表
   - 添加快捷操作按钮

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

**版本**: v2.2.1  
**更新日期**: 2025-10-12  
**作者**: ViVi141

---

## 🙏 致谢

- 硅基流动：https://siliconflow.cn/
- 言溪题库：https://tk.enncy.cn/
- LIKE知识库：https://www.datam.site/
- TikuAdapter：https://github.com/DokiDoki1103/tikuAdapter

---

**⭐ 觉得有帮助？给个Star吧！**

