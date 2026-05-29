<!-- 管理后台页面：优先做账号和系统控制台，别把工作台交互塞进来。 -->
<template>
  <div v-if="ready" class="admin-shell">
    <AdminHeader :username="username" @logout="handleLogout" />
    <div class="admin-shell__body">
      <AdminSidebar :items="navItems" :active-tab="activeTab" @change="changeTab" />
      <main class="admin-shell__content">
        <div v-if="globalMessage.text" :class="['admin-banner', globalMessage.type ? `is-${globalMessage.type}` : '']">
          {{ globalMessage.text }}
        </div>

        <AdminUsersPanel
          v-if="activeTab === 'users'"
          :users="usersApi.users.value"
          :filters="usersApi.filters"
          :loading="usersApi.loading.value"
          :error="usersApi.error.value"
          :total="usersApi.total.value"
          :page="usersApi.page.value"
          :size="usersApi.size.value"
          @create="openCreateUser"
          @edit="openEditUser"
          @reset-password="openResetPassword"
          @toggle-active="openToggleUser"
          @refresh="usersApi.loadUsers"
          @change-page="handleUsersPageChange"
          @update:filters="handleUserFiltersChange"
        />

        <AdminAiConfigPanel
          v-else-if="activeTab === 'ai'"
          :config="aiPanelConfig"
          :loading="aiApi.aiLoading.value"
          :saving="aiApi.aiSaving.value"
          :error="aiApi.aiError.value"
          :success="aiApi.aiSuccess.value"
          @save="handleSaveAiConfig"
          @update:config="handleAiConfigUpdate"
          @apply-provider-preset="aiApi.applyProviderPreset"
        />

        <AdminSystemPanel
          v-else-if="activeTab === 'system'"
          :system-info="aiApi.systemInfo.value"
          :loading="aiApi.systemLoading.value"
          :error="aiApi.systemError.value"
          @refresh="aiApi.loadSystemInfo"
        />

        <AdminJobsPanel
          v-else-if="activeTab === 'operations'"
          :operations-summary="operationsApi.operationsSummary.value"
          :queue-chips="operationsApi.queueChips.value"
          :sandbox-mode-chips="operationsApi.sandboxModeChips.value"
          :job-filters="operationsApi.jobFilters"
          :jobs="operationsApi.jobs.value"
          :jobs-loading="operationsApi.jobsLoading.value"
          :jobs-error="operationsApi.jobsError.value"
          :job-page="operationsApi.jobPage.value"
          :job-size="operationsApi.jobSize.value"
          :job-total="operationsApi.jobTotal.value"
          :sandbox-filters="operationsApi.sandboxFilters"
          :sandbox-executions="operationsApi.sandboxExecutions.value"
          :sandbox-loading="operationsApi.sandboxLoading.value"
          :sandbox-error="operationsApi.sandboxError.value"
          :sandbox-page="operationsApi.sandboxPage.value"
          :sandbox-size="operationsApi.sandboxSize.value"
          :sandbox-total="operationsApi.sandboxTotal.value"
          @refresh="operationsApi.loadOperationsData"
          @update:job-filters="handleJobFiltersChange"
          @update:sandbox-filters="handleSandboxFiltersChange"
          @change-job-page="handleJobPageChange"
          @change-sandbox-page="handleSandboxPageChange"
        />

        <AdminSessionsPanel
          v-else-if="activeTab === 'sessions'"
          :sessions="sessionsApi.sessions.value"
          :loading="sessionsApi.loading.value"
          :error="sessionsApi.error.value"
          :total="sessionsApi.total.value"
          :page="sessionsApi.page.value"
          :size="sessionsApi.size.value"
          @refresh="sessionsApi.loadSessions"
          @cleanup="openCleanupSessions"
          @delete="openDeleteSession"
          @change-page="handleSessionPageChange"
        />

        <AdminOverviewPanel
          v-else
          :dashboard="dashboardApi.dashboard.value"
          :loading="dashboardApi.loading.value"
          :error="dashboardApi.error.value"
          @refresh="dashboardApi.loadDashboard"
        />
      </main>
    </div>

    <AdminUserDialog
      v-if="userDialog.visible"
      v-model="userDialog.form"
      :mode="userDialog.mode"
      @close="closeUserDialog"
      @submit="submitUserDialog"
    />

    <AdminPasswordDialog
      v-if="passwordDialog.visible"
      v-model="passwordDialog.password"
      @close="closePasswordDialog"
      @submit="submitPasswordDialog"
    />

    <AdminConfirmDialog
      v-if="confirmDialog.visible"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :confirm-text="confirmDialog.confirmText"
      :danger="confirmDialog.danger"
      @cancel="closeConfirmDialog"
      @confirm="submitConfirmDialog"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { getCurrentUser, logout } from '@/api.js'
