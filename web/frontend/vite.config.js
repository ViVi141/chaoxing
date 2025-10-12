import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: 'localhost',  // 只监听localhost，避免Chrome安全警告
    // 如需局域网访问，使用 '0.0.0.0' 并通过localhost访问
  }
})

