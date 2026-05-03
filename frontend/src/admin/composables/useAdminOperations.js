import { computed, reactive, ref } from 'vue'
import { getAdminJobs, getAdminOperations, getAdminSandboxExecutions } from '../api.js'

export function useAdminOperations() {
  const operationsSummary = ref({})
  const summaryLoading = ref(false)
  const summaryError = ref('')

  const jobs = ref([])
  const jobsLoading = ref(false)
  const jobsError = ref('')
  const jobPage = ref(1)
  const jobSize = ref(12)
  const jobTotal = ref(0)
  const jobFilters = reactive({
    status: '',
    queue: '',
    job_type: '',
  })

  const sandboxExecutions = ref([])
  const sandboxLoading = ref(false)
  const sandboxError = ref('')
  const sandboxPage = ref(1)
  const sandboxSize = ref(12)
  const sandboxTotal = ref(0)
  const sandboxFilters = reactive({
    status: '',
    executor_mode: '',
  })

  const queueChips = computed(() => Object.entries(operationsSummary.value.job_queue_counts || {}).map(([key, count]) => ({ key, count })))
  const sandboxModeChips = computed(() => Object.entries(operationsSummary.value.sandbox_mode_counts || {}).map(([key, count]) => ({ key, count })))

  async function loadSummary() {
    summaryLoading.value = true
    summaryError.value = ''
    try {
      operationsSummary.value = await getAdminOperations()
    } catch (err) {
      summaryError.value = err.message || '作业总览加载失败'
    } finally {
      summaryLoading.value = false
    }
  }

  async function loadJobs() {
    jobsLoading.value = true
    jobsError.value = ''
    try {
      const data = await getAdminJobs({
        page: jobPage.value,
        size: jobSize.value,
        status: jobFilters.status,
        queue: jobFilters.queue,
        job_type: jobFilters.job_type,
      })
      jobs.value = data.jobs || []
      jobTotal.value = data.total || 0
    } catch (err) {
      jobsError.value = err.message || '作业列表加载失败'
    } finally {
      jobsLoading.value = false
    }
  }

  async function loadSandboxExecutions() {
    sandboxLoading.value = true
    sandboxError.value = ''
    try {
      const data = await getAdminSandboxExecutions({
        page: sandboxPage.value,
        size: sandboxSize.value,
        status: sandboxFilters.status,
        executor_mode: sandboxFilters.executor_mode,
      })
      sandboxExecutions.value = data.executions || []
      sandboxTotal.value = data.total || 0
    } catch (err) {
      sandboxError.value = err.message || 'Sandbox 审计加载失败'
    } finally {
      sandboxLoading.value = false
    }
  }

  async function loadOperationsData() {
    await Promise.all([loadSummary(), loadJobs(), loadSandboxExecutions()])
  }

  return {
    operationsSummary,
    summaryLoading,
    summaryError,
    jobs,
    jobsLoading,
    jobsError,
    jobPage,
    jobSize,
    jobTotal,
    jobFilters,
    sandboxExecutions,
    sandboxLoading,
    sandboxError,
    sandboxPage,
    sandboxSize,
    sandboxTotal,
    sandboxFilters,
    queueChips,
    sandboxModeChips,
    loadSummary,
    loadJobs,
    loadSandboxExecutions,
    loadOperationsData,
  }
}
