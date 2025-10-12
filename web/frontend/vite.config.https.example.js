import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

// HTTPS配置示例（需要SSL证书）
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: 'localhost',
    https: {
      // 开发环境可以使用mkcert生成本地证书
      // 1. 安装mkcert: choco install mkcert (Windows)
      // 2. 生成证书: mkcert -install && mkcert localhost
      // 3. 证书会生成在当前目录
      key: fs.readFileSync('./localhost-key.pem'),
      cert: fs.readFileSync('./localhost.pem'),
    }
  }
})

