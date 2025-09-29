import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/pull': 'http://localhost:8000',
      '/preview': 'http://localhost:8000',
      '/healthz': 'http://localhost:8000'
    }
  }
})

