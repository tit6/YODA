import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  //for link back and fronted
  //Front  →  Vite proxy  →  http://172.18.0.1:5000/  →  Flask (gpt demonstration)
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://172.18.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
    }
  }
})
