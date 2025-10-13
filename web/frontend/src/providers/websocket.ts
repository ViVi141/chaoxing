/**
 * WebSocket Provider for Real-time Updates
 * 实时进度更新的WebSocket连接管理
 */
import { useEffect } from 'react';

type MessageHandler = (data: any) => void;

class WebSocketManager {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  constructor(private url: string) {}

  connect(token: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WS] Already connected');
      return;
    }

    try {
      this.ws = new WebSocket(`${this.url}?token=${token}`);
      
      this.ws.onopen = () => {
        console.log('[WS] Connected successfully');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('[WS] Message received:', message);
          
          const { type, data } = message;
          const handlers = this.handlers.get(type);
          
          if (handlers) {
            handlers.forEach(handler => handler(data));
          }
        } catch (error) {
          console.error('[WS] Message parse error:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };

      this.ws.onclose = () => {
        console.log('[WS] Connection closed');
        this.attemptReconnect(token);
      };
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.attemptReconnect(token);
    }
  }

  private attemptReconnect(token: string) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WS] Max reconnect attempts reached');
      return;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    console.log(`[WS] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect(token);
    }, this.reconnectDelay);
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  send(type: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    } else {
      console.warn('[WS] Cannot send, connection not open');
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.handlers.clear();
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// 创建全局WebSocket实例
// ✅ 从环境变量读取API URL并转换为WebSocket URL
const API_URL: string = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';
const wsUrl =
  API_URL.replace(/^http:\/\//, 'ws://')
         .replace(/^https:\/\//, 'wss://')
         .replace(/\/api\/?$/, '/ws/connect');

export const websocketManager = new WebSocketManager(wsUrl);

// React Hook for WebSocket
export function useWebSocket(eventType: string, handler: MessageHandler) {
  useEffect(() => {
    const token = localStorage.getItem('token');
    
    if (token && !websocketManager.isConnected()) {
      websocketManager.connect(token);
    }

    websocketManager.on(eventType, handler);

    return () => {
      websocketManager.off(eventType, handler);
    };
  }, [eventType]); // 注意：handler不在依赖中，避免重复注册
}

