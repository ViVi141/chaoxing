<template>
  <div class="setup-container">
    <el-card class="setup-card">
      <template #header>
        <div class="card-header">
          <h1>
            <el-icon><Setting /></el-icon>
            超星学习通管理平台 - 初始化向导
          </h1>
          <p>欢迎使用！请按照步骤完成初始配置</p>
        </div>
      </template>

      <el-steps :active="activeStep" align-center finish-status="success">
        <el-step title="欢迎" />
        <el-step title="管理员配置" />
        <el-step title="系统配置" />
        <el-step title="完成" />
      </el-steps>

      <div class="setup-content">
        <!-- 步骤1：欢迎页 -->
        <div v-show="activeStep === 0" class="step-content">
          <el-result
            icon="success"
            title="欢迎使用超星学习通多用户管理平台"
            sub-title="基于 Samueli924/chaoxing 原项目的增强版"
          >
            <template #extra>
              <div class="welcome-info">
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>
                    <strong>平台特性</strong>
                  </template>
                  <ul>
                    <li>🌐 多用户注册登录（JWT认证）</li>
                    <li>📊 任务管理（创建/启动/暂停/取消）</li>
                    <li>⚡ 实时进度推送（WebSocket）</li>
                    <li>👥 管理员后台监控</li>
                    <li>🔒 安全可靠的数据加密</li>
                  </ul>
                </el-alert>
                
                <el-alert type="warning" :closable="false" show-icon style="margin-top: 20px">
                  <template #title>
                    <strong>使用须知</strong>
                  </template>
                  <p>本平台仅供学习交流使用，请勿用于商业用途。</p>
                  <p>遵循 GPL-3.0 开源协议。</p>
                </el-alert>

                <div class="project-links" style="margin-top: 20px">
                  <el-tag type="info">
                    原项目: 
                    <el-link href="https://github.com/Samueli924/chaoxing" target="_blank">
                      Samueli924/chaoxing
                    </el-link>
                  </el-tag>
                  <el-tag type="success" style="margin-left: 10px">
                    增强版: 
                    <el-link href="https://github.com/ViVi141/chaoxing" target="_blank">
                      ViVi141/chaoxing
                    </el-link>
                  </el-tag>
                </div>
              </div>
            </template>
          </el-result>
        </div>

        <!-- 步骤2：管理员配置 -->
        <div v-show="activeStep === 1" class="step-content">
          <el-form :model="adminForm" :rules="adminRules" ref="adminFormRef" label-width="120px">
            <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 20px">
              <template #title>
                <strong>配置管理员账号</strong>
              </template>
              <p>这是您第一次使用本平台，请创建管理员账号。</p>
              <p>如果后端已创建默认管理员（admin / Admin@123），可以选择使用默认账号或创建新账号。</p>
            </el-alert>

            <el-radio-group v-model="useDefaultAdmin" style="margin-bottom: 20px">
              <el-radio :label="true">使用默认管理员账号</el-radio>
              <el-radio :label="false">创建新管理员账号</el-radio>
            </el-radio-group>

            <div v-if="useDefaultAdmin">
              <el-form-item label="用户名">
                <el-input v-model="adminForm.username" disabled placeholder="admin" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="adminForm.password" type="password" placeholder="Admin@123" show-password />
              </el-form-item>
              <el-alert type="error" :closable="false" show-icon style="margin-top: 10px">
                <strong>安全提示：</strong>首次登录后请立即修改密码！
              </el-alert>
            </div>

            <div v-else>
              <el-form-item label="用户名" prop="username">
                <el-input v-model="adminForm.username" placeholder="请输入管理员用户名（3-80字符）" />
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="adminForm.password" type="password" placeholder="请输入密码（至少6字符）" show-password />
              </el-form-item>
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input v-model="adminForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="adminForm.email" placeholder="请输入邮箱（可选）" />
              </el-form-item>
            </div>
          </el-form>
        </div>

        <!-- 步骤3：系统配置 -->
        <div v-show="activeStep === 2" class="step-content">
          <el-form :model="systemForm" label-width="160px">
            <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px">
              <template #title>
                <strong>系统基础配置</strong>
              </template>
              <p>这些配置可以在后台随时修改。</p>
            </el-alert>

            <el-divider content-position="left">部署模式</el-divider>
            
            <el-form-item label="部署模式">
              <el-radio-group v-model="systemForm.deployMode">
                <el-radio label="simple">
                  <strong>简单模式</strong>
                  <div class="mode-desc">
                    <el-tag type="success" size="small">推荐</el-tag>
                    <span>使用SQLite数据库 + 文件队列</span>
                    <br/>
                    <span style="font-size: 12px; color: #909399">
                      无需安装PostgreSQL和Redis，适合小规模使用（&lt;50用户）
                    </span>
                  </div>
                </el-radio>
                <el-radio label="standard" style="margin-top: 15px">
                  <strong>标准模式</strong>
                  <div class="mode-desc">
                    <el-tag type="warning" size="small">需要依赖</el-tag>
                    <span>使用PostgreSQL + Redis</span>
                    <br/>
                    <span style="font-size: 12px; color: #909399">
                      需要安装PostgreSQL和Redis，适合生产环境（&gt;50用户）
                    </span>
                  </div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-divider content-position="left">基础配置</el-divider>
            
            <el-form-item label="平台名称">
              <el-input v-model="systemForm.platformName" placeholder="超星学习通管理平台" />
            </el-form-item>

            <el-form-item label="每用户最大任务数">
              <el-input-number v-model="systemForm.maxTasksPerUser" :min="1" :max="10" />
              <span class="form-tip">同时运行的任务数限制</span>
            </el-form-item>

            <el-form-item label="任务超时时间（分钟）">
              <el-input-number v-model="systemForm.taskTimeout" :min="30" :max="480" :step="30" />
              <span class="form-tip">超过此时间任务将被标记为超时</span>
            </el-form-item>

            <el-divider content-position="left">可选配置</el-divider>

            <el-form-item label="启用用户注册">
              <el-switch v-model="systemForm.enableRegister" />
              <span class="form-tip">关闭后仅管理员可创建账号</span>
            </el-form-item>

            <el-form-item label="启用邮件通知">
              <el-switch v-model="systemForm.enableEmailNotification" />
              <span class="form-tip">需要配置SMTP服务器</span>
            </el-form-item>

            <el-form-item label="日志保留天数">
              <el-input-number v-model="systemForm.logRetentionDays" :min="7" :max="90" />
              <span class="form-tip">超过此天数的日志将被自动清理</span>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤4：完成 -->
        <div v-show="activeStep === 3" class="step-content">
          <el-result
            icon="success"
            title="配置完成！"
            sub-title="您已成功完成初始化配置"
          >
            <template #extra>
              <div class="complete-info">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="部署模式">
                    <el-tag :type="systemForm.deployMode === 'simple' ? 'success' : 'warning'">
                      {{ systemForm.deployMode === 'simple' ? '简单模式（SQLite + 文件队列）' : '标准模式（PostgreSQL + Redis）' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="管理员账号">
                    {{ useDefaultAdmin ? 'admin (默认)' : adminForm.username }}
                  </el-descriptions-item>
                  <el-descriptions-item label="平台名称">
                    {{ systemForm.platformName }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最大任务数">
                    {{ systemForm.maxTasksPerUser }}个/用户
                  </el-descriptions-item>
                  <el-descriptions-item label="用户注册">
                    {{ systemForm.enableRegister ? '已启用' : '已禁用' }}
                  </el-descriptions-item>
                </el-descriptions>

                <el-alert type="success" :closable="false" show-icon style="margin-top: 20px">
                  <template #title>
                    <strong>下一步操作</strong>
                  </template>
                  <ol>
                    <li>点击"进入系统"按钮</li>
                    <li>使用管理员账号登录</li>
                    <li v-if="useDefaultAdmin" style="color: red; font-weight: bold">立即修改默认密码！</li>
                    <li>开始创建用户和任务</li>
                  </ol>
                </el-alert>
              </div>
            </template>
          </el-result>
        </div>
      </div>

      <template #footer>
        <div class="setup-footer">
          <el-button v-if="activeStep > 0" @click="prevStep">
            <el-icon><ArrowLeft /></el-icon> 上一步
          </el-button>
          <el-button
            v-if="activeStep < 3"
            type="primary"
            @click="nextStep"
            :loading="loading"
          >
            下一步 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-if="activeStep === 3"
            type="success"
            @click="finishSetup"
            :loading="loading"
          >
            进入系统 <el-icon><Check /></el-icon>
          </el-button>
        </div>
      </template>
    </el-card>

    <div class="footer-info">
      <p>
        基于 
        <el-link href="https://github.com/Samueli924/chaoxing" target="_blank">
          Samueli924/chaoxing
        </el-link>
        原项目开发 | 增强版本: 
        <el-link href="https://github.com/ViVi141/chaoxing" target="_blank">
          ViVi141/chaoxing
        </el-link>
      </p>
      <p>开发者: ViVi141 | GPL-3.0 License</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI, setupAPI } from '@/api'

const router = useRouter()
const activeStep = ref(0)
const loading = ref(false)
const useDefaultAdmin = ref(true)
const adminFormRef = ref(null)

// 管理员表单
const adminForm = reactive({
  username: 'admin',
  password: 'Admin@123',
  confirmPassword: '',
  email: ''
})

// 系统配置表单
const systemForm = reactive({
  deployMode: 'simple',  // 默认简单模式
  platformName: '超星学习通管理平台',
  maxTasksPerUser: 3,
  taskTimeout: 120,
  enableRegister: true,
  enableEmailNotification: false,
  logRetentionDays: 30
})

// 管理员表单验证规则
const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 80, message: '用户名长度应在3-80字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== adminForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 下一步
const nextStep = async () => {
  if (activeStep.value === 1 && !useDefaultAdmin.value) {
    // 验证管理员表单
    if (!adminFormRef.value) return
    
    try {
      await adminFormRef.value.validate()
    } catch (error) {
      ElMessage.error('请正确填写管理员信息')
      return
    }
  }

  if (activeStep.value === 2) {
    // 提交配置
    await submitSetup()
  } else {
    activeStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 提交配置
const submitSetup = async () => {
  loading.value = true
  
  try {
    // 准备配置数据
    const configData = {
      deploy_mode: systemForm.deployMode,
      platform_name: systemForm.platformName,
      max_tasks_per_user: systemForm.maxTasksPerUser,
      task_timeout: systemForm.taskTimeout,
      enable_register: systemForm.enableRegister,
      use_default_admin: useDefaultAdmin.value
    }
    
    // 如果是标准模式，添加数据库配置
    if (systemForm.deployMode === 'standard') {
      configData.database_url = systemForm.databaseUrl
      configData.redis_url = systemForm.redisUrl
    }
    
    // 如果创建新管理员，添加管理员信息
    if (!useDefaultAdmin.value) {
      configData.admin_username = adminForm.username
      configData.admin_password = adminForm.password
      configData.admin_email = adminForm.email || null
    }
    
    // 调用配置API
    const response = await setupAPI.configureSetup(configData)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '配置完成')
      activeStep.value = 3
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '配置失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

// 完成设置
const finishSetup = () => {
  ElMessage.success({
    message: '初始化完成！正在跳转到登录页面...',
    duration: 2000
  })
  
  setTimeout(() => {
    router.push('/login')
  }, 2000)
}
</script>

<style scoped>
.setup-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.setup-card {
  width: 100%;
  max-width: 900px;
  margin: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.card-header p {
  margin: 10px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.setup-content {
  margin: 30px 0;
  min-height: 400px;
}

.step-content {
  padding: 20px;
}

.welcome-info ul {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.welcome-info li {
  padding: 8px 0;
  font-size: 15px;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.setup-footer {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 0;
}

.complete-info {
  max-width: 600px;
  margin: 0 auto;
}

.footer-info {
  text-align: center;
  color: #ffffff;
  margin-top: 20px;
  font-size: 13px;
}

.footer-info p {
  margin: 5px 0;
}

.project-links {
  text-align: center;
}

:deep(.el-link) {
  color: #409EFF;
  font-weight: bold;
}

:deep(.el-alert__title) {
  font-size: 14px;
}

.mode-desc {
  margin-left: 10px;
  padding: 5px 0;
}
</style>

