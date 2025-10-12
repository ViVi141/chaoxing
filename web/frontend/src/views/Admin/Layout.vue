<template>
  <el-container class="admin-container">
    <el-aside width="220px">
      <div class="logo">
        <h2>管理员后台</h2>
      </div>
      <el-menu :default-active="activeMenu" router>
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/tasks">
          <el-icon><List /></el-icon>
          <span>任务监控</span>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
        <el-divider />
        <el-menu-item index="/dashboard">
          <el-icon><Back /></el-icon>
          <span>返回用户端</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <span>管理员: {{ userStore.userName }}</span>
          <el-button type="danger" size="small" @click="logout">
            <el-icon><SwitchButton /></el-icon> 退出
          </el-button>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => router.currentRoute.value.path)

const logout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.admin-container { height: 100vh; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #F56C6C; color: #ffffff; }
.logo h2 { margin: 0; font-size: 16px; }
.el-header { background-color: #ffffff; box-shadow: 0 1px 4px rgba(0,21,41,.08); padding: 0 20px; }
.header-content { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.el-main { background-color: #f0f2f5; padding: 20px; }
</style>

