import { ref } from 'vue'
import { getAdminDashboard } from '@/api.js'

export function useAdminDashboard() {
  const dashboard = ref({})
  const loading = ref(false)
  const error = ref('')

  async function loadDashboard() {
    loading.value = true
    error.value = ''
    try {
      dashboard.value = await getAdminDashboard()
    } catch (err) {
      error.value = err.message || '概览加载失败'
    } finally {
      loading.value = false
    }
  }

  return {
    dashboard,
    loading,
    error,
    loadDashboard,
  }
}
