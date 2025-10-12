/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const user = ref(null)
  const config = ref(null)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userName = computed(() => user.value?.username || '')

  // Actions
  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUser(newUser) {
    user.value = newUser
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('user')
    }
  }

  function setConfig(newConfig) {
    config.value = newConfig
  }

  async function loadUserInfo() {
    try {
      const response = await authAPI.getCurrentUser()
      if (response.data) {
        setUser(response.data)
        return response.data
      }
    } catch (error) {
      console.error('加载用户信息失败:', error)
      return null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    config.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 初始化（从localStorage恢复）
  function init() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken) {
      token.value = savedToken
    }
    
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('解析用户信息失败', e)
      }
    }
  }

  return {
    token,
    user,
    config,
    isLoggedIn,
    isAdmin,
    userName,
    setToken,
    setUser,
    setConfig,
    loadUserInfo,
    logout,
    init
  }
})

