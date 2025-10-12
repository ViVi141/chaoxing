<template>
  <el-container class="dashboard-container">
    <!-- 侧边栏 -->
    <el-aside width="200px">
      <div class="logo">
        <h2>超星管理平台</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/config">
          <el-icon><Setting /></el-icon>
          <span>个人配置</span>
        </el-menu-item>
        <el-menu-item index="/admin/dashboard" v-if="userStore.isAdmin">
          <el-icon><Monitor /></el-icon>
          <span>管理后台</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 头部 -->
      <el-header>
        <div class="header-content">
          <span>欢迎回来，{{ userStore.userName }}</span>
          <div class="header-right">
            <el-tag :type="userStore.isAdmin ? 'danger' : 'success'">
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
            <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link">
                <el-avatar :size="32" icon="User" />
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon> 个人信息
                  </el-dropdown-item>
                  <el-dropdown-item command="config">
                    <el-icon><Setting /></el-icon> 配置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main>
        <!-- 统计卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="总任务数" :value="statistics.total">
                <template #prefix>
                  <el-icon><Tickets /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="运行中" :value="statistics.running">
                <template #prefix>
                  <el-icon color="#67C23A"><VideoPlay /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="已完成" :value="statistics.completed">
                <template #prefix>
                  <el-icon color="#409EFF"><CircleCheck /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="失败" :value="statistics.failed">
                <template #prefix>
                  <el-icon color="#F56C6C"><CircleClose /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <!-- 最近任务 -->
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近任务</span>
              <el-button type="primary" size="small" @click="$router.push('/tasks')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <el-table :data="recentTasks" v-loading="loading">
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewTask(row.id)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { taskAPI } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => router.currentRoute.value.path)
const loading = ref(false)
const statistics = ref({
  total: 0,
  running: 0,
  completed: 0,
  failed: 0
})
const recentTasks = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 加载用户信息
    await userStore.loadUserInfo()
    
    // 加载任务列表
    const response = await taskAPI.getTasks({ page: 1, page_size: 5 })
    if (response.data) {
      recentTasks.value = response.data.items
      
      // 计算统计数据
      const allTasksResponse = await taskAPI.getTasks({ page: 1, page_size: 1000 })
      if (allTasksResponse.data) {
        const tasks = allTasksResponse.data.items
        statistics.value = {
          total: tasks.length,
          running: tasks.filter(t => t.status === 'running').length,
          completed: tasks.filter(t => t.status === 'completed').length,
          failed: tasks.filter(t => t.status === 'failed').length
        }
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 状态类型
const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
    paused: 'warning'
  }
  return typeMap[status] || 'info'
}

// 状态文本
const getStatusText = (status) => {
  const textMap = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
    paused: '已暂停'
  }
  return textMap[status] || status
}

// 进度状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

// 格式化日期
const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

// 查看任务
const viewTask = (id) => {
  router.push(`/tasks?id=${id}`)
}

// 下拉菜单处理
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/config')
      break
    case 'config':
      router.push('/config')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
      break
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #545c64;
  color: #ffffff;
}

.logo h2 {
  margin: 0;
  font-size: 16px;
}

.el-menu-vertical {
  border-right: none;
  height: calc(100vh - 60px);
}

.el-header {
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

