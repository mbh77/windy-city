import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // 빌드 결과물을 ../static 에 출력 (FastAPI가 서빙)
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    // 개발 중 API 프록시 (FastAPI 8000 포트)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