import AdminAiConfigPanel from '@/components/admin/AdminAiConfigPanel.vue'
import AdminConfirmDialog from '@/components/admin/AdminConfirmDialog.vue'
import AdminHeader from '@/components/admin/AdminHeader.vue'
import AdminJobsPanel from '@/components/admin/AdminJobsPanel.vue'
import AdminOverviewPanel from '@/components/admin/AdminOverviewPanel.vue'
import AdminPasswordDialog from '@/components/admin/AdminPasswordDialog.vue'
import AdminSessionsPanel from '@/components/admin/AdminSessionsPanel.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminSystemPanel from '@/components/admin/AdminSystemPanel.vue'
import AdminUserDialog from '@/components/admin/AdminUserDialog.vue'
import AdminUsersPanel from '@/components/admin/AdminUsersPanel.vue'
import { useAdminAiConfig } from '@/composables/admin/useAdminAiConfig.js'
import { useAdminDashboard } from '@/composables/admin/useAdminDashboard.js'
import { useAdminOperations } from '@/composables/admin/useAdminOperations.js'
import { useAdminSessions } from '@/composables/admin/useAdminSessions.js'
import { useAdminUsers } from '@/composables/admin/useAdminUsers.js'

const ready = ref(false)
const username = ref('')
const activeTab = ref('users')

const dashboardApi = useAdminDashboard()
const usersApi = useAdminUsers()
const aiApi = useAdminAiConfig()
const operationsApi = useAdminOperations()
const sessionsApi = useAdminSessions()

const globalMessage = reactive({
  text: '',
  type: '',
})

const userDialog = reactive({
  visible: false,
  mode: 'create',
  targetUser: null,
  form: {
    username: '',
    password: '',
    role: 'user',
  },
})

const passwordDialog = reactive({
  visible: false,
  targetUser: null,
  password: '',
})

const confirmDialog = reactive({
  visible: false,
  title: '',
  message: '',
  confirmText: '确认',
  danger: false,
  action: null,
})

