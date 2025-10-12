<template>
  <div>
    <el-card>
      <template #header><span>全局任务监控</span></template>

      <el-table :data="tasks" v-loading="loading" border>
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="username" label="所属用户" width="120" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : undefined" />
          </template>
        </el-table-column>
        <el-table-column label="课程" width="100">
          <template #default="{ row }">{{ row.completed_courses }}/{{ row.total_courses }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'running' || row.status === 'pending'" link type="danger" size="small" @click="forceStop(row.id)">
              <el-icon><Close /></el-icon> 强制停止
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @change="loadTasks"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const tasks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getAllTasks({ page: currentPage.value, page_size: pageSize.value })
    tasks.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

const forceStop = async (id) => {
  try {
    await ElMessageBox.confirm('确定要强制停止此任务吗？', '警告', { type: 'warning' })
    await adminAPI.forceStopTask(id)
    ElMessage.success('任务已强制停止')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const getStatusType = (status) => {
  const map = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger', cancelled: 'info', paused: 'warning' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '等待', running: '运行', completed: '完成', failed: '失败', cancelled: '取消', paused: '暂停' }
  return map[status] || status
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

onMounted(() => loadTasks())
</script>

