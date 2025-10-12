<template>
  <el-container class="dashboard-container">
    <el-aside width="200px">
      <div class="logo"><h2>超星管理平台</h2></div>
      <el-menu :default-active="'/config'" router>
        <el-menu-item index="/dashboard"><el-icon><House /></el-icon><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/tasks"><el-icon><List /></el-icon><span>任务管理</span></el-menu-item>
        <el-menu-item index="/config"><el-icon><Setting /></el-icon><span>个人配置</span></el-menu-item>
        <el-menu-item index="/admin/dashboard" v-if="userStore.isAdmin"><el-icon><Monitor /></el-icon><span>管理后台</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content"><h3>个人配置</h3></div>
      </el-header>

      <el-main>
        <el-tabs v-model="activeTab">
          <!-- 超星账号配置 -->
          <el-tab-pane label="超星账号" name="account">
            <el-form :model="configForm" label-width="140px" style="max-width: 600px">
              <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px">
                <strong>配置您的超星学习通账号，用于自动登录和学习</strong>
              </el-alert>
              
              <el-form-item label="手机号">
                <el-input v-model="configForm.cx_username" placeholder="11位手机号" maxlength="11" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="configForm.cx_password" type="password" placeholder="超星账号密码" show-password />
                <div class="form-tip">密码将加密存储，请放心填写</div>
              </el-form-item>
              <el-form-item label="使用Cookie登录">
                <el-switch v-model="configForm.use_cookies" />
                <div class="form-tip">如果开启，将使用Cookie方式登录</div>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 学习配置 -->
          <el-tab-pane label="学习配置" name="study">
            <el-form :model="configForm" label-width="160px" style="max-width: 600px">
              <el-form-item label="播放倍速">
                <el-slider v-model="configForm.speed" :min="1.0" :max="2.0" :step="0.1" show-input />
                <div class="form-tip">视频播放倍速（1.0-2.0倍）</div>
              </el-form-item>
              <el-form-item label="未开放章节处理">
                <el-radio-group v-model="configForm.notopen_action">
                  <el-radio label="retry">重试上一章节</el-radio>
                  <el-radio label="ask">询问是否继续</el-radio>
                  <el-radio label="continue">自动跳过</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 题库配置 -->
          <el-tab-pane label="题库配置" name="tiku">
            <el-form :model="tikuConfig" label-width="140px" style="max-width: 600px">
              <el-form-item label="题库提供商">
                <el-select v-model="tikuConfig.provider" placeholder="选择题库" clearable>
                  <el-option label="言溪题库" value="TikuYanxi" />
                  <el-option label="LIKE知识库" value="TikuLike" />
                  <el-option label="TikuAdapter" value="TikuAdapter" />
                  <el-option label="AI大模型" value="AI" />
                  <el-option label="硅基流动" value="SiliconFlow" />
                </el-select>
              </el-form-item>
              
              <template v-if="tikuConfig.provider">
                <el-form-item label="Token/密钥">
                  <el-input v-model="tikuConfig.tokens" type="textarea" :rows="2" placeholder="输入题库Token" />
                </el-form-item>
                <el-form-item label="自动提交">
                  <el-switch v-model="tikuConfig.submit" />
                  <div class="form-tip">开启后将自动提交答案（正确率不保证）</div>
                </el-form-item>
                <el-form-item label="题库覆盖率">
                  <el-slider v-model="tikuConfig.cover_rate" :min="0" :max="1" :step="0.1" show-input />
                  <div class="form-tip">搜到的题目占比达到此值才提交</div>
                </el-form-item>
                <el-form-item label="查询延迟(秒)">
                  <el-input-number v-model="tikuConfig.delay" :min="0" :max="10" :step="0.5" />
                </el-form-item>
              </template>
            </el-form>
          </el-tab-pane>

          <!-- 通知配置 -->
          <el-tab-pane label="通知配置" name="notification">
            <el-form :model="notificationConfig" label-width="140px" style="max-width: 600px">
              <el-form-item label="通知提供商">
                <el-select v-model="notificationConfig.provider" placeholder="选择通知方式" clearable>
                  <el-option label="Server酱" value="ServerChan" />
                  <el-option label="Qmsg酱" value="Qmsg" />
                  <el-option label="Bark" value="Bark" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="通知URL" v-if="notificationConfig.provider">
                <el-input v-model="notificationConfig.url" placeholder="输入通知服务URL" />
                <div class="form-tip">
                  示例：<br/>
                  Server酱: https://sctapi.ftqq.com/你的Key.send<br/>
                  Qmsg: https://qmsg.zendee.cn/send/你的Key<br/>
                  Bark: https://api.day.app/你的Key/
                </div>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <!-- 保存按钮 -->
        <div style="text-align: center; margin-top: 30px">
          <el-button type="primary" size="large" @click="saveConfig" :loading="saveLoading">
            <el-icon><Check /></el-icon> 保存配置
          </el-button>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { userAPI } from '@/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const activeTab = ref('account')
const saveLoading = ref(false)

const configForm = reactive({
  cx_username: '',
  cx_password: '',
  use_cookies: false,
  speed: 1.0,
  notopen_action: 'retry'
})

const tikuConfig = reactive({
  provider: '',
  tokens: '',
  submit: false,
  cover_rate: 0.9,
  delay: 1.0
})

const notificationConfig = reactive({
  provider: '',
  url: ''
})

// 加载配置
const loadConfig = async () => {
  try {
    const response = await userAPI.getConfig()
    if (response.data) {
      const config = response.data
      configForm.cx_username = config.cx_username || ''
      configForm.use_cookies = config.use_cookies
      configForm.speed = config.speed
      configForm.notopen_action = config.notopen_action
      
      if (config.tiku_config) {
        Object.assign(tikuConfig, config.tiku_config)
      }
      if (config.notification_config) {
        Object.assign(notificationConfig, config.notification_config)
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 保存配置
const saveConfig = async () => {
  saveLoading.value = true
  try {
    await userAPI.updateConfig({
      cx_username: configForm.cx_username,
      cx_password: configForm.cx_password || undefined,
      use_cookies: configForm.use_cookies,
      speed: configForm.speed,
      notopen_action: configForm.notopen_action,
      tiku_config: tikuConfig.provider ? tikuConfig : null,
      notification_config: notificationConfig.provider ? notificationConfig : null
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saveLoading.value = false
  }
}

onMounted(() => loadConfig())
</script>

<style scoped>
.dashboard-container { height: 100vh; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #545c64; color: #ffffff; }
.logo h2 { margin: 0; font-size: 16px; }
.el-header { background-color: #ffffff; box-shadow: 0 1px 4px rgba(0,21,41,.08); padding: 0 20px; }
.header-content { display: flex; align-items: center; }
.el-main { background-color: #f0f2f5; padding: 20px; }
.form-tip { margin-top: 5px; color: #909399; font-size: 12px; line-height: 1.5; }
</style>

