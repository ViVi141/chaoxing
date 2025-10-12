<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统日志</span>
          <el-select v-model="filterLevel" placeholder="日志级别" clearable style="width: 120px" @change="loadLogs">
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </div>
      </template>

      <el-table :data="logs" v-loading="loading" border max-height="600">
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="150" />
        <el-table-column prop="message" label="消息" min-width="400" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="130" />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="loadLogs"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const logs = ref([])
const filterLevel = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

const loadLogs = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getSystemLogs({
      page: currentPage.value,
      page_size: pageSize.value,
      level: filterLevel.value || undefined
    })
    logs.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const getLevelType = (level) => {
  const map = { INFO: 'info', WARNING: 'warning', ERROR: 'danger' }
  return map[level] || 'info'
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

onMounted(() => loadLogs())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>

