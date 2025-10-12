<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-input v-model="searchText" placeholder="搜索用户名或邮箱" style="width: 200px" clearable @input="loadUsers" />
        </div>
      </template>

      <el-table :data="users" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160">
          <template #default="{ row }">{{ row.last_login ? formatDate(row.last_login) : '从未登录' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button link type="primary" @click="viewUser(row)">查看</el-button>
              <el-button link :type="row.is_active ? 'warning' : 'success'" @click="toggleUserStatus(row)">
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
              <el-button link type="danger" @click="deleteUser(row)" :disabled="row.id === userStore.user.id">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @change="loadUsers"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const loading = ref(false)
const users = ref([])
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getUsers({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value || undefined
    })
    users.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const viewUser = (user) => {
  ElMessageBox.alert(`
    <p><strong>ID:</strong> ${user.id}</p>
    <p><strong>用户名:</strong> ${user.username}</p>
    <p><strong>邮箱:</strong> ${user.email || '未设置'}</p>
    <p><strong>角色:</strong> ${user.role}</p>
    <p><strong>状态:</strong> ${user.is_active ? '正常' : '禁用'}</p>
    <p><strong>注册时间:</strong> ${formatDate(user.created_at)}</p>
  `, '用户详情', { dangerouslyUseHTMLString: true })
}

const toggleUserStatus = async (user) => {
  try {
    await adminAPI.updateUser(user.id, { is_active: !user.is_active })
    ElMessage.success(`已${user.is_active ? '禁用' : '启用'}用户`)
    loadUsers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${user.username}"吗？此操作不可撤销。`, '警告', { type: 'warning' })
    await adminAPI.deleteUser(user.id)
    ElMessage.success('用户已删除')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

onMounted(() => loadUsers())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>

