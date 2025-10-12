/**
 * Vue Router配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { setupAPI } from '@/api'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/views/Setup.vue'),
    meta: { requiresAuth: false, hideForAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, hideForAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/Config.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin/Layout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/Admin/Dashboard.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/Admin/Users.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'tasks',
        name: 'AdminTasks',
        component: () => import('@/views/Admin/Tasks.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'logs',
        name: 'AdminLogs',
        component: () => import('@/views/Admin/Logs.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否完成初始设置（对于非setup页面）
  if (to.path !== '/setup') {
    try {
      const response = await setupAPI.checkSetup()
      if (!response.data.is_setup) {
        return next('/setup')
      }
    } catch (error) {
      // 如果检查失败（可能是网络问题），继续导航
      console.warn('检查安装状态失败:', error)
    }
  }
  
  // 如果已登录且访问登录/注册页，跳转到首页
  if (userStore.isLoggedIn && to.meta.hideForAuth) {
    return next('/dashboard')
  }
  
  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return next('/login')
  }
  
  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    return next('/dashboard')
  }
  
  next()
})

export default router

