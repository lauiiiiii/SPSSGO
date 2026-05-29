import { reactive, ref } from 'vue'
import {
  createAdminUser,
  getAdminUsers,
  resetAdminUserPassword,
  toggleAdminUserActive,
  updateAdminUser,
} from '@/api.js'

export function useAdminUsers() {
  const users = ref([])
  const loading = ref(false)
  const error = ref('')
  const saving = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = ref(12)
  const filters = reactive({
    keyword: '',
    role: '',
    is_active: '',
  })

  async function loadUsers() {
    loading.value = true
    error.value = ''
    try {
      const data = await getAdminUsers({
        page: page.value,
        size: size.value,
        keyword: filters.keyword,
        role: filters.role,
        is_active: filters.is_active,
      })
      users.value = data.users || []
      total.value = data.total || 0
    } catch (err) {
      error.value = err.message || '账户列表加载失败'
    } finally {
      loading.value = false
    }
  }

  async function createUser(payload) {
    saving.value = true
    error.value = ''
    try {
      await createAdminUser(payload)
      await loadUsers()
    } finally {
      saving.value = false
    }
  }

  async function updateUser(userId, payload) {
    saving.value = true
    error.value = ''
    try {
      await updateAdminUser(userId, payload)
      await loadUsers()
    } finally {
      saving.value = false
    }
  }

  async function resetPassword(userId, newPassword) {
    saving.value = true
    error.value = ''
    try {
      await resetAdminUserPassword(userId, newPassword)
    } finally {
      saving.value = false
    }
  }

  async function toggleUserActive(userId, isActive) {
    saving.value = true
    error.value = ''
    try {
      await toggleAdminUserActive(userId, isActive)
      await loadUsers()
    } finally {
      saving.value = false
    }
  }

  return {
    users,
    loading,
    error,
    saving,
    total,
    page,
    size,
    filters,
    loadUsers,
    createUser,
    updateUser,
    resetPassword,
    toggleUserActive,
  }
}
