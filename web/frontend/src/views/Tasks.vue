<template>
  <el-container class="dashboard-container">
    <el-aside width="200px">
      <div class="logo"><h2>超星管理平台</h2></div>
      <el-menu :default-active="'/tasks'" router>
        <el-menu-item index="/dashboard"><el-icon><House /></el-icon><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/tasks"><el-icon><List /></el-icon><span>任务管理</span></el-menu-item>
        <el-menu-item index="/config"><el-icon><Setting /></el-icon><span>个人配置</span></el-menu-item>
        <el-menu-item index="/admin/dashboard" v-if="userStore.isAdmin"><el-icon><Monitor /></el-icon><span>管理后台</span></el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <h3>任务管理</h3>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 创建任务
          </el-button>
        </div>
      </el-header>

      <el-main>
        <!-- 过滤栏 -->
        <el-card shadow="never" style="margin-bottom: 20px">
          <el-form :inline="true">
            <el-form-item label="状态">
              <el-select v-model="filterStatus" placeholder="全部" clearable @change="loadTasks">
                <el-option label="等待中" value="pending" />
                <el-option label="运行中" value="running" />
                <el-option label="已完成" value="completed" />
                <el-option label="失败" value="failed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button @click="loadTasks">刷新</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 任务列表 -->
        <el-table :data="tasks" v-loading="loading" border>
          <el-table-column prop="name" label="任务名称" min-width="200" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="180">
            <template #default="{ row }">
              <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" />
            </template>
          </el-table-column>
          <el-table-column label="课程" width="120">
            <template #default="{ row }">
              {{ row.completed_courses }}/{{ row.total_courses }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button v-if="row.status === 'pending' || row.status === 'paused'" link type="success" size="small" @click="startTask(row.id)">
                  <el-icon><VideoPlay /></el-icon> 启动
                </el-button>
                <el-button v-if="row.status === 'running'" link type="warning" size="small" @click="pauseTask(row.id)">
                  <el-icon><VideoPause /></el-icon> 暂停
                </el-button>
                <el-button v-if="row.status === 'running' || row.status === 'pending'" link type="danger" size="small" @click="cancelTask(row.id)">
                  <el-icon><Close /></el-icon> 取消
                </el-button>
                <el-button link type="primary" size="small" @click="viewLogs(row.id)">
                  <el-icon><Document /></el-icon> 日志
                </el-button>
                <el-button v-if="row.status === 'completed' || row.status === 'failed' || row.status === 'cancelled'" link type="danger" size="small" @click="deleteTask(row.id)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
          style="margin-top: 20px; justify-content: center"
        />
      </el-main>
    </el-container>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建新任务" width="600px">
      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="课程ID">
          <el-input
            v-model="taskForm.courseIds"
            type="textarea"
            :rows="3"
            placeholder="输入课程ID，多个ID用逗号分隔，留空表示学习所有课程"
          />
          <div class="form-tip">例如: 123456,789012,345678</div>
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon>
          <strong>提示：</strong>请先在"个人配置"中配置您的超星账号，否则任务无法执行。
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="submitLoading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 日志查看对话框 -->
    <el-dialog v-model="showLogsDialog" title="任务日志" width="800px">
      <el-table :data="logs" max-height="400" border>
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="getLogLevelType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" min-width="400" />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showLogsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { taskAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const loading = ref(false)
const submitLoading = ref(false)
const tasks = ref([])
const logs = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const showLogsDialog = ref(false)
const taskFormRef = ref(null)

// 任务表单
const taskForm = reactive({
  name: '',
  courseIds: ''
})

// 验证规则
const taskRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }]
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const response = await taskAPI.getTasks({
      page: currentPage.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined
    })
    if (response.data) {
      tasks.value = response.data.items
      total.value = response.data.total
    }
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 创建任务
const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    submitLoading.value = true
    
    const courseIds = taskForm.courseIds
      .split(',')
      .map(id => id.trim())
      .filter(id => id)
    
    const response = await taskAPI.createTask({
      name: taskForm.name,
      course_ids: courseIds.length > 0 ? courseIds : null
    })
    
    if (response.data) {
      ElMessage.success('任务创建成功')
      showCreateDialog.value = false
      taskForm.name = ''
      taskForm.courseIds = ''
      loadTasks()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

// 启动任务
const startTask = async (id) => {
  try {
    await taskAPI.startTask(id)
    ElMessage.success('任务已启动')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '启动失败')
  }
}

// 暂停任务
const pauseTask = async (id) => {
  try {
    await taskAPI.pauseTask(id)
    ElMessage.success('任务已暂停')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '暂停失败')
  }
}

// 取消任务
const cancelTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消此任务吗？', '确认', {
      type: 'warning'
    })
    await taskAPI.cancelTask(id)
    ElMessage.success('任务已取消')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}

// 删除任务
const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？此操作不可撤销。', '确认', {
      type: 'warning'
    })
    await taskAPI.deleteTask(id)
    ElMessage.success('任务已删除')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 查看日志
const viewLogs = async (id) => {
  try {
    const response = await taskAPI.getTaskLogs(id, { limit: 100 })
    if (response.data) {
      logs.value = response.data
      showLogsDialog.value = true
    }
  } catch (error) {
    ElMessage.error('加载日志失败')
  }
}

// 辅助函数
const getStatusType = (status) => {
  const typeMap = {
    pending: 'info', running: 'warning', completed: 'success',
    failed: 'danger', cancelled: 'info', paused: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待中', running: '运行中', completed: '已完成',
    failed: '失败', cancelled: '已取消', paused: '已暂停'
  }
  return textMap[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

const getLogLevelType = (level) => {
  const typeMap = { INFO: 'info', WARNING: 'warning', ERROR: 'danger' }
  return typeMap[level] || 'info'
}

const formatDate = (dateStr) => dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')

onMounted(() => loadTasks())
</script>

<style scoped>
.dashboard-container { height: 100vh; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #545c64; color: #ffffff; }
.logo h2 { margin: 0; font-size: 16px; }
.el-header { background-color: #ffffff; box-shadow: 0 1px 4px rgba(0,21,41,.08); padding: 0 20px; }
.header-content { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.el-main { background-color: #f0f2f5; padding: 20px; }
.form-tip { margin-top: 5px; color: #909399; font-size: 12px; }
</style>