const navItems = [
  { key: 'users', label: '账户管理', icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M8 8a2.75 2.75 0 1 0 0-5.5A2.75 2.75 0 0 0 8 8Z" stroke="currentColor" stroke-width="1.4"/><path d="M2.5 13.5c.6-2.4 2.7-3.5 5.5-3.5s4.9 1.1 5.5 3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' },
  { key: 'ai', label: 'AI 配置', icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.2 3.2l1.4 1.4M11.4 11.4l1.4 1.4M3.2 12.8l1.4-1.4M11.4 4.6l1.4-1.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="8" cy="8" r="2.4" stroke="currentColor" stroke-width="1.4"/></svg>' },
  { key: 'system', label: '系统信息', icon: '<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="8.5" rx="1.5" stroke="currentColor" stroke-width="1.4"/><path d="M5.5 13h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>' },
  { key: 'operations', label: '作业监控', icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M2 12.5h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M4 10V7M8 10V4M12 10V6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { key: 'sessions', label: '会话管理', icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M3 3.5h10M3 8h10M3 12.5h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { key: 'overview', label: '概览', icon: '<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="4.5" height="4.5" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="9.5" y="2" width="4.5" height="4.5" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="2" y="9.5" width="4.5" height="4.5" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="9.5" y="9.5" width="4.5" height="4.5" rx="1" stroke="currentColor" stroke-width="1.3"/></svg>' },
]

const aiPanelConfig = computed(() => ({
  provider: aiApi.aiConfig.provider,
  base_url: aiApi.aiConfig.base_url,
  model: aiApi.aiConfig.model,
  api_key: aiApi.aiConfig.api_key,
  has_api_key: aiApi.aiConfig.has_api_key,
  api_key_masked: aiApi.aiConfig.api_key_masked,
  clear_api_key: aiApi.aiConfig.clear_api_key,
}))

onMounted(async () => {
  const user = await getCurrentUser()
  if (!user || user.role !== 'admin') {
    window.location.href = '/login?redirect=%2Fadmin'
    return
  }
  username.value = user.username || ''
  ready.value = true
  await loadTabData(activeTab.value)
})

async function loadTabData(tab) {
  if (tab === 'users') return usersApi.loadUsers()
  if (tab === 'ai') return aiApi.loadAiConfig()
  if (tab === 'system') return aiApi.loadSystemInfo()
  if (tab === 'operations') return operationsApi.loadOperationsData()
  if (tab === 'sessions') return sessionsApi.loadSessions()
  return dashboardApi.loadDashboard()
}

async function changeTab(tab) {
  activeTab.value = tab
  clearMessage()
  await loadTabData(tab)
}

function handleLogout() {
  logout()
}

function handleAiConfigUpdate(nextValue) {
  aiApi.aiConfig.provider = nextValue.provider
  aiApi.aiConfig.base_url = nextValue.base_url
  aiApi.aiConfig.model = nextValue.model
  aiApi.aiConfig.api_key = nextValue.api_key
  aiApi.aiConfig.clear_api_key = nextValue.clear_api_key
}

async function handleSaveAiConfig() {
  try {
    await aiApi.saveAiConfig()
    setMessage('AI 配置已保存并立即生效', 'success')
  } catch (err) {
    setMessage(err.message || 'AI 配置保存失败', 'error')
  }
}

function handleUserFiltersChange(nextFilters) {
  usersApi.filters.keyword = nextFilters.keyword
  usersApi.filters.role = nextFilters.role
  usersApi.filters.is_active = nextFilters.is_active
  usersApi.page.value = 1
  usersApi.loadUsers()
}

function handleUsersPageChange(nextPage) {
  usersApi.page.value = nextPage
  usersApi.loadUsers()
}

function openCreateUser() {
  userDialog.visible = true
  userDialog.mode = 'create'
  userDialog.targetUser = null
  userDialog.form = { username: '', password: '', role: 'user' }
}

function openEditUser(user) {
  userDialog.visible = true
  userDialog.mode = 'edit'
  userDialog.targetUser = user
  userDialog.form = { username: user.username, password: '', role: user.role }
}

function closeUserDialog() {
  userDialog.visible = false
}

async function submitUserDialog() {
  try {
    if (userDialog.mode === 'create') {
      await usersApi.createUser(userDialog.form)
      setMessage(`账户 ${userDialog.form.username} 已创建`, 'success')
    } else {
      await usersApi.updateUser(userDialog.targetUser.id, {
        username: userDialog.form.username,
        role: userDialog.form.role,
      })
      setMessage(`账户 ${userDialog.form.username} 已更新`, 'success')
    }
    closeUserDialog()
  } catch (err) {
    setMessage(err.message || '账户操作失败', 'error')
  }
}

function openResetPassword(user) {
  passwordDialog.visible = true
  passwordDialog.targetUser = user
  passwordDialog.password = ''
}

function closePasswordDialog() {
  passwordDialog.visible = false
}

async function submitPasswordDialog() {
  try {
    await usersApi.resetPassword(passwordDialog.targetUser.id, passwordDialog.password)
    setMessage(`已重置 ${passwordDialog.targetUser.username} 的密码`, 'success')
    closePasswordDialog()
  } catch (err) {
    setMessage(err.message || '密码重置失败', 'error')
  }
}

function openToggleUser(user) {
  confirmDialog.visible = true
  confirmDialog.title = user.is_active ? '停用账户' : '启用账户'
  confirmDialog.message = user.is_active
    ? `确认停用账户 ${user.username}？停用后该账号将无法继续登录。`
    : `确认重新启用账户 ${user.username}？`
  confirmDialog.confirmText = user.is_active ? '确认停用' : '确认启用'
  confirmDialog.danger = !!user.is_active
  confirmDialog.action = async () => {
    await usersApi.toggleUserActive(user.id, !user.is_active)
    setMessage(`账户 ${user.username} 已${user.is_active ? '停用' : '启用'}`, 'success')
  }
}

function openDeleteSession(session) {
  confirmDialog.visible = true
  confirmDialog.title = '删除会话'
  confirmDialog.message = `确认删除会话 ${session.id}？这个操作不可撤销。`
  confirmDialog.confirmText = '确认删除'
  confirmDialog.danger = true
  confirmDialog.action = async () => {
    await sessionsApi.removeSession(session.id)
    await dashboardApi.loadDashboard()
    setMessage(`会话 ${session.id} 已删除`, 'success')
  }
}

function openCleanupSessions() {
  confirmDialog.visible = true
  confirmDialog.title = '清理过期会话'
  confirmDialog.message = '确认执行过期会话清理？这会删除已过期的数据和产物。'
  confirmDialog.confirmText = '立即清理'
  confirmDialog.danger = true
  confirmDialog.action = async () => {
    const result = await sessionsApi.cleanupSessions()
    await dashboardApi.loadDashboard()
    setMessage(result.message || '过期会话已清理', 'success')
  }
}

function closeConfirmDialog() {
  confirmDialog.visible = false
  confirmDialog.action = null
}

async function submitConfirmDialog() {
  if (!confirmDialog.action) return
  try {
    await confirmDialog.action()
  } catch (err) {
    setMessage(err.message || '操作失败', 'error')
  } finally {
    closeConfirmDialog()
  }
}

function handleJobFiltersChange(nextFilters) {
  operationsApi.jobFilters.status = nextFilters.status
  operationsApi.jobFilters.queue = nextFilters.queue
  operationsApi.jobFilters.job_type = nextFilters.job_type
  operationsApi.jobPage.value = 1
  operationsApi.loadJobs()
}

function handleSandboxFiltersChange(nextFilters) {
  operationsApi.sandboxFilters.status = nextFilters.status
  operationsApi.sandboxFilters.executor_mode = nextFilters.executor_mode
  operationsApi.sandboxPage.value = 1
  operationsApi.loadSandboxExecutions()
}

function handleJobPageChange(nextPage) {
  operationsApi.jobPage.value = nextPage
  operationsApi.loadJobs()
}

function handleSandboxPageChange(nextPage) {
  operationsApi.sandboxPage.value = nextPage
  operationsApi.loadSandboxExecutions()
}

function handleSessionPageChange(nextPage) {
  sessionsApi.page.value = nextPage
  sessionsApi.loadSessions()
}

function setMessage(text, type = '') {
  globalMessage.text = text
  globalMessage.type = type
  window.clearTimeout(setMessage._timer)
  setMessage._timer = window.setTimeout(clearMessage, 3200)
}

function clearMessage() {
  globalMessage.text = ''
  globalMessage.type = ''
}
</script>
