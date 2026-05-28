import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

function manualChunks(id) {
  if (!id.includes('node_modules')) return undefined
  if (id.includes('ag-grid-community') || id.includes('ag-grid-vue3')) return 'vendor-ag-grid'
  if (id.includes('katex')) return 'vendor-katex'
  if (id.includes('xlsx')) return 'vendor-xlsx'
  if (id.includes('vue-router')) return 'vendor-router'
  if (id.includes('/vue/')) return 'vendor-vue'
  return 'vendor'
}

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks,
      },
    },
  },
  server: {
    port: 5577,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
