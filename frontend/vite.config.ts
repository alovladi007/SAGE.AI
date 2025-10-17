import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
        ws: true,
      }
    }
  },
  build: {
    outDir: 'build',
    sourcemap: true,
  }
})
