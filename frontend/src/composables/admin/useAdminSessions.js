import { ref } from 'vue'
import { cleanupAdminSessions, deleteAdminSession, getAdminSessions } from '@/api.js'

export function useAdminSessions() {
  const sessions = ref([])
  const loading = ref(false)
  const error = ref('')
  const acting = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = ref(12)

  async function loadSessions() {
    loading.value = true
    error.value = ''
    try {
      const data = await getAdminSessions({
        page: page.value,
        size: size.value,
      })
      sessions.value = data.sessions || []
      total.value = data.total || 0
    } catch (err) {
      error.value = err.message || '会话列表加载失败'
    } finally {
      loading.value = false
    }
  }

  async function removeSession(sessionId) {
    acting.value = true
    error.value = ''
    try {
      await deleteAdminSession(sessionId)
      await loadSessions()
    } finally {
      acting.value = false
    }
  }

  async function cleanupSessions() {
    acting.value = true
    error.value = ''
    try {
      const result = await cleanupAdminSessions()
      await loadSessions()
      return result
    } finally {
      acting.value = false
    }
  }

  return {
    sessions,
    loading,
    error,
    acting,
    total,
    page,
    size,
    loadSessions,
    removeSession,
    cleanupSessions,
  }
}
