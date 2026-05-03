import { computed, onBeforeUnmount, watch } from 'vue'
import * as api from '../../api.js'

const TASK_JOB_RECONCILE_INTERVAL_MS = 4000
const TERMINAL_JOB_STATUSES = new Set(['succeeded', 'failed', 'canceled'])

export function useTaskJobs({
  currentDatasetVersionId,
  currentDatasetVersionNo,
  historyItems,
  mapStoredResults,
  sessionId,
  taskJobs,
}) {
  let taskJobPollTimer = null
  let taskJobPollPending = false
  const taskJobStreams = new Map()

  const activeJobCount = computed(() => taskJobs.value.filter(job => !isTerminalJob(job)).length)

  function isTerminalJob(job) {
    return TERMINAL_JOB_STATUSES.has(job?.status)
  }

  function sortTaskJobs(items) {
    return [...items].sort((a, b) => {
      const aTerminal = isTerminalJob(a)
      const bTerminal = isTerminalJob(b)
      if (aTerminal !== bTerminal) return aTerminal ? 1 : -1
      return Number(b.created_at || 0) - Number(a.created_at || 0)
    })
  }

  function upsertTaskJob(job) {
    if (!job) return
    if (sessionId.value && job.session_id && job.session_id !== sessionId.value) return
    const next = [...taskJobs.value]
    const idx = next.findIndex(item => item.id === job.id)
    if (idx >= 0) next[idx] = { ...next[idx], ...job }
    else next.unshift(job)
    taskJobs.value = sortTaskJobs(next).slice(0, 12)
    if (isTerminalJob(job)) {
      stopTaskJobStream(job.id)
    } else {
      ensureTaskJobStream(job)
    }
  }

  function replaceActiveTaskJobs(jobs) {
    const activeIds = new Set((jobs || []).map(job => job.id))
    const retained = taskJobs.value.filter(job => isTerminalJob(job) || activeIds.has(job.id))
    taskJobs.value = retained
    for (const job of (jobs || [])) {
      upsertTaskJob(job)
    }
  }

  function clearCompletedTaskJobs() {
    taskJobs.value = taskJobs.value.filter(job => !isTerminalJob(job))
  }

  function syncResultContext(resData) {
    currentDatasetVersionId.value = resData?.current_dataset_version_id || null
    currentDatasetVersionNo.value = resData?.current_dataset_version_no || null
  }

  function patchTaskJob(jobId, patch) {
    const idx = taskJobs.value.findIndex(job => job.id === jobId)
    if (idx < 0) return
    const next = [...taskJobs.value]
    next[idx] = { ...next[idx], ...patch }
    taskJobs.value = sortTaskJobs(next)
  }

  function stopTaskJobStream(jobId) {
    const controller = taskJobStreams.get(jobId)
    if (!controller) return
    controller.abort()
    taskJobStreams.delete(jobId)
  }

  function stopTaskJobStreams() {
    for (const controller of taskJobStreams.values()) {
      controller.abort()
    }
    taskJobStreams.clear()
  }

  function ensureTaskJobStream(job) {
    if (!job?.id || isTerminalJob(job)) return
    if (taskJobStreams.has(job.id)) return
    if (sessionId.value && job.session_id && job.session_id !== sessionId.value) return

    const controller = new AbortController()
    taskJobStreams.set(job.id, controller)
    api.streamJobEvents(job.id, {
      job(snapshot) {
        if (taskJobStreams.get(job.id) !== controller) return
        upsertTaskJob(snapshot)
      },
      done(snapshot) {
        if (taskJobStreams.get(job.id) !== controller) return
        upsertTaskJob(snapshot)
        stopTaskJobStream(job.id)
        refreshTaskJobs({ forceResults: true })
      },
    }, {
      signal: controller.signal,
    }).catch(() => {
      if (taskJobStreams.get(job.id) === controller) {
        taskJobStreams.delete(job.id)
      }
    })
  }

  function stopTaskJobPolling() {
    if (taskJobPollTimer) {
      clearInterval(taskJobPollTimer)
      taskJobPollTimer = null
    }
  }

  async function refreshTaskJobs(options = {}) {
    const { forceResults = false } = options
    if (!sessionId.value) {
      taskJobs.value = []
      return
    }
    try {
      const hadActiveJobs = taskJobs.value.some(job => !isTerminalJob(job))
      const resData = await api.getResults(sessionId.value)
      syncResultContext(resData)
      replaceActiveTaskJobs(resData.jobs || [])
      if (forceResults || (resData.jobs || []).length || hadActiveJobs) {
        historyItems.value = mapStoredResults(resData.results || [])
      }
    } catch (_) { /* ignore */ }
  }

  function startTaskJobPolling() {
    stopTaskJobPolling()
    if (!sessionId.value) return
    taskJobPollTimer = setInterval(async () => {
      if (taskJobPollPending || !sessionId.value) return
      taskJobPollPending = true
      try {
        await refreshTaskJobs()
      } finally {
        taskJobPollPending = false
      }
    }, TASK_JOB_RECONCILE_INTERVAL_MS)
  }

  function handleTrackedJobProgress(job) {
    upsertTaskJob(job)
  }

  async function onCancelTaskJob(job) {
    if (!job?.id) return
    patchTaskJob(job.id, { action_pending: true, action_type: 'cancel' })
    try {
      const result = await api.cancelJob(job.id)
      patchTaskJob(job.id, { action_pending: false, action_type: '' })
      if (result?.job) upsertTaskJob(result.job)
      await refreshTaskJobs()
    } catch (e) {
      patchTaskJob(job.id, { action_pending: false, action_type: '' })
      alert('取消任务失败: ' + e.message)
    }
  }

  async function onRetryTaskJob(job) {
    if (!job?.id) return
    patchTaskJob(job.id, { action_pending: true, action_type: 'retry' })
    try {
      const result = await api.retryJob(job.id)
      patchTaskJob(job.id, { action_pending: false, action_type: '' })
      if (result?.job) upsertTaskJob(result.job)
      await refreshTaskJobs()
    } catch (e) {
      patchTaskJob(job.id, { action_pending: false, action_type: '' })
      alert('重试任务失败: ' + e.message)
    }
  }

  watch(() => sessionId.value, async (nextId) => {
    stopTaskJobStreams()
    taskJobs.value = []
    if (!nextId) {
      stopTaskJobPolling()
      currentDatasetVersionId.value = null
      currentDatasetVersionNo.value = null
      return
    }
    startTaskJobPolling()
    await refreshTaskJobs()
  })

  onBeforeUnmount(() => {
    stopTaskJobPolling()
    stopTaskJobStreams()
  })

  return {
    activeJobCount,
    clearCompletedTaskJobs,
    handleTrackedJobProgress,
    onCancelTaskJob,
    onRetryTaskJob,
    refreshTaskJobs,
    startTaskJobPolling,
    stopTaskJobPolling,
    stopTaskJobStreams,
    syncResultContext,
  }
}
