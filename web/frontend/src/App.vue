<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

onMounted(() => {
  // 检查是否完成初始设置
  const setupCompleted = localStorage.getItem('setup_completed')
  
  if (!setupCompleted && router.currentRoute.value.path !== '/setup') {
    router.push('/setup')
  }
  
  // 尝试从localStorage恢复用户信息
  const token = localStorage.getItem('token')
  if (token) {
    userStore.setToken(token)
  }
})
</script>

<style>
#app {
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}
</style>

