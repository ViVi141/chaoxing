/**
 * API调用模块
 * 基于原项目: https://github.com/Samueli924/chaoxing
 * 增强开发: ViVi141 (747384120@qq.com)
 */
import request from './request'

// 认证API
export const authAPI = {
  // 用户登录
  login: (username, password) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  // 用户注册
  register: (data) => request.post('/auth/register', data),

  // 获取当前用户信息
  getCurrentUser: () => request.get('/auth/me'),

  // 刷新令牌
  refreshToken: () => request.post('/auth/refresh'),

  // 登出
  logout: () => request.post('/auth/logout')
}

// 用户API
export const userAPI = {
  // 获取用户配置
  getConfig: () => request.get('/user/config'),

  // 更新用户配置
  updateConfig: (data) => request.put('/user/config', data),

  // 修改密码
  changePassword: (oldPassword, newPassword) => 
    request.put('/user/password', null, {
      params: { old_password: oldPassword, new_password: newPassword }
    }),

  // 获取用户详情
  getProfile: () => request.get('/user/profile'),

  // 删除账号
  deleteAccount: (password) => 
    request.delete('/user/account', { params: { password } })
}

// 任务API
export const taskAPI = {
  // 获取任务列表
  getTasks: (params) => request.get('/tasks', { params }),

  // 创建任务
  createTask: (data) => request.post('/tasks', data),

  // 获取任务详情
  getTask: (id) => request.get(`/tasks/${id}`),

  // 更新任务
  updateTask: (id, data) => request.put(`/tasks/${id}`, data),

  // 启动任务
  startTask: (id) => request.post(`/tasks/${id}/start`),

  // 暂停任务
  pauseTask: (id) => request.post(`/tasks/${id}/pause`),

  // 取消任务
  cancelTask: (id) => request.post(`/tasks/${id}/cancel`),

  // 删除任务
  deleteTask: (id) => request.delete(`/tasks/${id}`),

  // 获取任务日志
  getTaskLogs: (id, params) => request.get(`/tasks/${id}/logs`, { params })
}

// 管理员API
export const adminAPI = {
  // 获取所有用户
  getUsers: (params) => request.get('/admin/users', { params }),

  // 获取用户详情
  getUser: (id) => request.get(`/admin/users/${id}`),

  // 更新用户
  updateUser: (id, data) => request.put(`/admin/users/${id}`, data),

  // 删除用户
  deleteUser: (id) => request.delete(`/admin/users/${id}`),

  // 获取所有任务
  getAllTasks: (params) => request.get('/admin/tasks', { params }),

  // 强制停止任务
  forceStopTask: (id) => request.post(`/admin/tasks/${id}/force-stop`),

  // 获取统计数据
  getStatistics: () => request.get('/admin/statistics'),

  // 获取系统日志
  getSystemLogs: (params) => request.get('/admin/logs', { params })
}

// 安装向导API
export const setupAPI = {
  // 检查安装状态
  checkSetup: () => request.get('/setup/check'),

  // 配置系统
  configureSetup: (data) => request.post('/setup/configure', data),

  // 获取当前配置
  getConfig: () => request.get('/setup/config')
}

// WebSocket连接（辅助函数）
export function createWebSocket(token) {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  const ws = new WebSocket(`${wsUrl}/ws/connect?token=${token}`)
  return ws
}

export default {
  authAPI,
  userAPI,
  taskAPI,
  adminAPI,
  setupAPI,
  createWebSocket
}

