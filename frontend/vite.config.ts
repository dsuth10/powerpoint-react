import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    // Temporarily disable proxy to force direct API calls
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //   },
    //   // Proxy Socket.IO/WebSocket traffic to backend
    //   '/ws': {
    //     target: 'http://localhost:8000',
    //     ws: true,
    //     changeOrigin: true,
    //   },
    // },
  },
})
