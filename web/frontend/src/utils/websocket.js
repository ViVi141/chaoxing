/**
 * WebSocket工具
 * 用于实时接收任务进度和系统通知
 */
import { ElNotification } from 'element-plus'

class WebSocketClient {
  constructor() {
    this.ws = null
    this.reconnectTimer = null
    this.heartbeatTimer = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.messageHandlers = new Map()
  }

  /**
   * 连接WebSocket
   */
  connect(token) {
    if (this.ws) {
      this.ws.close()
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const url = `${wsUrl}/ws/connect?token=${token}`

    try {
      this.ws = new WebSocket(url)
      this.setupEventHandlers()
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.scheduleReconnect(token)
    }
  }

  /**
   * 设置事件处理器
   */
  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('WebSocket已连接')
      this.reconnectAttempts = 0
      this.startHeartbeat()
      
      ElNotification({
        title: '实时连接已建立',
        message: '将实时接收任务进度更新',
        type: 'success',
        duration: 2000
      })
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket连接已关闭')
      this.stopHeartbeat()
      
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.scheduleReconnect()
      }
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(message) {
    const { type, data } = message

    console.log('收到消息:', message)

    switch (type) {
      case 'connected':
        console.log('WebSocket连接确认:', message)
        break

      case 'task_update':
        // 任务更新
        this.triggerHandler('task_update', data)
        
        // 显示通知
        if (data.status === 'completed') {
          ElNotification({
            title: '任务完成',
            message: `任务进度: ${data.progress}%`,
            type: 'success'
          })
        }
        break

      case 'notification':
        // 系统通知
        ElNotification({
          title: '系统通知',
          message: data.message,
          type: data.level || 'info'
        })
        break

      case 'pong':
        // 心跳响应
        break

      case 'error':
        console.error('WebSocket错误消息:', message)
        break

      default:
        console.warn('未知消息类型:', type)
    }

    // 触发自定义处理器
    this.triggerHandler(type, data)
  }

  /**
   * 订阅任务更新
   */
  subscribeTask(taskId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe_task',
        task_id: taskId
      }))
    }
  }

  /**
   * 取消订阅任务
   */
  unsubscribeTask(taskId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe_task',
        task_id: taskId
      }))
    }
  }

  /**
   * 注册消息处理器
   */
  on(type, handler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type).push(handler)
  }

  /**
   * 移除消息处理器
   */
  off(type, handler) {
    if (this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * 触发处理器
   */
  triggerHandler(type, data) {
    if (this.messageHandlers.has(type)) {
      this.messageHandlers.get(type).forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error('处理器执行错误:', error)
        }
      })
    }
  }

  /**
   * 开始心跳
   */
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 30秒心跳
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 计划重连
   */
  scheduleReconnect(token) {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)

    console.log(`将在${delay}ms后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    this.reconnectTimer = setTimeout(() => {
      this.connect(token)
    }, delay)
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopHeartbeat()
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.messageHandlers.clear()
  }

  /**
   * 获取连接状态
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 创建全局实例
const wsClient = new WebSocketClient()

export default wsClient

