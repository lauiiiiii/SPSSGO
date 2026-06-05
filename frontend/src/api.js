import { apiUrl } from './runtimeConfig.js'

export { apiUrl }

const TERMINAL_JOB_STATUSES = new Set(['succeeded', 'failed', 'canceled'])

export const requestJitterSeed = [76, 126, 106, 101, 108, 127, 106, 98, 97, 98, 97, 106, 99, 110, 37]

function getToken() {
  return localStorage.getItem('spssgo_token') || ''
}

function authHeaders(extra = {}) {
  const token = getToken()
  const headers = { ...extra }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

export function handleAuthError() {
  const current = `${window.location.pathname}${window.location.search}${window.location.hash}`
  localStorage.removeItem('spssgo_token')
  localStorage.removeItem('spssgo_refresh_token')
  localStorage.removeItem('spssgo_user')
  localStorage.removeItem('spssgo_role')
  localStorage.removeItem('spssgo_session_id')
  localStorage.removeItem('spssgo_visualization_session_id')
  const next = current && current !== '/login' ? `/login?redirect=${encodeURIComponent(current)}` : '/login'
  window.location.href = next
}

async function parseErrorResponse(resp, fallbackMessage) {
  const err = await resp.json().catch(() => ({ detail: resp.statusText }))
  const detail = typeof err?.detail === 'object' && err?.detail
    ? err.detail.message || fallbackMessage
    : err?.detail || fallbackMessage
  const error = new Error(detail)
  error.status = resp.status
  error.code = typeof err?.detail === 'object' ? err.detail.code : undefined
  throw error
}

export async function request(url, options = {}) {
  options.headers = authHeaders(options.headers || {})
  const resp = await fetch(apiUrl(url), options)
  if (resp.status === 401) { handleAuthError(); return }
  if (!resp.ok) {
    await parseErrorResponse(resp, '请求失败')
  }
  return resp.json()
}

export async function publicRequest(url, options = {}) {
  const resp = await fetch(apiUrl(url), options)
  if (!resp.ok) {
    await parseErrorResponse(resp, '请求失败')
  }
  return resp.json()
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function parseSseChunk(chunk, onEvent) {
  let eventName = 'message'
  const dataLines = []
  const lines = String(chunk || '').split('\n')
  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, '')
    if (!line) continue
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim() || 'message'
      continue
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }
  if (!dataLines.length) return
  const rawData = dataLines.join('\n')
  let payload = rawData
  try {
    payload = JSON.parse(rawData)
  } catch (_) { /* ignore non-json payload */ }
  onEvent(eventName, payload)
}

async function streamSse(url, callbacks = {}, options = {}) {
  const resp = await fetch(apiUrl(url), {
    method: options.method || 'GET',
    headers: authHeaders({
      Accept: 'text/event-stream',
      ...(options.headers || {}),
    }),
    body: options.body,
    signal: options.signal,
  })
  if (resp.status === 401) { handleAuthError(); return }
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || '事件流请求失败')
  }
  if (!resp.body || typeof resp.body.getReader !== 'function') {
    throw new Error('当前环境不支持流式事件')
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''

    for (const part of parts) {
      if (!part.trim()) continue
      parseSseChunk(part, (event, payload) => {
        if (callbacks[event]) callbacks[event](payload)
        if (callbacks.message) callbacks.message({ event, payload })
      })
    }
  }

  if (buffer.trim()) {
    parseSseChunk(buffer, (event, payload) => {
      if (callbacks[event]) callbacks[event](payload)
      if (callbacks.message) callbacks.message({ event, payload })
    })
  }
}

function mapStoredResultToExecutionItem(item) {
  return {
    id: item.id,
    name: item.analysis_name,
    headers: item.table_headers || [],
    rows: item.table_rows || [],
    description: item.description || '',
    sections: item.sections || null,
    job_id: item.job_id || null,
    dataset_version_id: item.dataset_version_id || null,
    dataset_version_no: item.dataset_version_no || null,
    created_at: item.created_at || null,
  }
}

export function getJob(jobId) {
  return request(`/api/jobs/${jobId}`)
}

export function cancelJob(jobId) {
  return request(`/api/jobs/${jobId}/cancel`, {
    method: 'POST',
  })
}

export function retryJob(jobId) {
  return request(`/api/jobs/${jobId}/retry`, {
    method: 'POST',
  })
}

export function streamJobEvents(jobId, callbacks = {}, options = {}) {
  return streamSse(`/api/jobs/${jobId}/events`, callbacks, options)
}

export async function getJobOutputBuffer(jobId) {
  const resp = await fetch(apiUrl(`/api/jobs/${jobId}/output`), {
    headers: authHeaders(),
  })
  if (resp.status === 401) { handleAuthError(); return }
  if (!resp.ok) {
    const detail = await resp
      .clone()
      .json()
      .then(data => data?.detail || '')
      .catch(async () => (await resp.text().catch(() => '')).trim())
    throw new Error(detail || `任务产物下载失败（HTTP ${resp.status}）`)
  }
  return resp.arrayBuffer()
}

export async function waitForJob(jobId, options = {}) {
  const {
    timeoutMs = 5 * 60 * 1000,
    intervalMs = 1000,
    onProgress = null,
    preferStream = true,
  } = options
  if (!preferStream) {
    return waitForJobByPolling(jobId, { timeoutMs, intervalMs, onProgress })
  }

  const startedAt = Date.now()
  let latestJob = null
  let timedOut = false
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null
  const timeoutHandle = controller
    ? setTimeout(() => {
      timedOut = true
      controller.abort()
    }, timeoutMs)
    : null

  try {
    await streamJobEvents(jobId, {
      job(job) {
        latestJob = job
        if (onProgress) onProgress(job)
      },
      done(job) {
        latestJob = job
        if (onProgress) onProgress(job)
      },
    }, {
      signal: controller?.signal,
    })
    if (latestJob && TERMINAL_JOB_STATUSES.has(latestJob.status)) return latestJob
    throw new Error('任务事件流已结束')
  } catch (error) {
    if (timedOut) {
      throw new Error('任务执行超时，请稍后在任务状态中重试')
    }
    if (latestJob && TERMINAL_JOB_STATUSES.has(latestJob.status)) return latestJob
    const remaining = Math.max(timeoutMs - (Date.now() - startedAt), intervalMs)
    return waitForJobByPolling(jobId, {
      timeoutMs: remaining,
      intervalMs,
      onProgress,
    })
  } finally {
    if (timeoutHandle) clearTimeout(timeoutHandle)
  }
}

async function waitForJobByPolling(jobId, options = {}) {
  const {
    timeoutMs = 5 * 60 * 1000,
    intervalMs = 1000,
    onProgress = null,
  } = options
  const startedAt = Date.now()
  let lastSignature = ''

  while (true) {
    const job = await getJob(jobId)
    const signature = JSON.stringify([job.status, job.progress, job.result, job.error_message])
    if (signature !== lastSignature) {
      lastSignature = signature
      if (onProgress) onProgress(job)
    }
    if (TERMINAL_JOB_STATUSES.has(job.status)) return job
    if (Date.now() - startedAt > timeoutMs) {
      throw new Error('任务执行超时，请稍后在任务状态中重试')
    }
    await sleep(intervalMs)
  }
}

export function createSession() {
  return request('/api/session', { method: 'POST' })
}

export async function uploadFile(sessionId, file, options = {}) {
  const fd = new FormData()
  fd.append('file', file)
  const accepted = await request(`/api/upload/${sessionId}`, { method: 'POST', body: fd })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') throw new Error(job.error_message || '上传失败')
  return { ...accepted, ...job.result, job }
}

export async function generatePlan(sessionId, form, options = {}) {
  const fd = new FormData()
  for (const [k, v] of Object.entries(form)) {
    fd.append(k, v)
  }
  const accepted = await request(`/api/plan/${sessionId}`, { method: 'POST', body: fd })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    throw new Error(job.error_message || 'AI 生成计划失败')
  }
  return { ...(job.result || {}), job_id: accepted.job_id, job }
}

export async function executePlan(sessionId, planText, options = {}) {
  const fd = new FormData()
  fd.append('plan_edit', planText)
  const accepted = await request(`/api/execute/${sessionId}`, { method: 'POST', body: fd })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    return { success: false, error: job.error_message || '整套分析执行失败', job }
  }
  const resultData = await getResults(sessionId)
  const results = (resultData.results || [])
    .filter(item => item.job_id === accepted.job_id)
    .map(mapStoredResultToExecutionItem)
  return {
    success: true,
    results,
    job_id: accepted.job_id,
    job,
    mode: job.result?.mode || '',
  }
}

export async function executePlanStream(sessionId, planText, callbacks) {
  const fd = new FormData()
  fd.append('plan_edit', planText)
  return streamSse(`/api/execute-stream/${sessionId}`, callbacks, {
    method: 'POST',
    body: fd,
  })
}

export function getResults(sessionId) {
  return request(`/api/results/${sessionId}`)
}

export function renameAnalysisResult(sessionId, resultId, name) {
  return request(`/api/results/${sessionId}/${resultId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function deleteAnalysisResult(sessionId, resultId) {
  return request(`/api/results/${sessionId}/${resultId}`, {
    method: 'DELETE',
  })
}

export function createReportShare(sessionId, payload) {
  return request('/api/shared-reports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      ...payload,
    }),
  })
}

export function getReportShare(shareToken) {
  return publicRequest(`/api/shared-reports/${encodeURIComponent(shareToken)}`)
}

export function accessReportShare(shareToken, password = '') {
  return publicRequest(`/api/shared-reports/${encodeURIComponent(shareToken)}/access`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
}

export function downloadWordUrl(sessionId) {
  return apiUrl(`/api/download/${sessionId}?token=${getToken()}`)
}

export async function downloadWordBuffer(sessionId, options = {}) {
  const accepted = await request(`/api/download/${sessionId}`, {
    method: 'POST',
  })
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    throw new Error(job.error_message || '报告生成失败')
  }
  return getJobOutputBuffer(accepted.job_id)
}

export function getSessions() {
  return request('/api/sessions')
}

export function getDatasets(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString() ? `?${search.toString()}` : ''
  return request(`/api/datasets${suffix}`)
}

export function renameDataset(datasetId, name) {
  return request(`/api/datasets/${datasetId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function renameDatasetVersion(versionId, name) {
  return request(`/api/dataset-versions/${versionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function deleteDatasetVersion(versionId) {
  return request(`/api/dataset-versions/${versionId}`, { method: 'DELETE' })
}

export function copyDatasetVersion(versionId, name) {
  return request(`/api/dataset-versions/${versionId}/copy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function touchDataset(datasetId) {
  return request(`/api/datasets/${datasetId}/touch`, { method: 'POST' })
}

export function deleteDataset(datasetId) {
  return request(`/api/datasets/${datasetId}`, { method: 'DELETE' })
}

export function getDatasetFolders() {
  return request('/api/dataset-folders')
}

export function createDatasetFolder(name) {
  return request('/api/dataset-folders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function renameDatasetFolder(folderId, name) {
  return request(`/api/dataset-folders/${folderId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
}

export function deleteDatasetFolder(folderId) {
  return request(`/api/dataset-folders/${folderId}`, { method: 'DELETE' })
}

export function moveDatasetToFolder(sessionId, folderId) {
  return request('/api/dataset-folder-items', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, folder_id: folderId || null }),
  })
}

export function getSessionInfo(sessionId) {
  return request(`/api/session/${sessionId}`)
}

export function renameSession(sessionId, title) {
  const fd = new FormData()
  fd.append('title', title)
  return request(`/api/session/${sessionId}/title`, { method: 'PATCH', body: fd })
}

export function deleteSession(sessionId) {
  return request(`/api/session/${sessionId}`, { method: 'DELETE' })
}

export function getFiles(sessionId) {
  return request(`/api/files/${sessionId}`)
}

export function dataFileUrl(sessionId) {
  return apiUrl(`/api/data-file/${sessionId}?token=${getToken()}`)
}

export function getQuestionnaireContent(sessionId, filename) {
  return request(`/api/questionnaire/${sessionId}/${encodeURIComponent(filename)}`)
}

export function getDataPreview(sessionId, limit = 100) {
  return request(`/api/data-preview/${sessionId}?limit=${encodeURIComponent(limit)}`)
}

export function batchDeleteDatasets(sessionIds) {
  return request('/api/datasets/batch-delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_ids: sessionIds }),
  })
}

export function batchMoveDatasetsToFolder(sessionIds, folderId) {
  return request('/api/dataset-folder-items/batch-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_ids: sessionIds, folder_id: folderId }),
  })
}

export async function getDataFileBuffer(sessionId) {
  const resp = await fetch(apiUrl(`/api/data-file/${sessionId}`), {
    headers: authHeaders(),
  })
  if (resp.status === 401) { handleAuthError(); return }
  if (!resp.ok) throw new Error('文件下载失败')
  return resp.arrayBuffer()
}

export async function exportDataFileBuffer(sessionId, format) {
  const resp = await fetch(apiUrl(`/api/data-file/${sessionId}/export?format=${encodeURIComponent(format)}`), {
    headers: authHeaders(),
  })
  if (resp.status === 401) { handleAuthError(); return }
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: '文件导出失败' }))
    throw new Error(err.detail || '文件导出失败')
  }
  return resp.arrayBuffer()
}

export function getMethods() {
  return request('/api/methods')
}

export function getVariables(sessionId) {
  return request(`/api/variables/${sessionId}`)
}

export function getVariableValues(sessionId, columnName) {
  return request(`/api/variable-values/${sessionId}/${encodeURIComponent(columnName)}`)
}

export async function executeMethod(sessionId, method, params, options = {}) {
  const accepted = await request(`/api/execute-method/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ method, params }),
  })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    return { success: false, error: job.error_message || '分析执行失败', job }
  }
  const resultData = await getResults(sessionId)
  const results = (resultData.results || [])
    .filter(item => item.job_id === accepted.job_id)
    .map(mapStoredResultToExecutionItem)
  return { success: true, results, job_id: accepted.job_id, job }
}

export async function processData(sessionId, method, params, options = {}) {
  const accepted = await request(`/api/process/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ method, params }),
  })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    return { success: false, error: job.error_message || '数据处理失败', job }
  }
  return { success: true, ...(job.result || {}), job_id: accepted.job_id, job }
}

export function previewVisualization(sessionId, payload) {
  return request(`/api/visualizations/${sessionId}/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function saveVisualization(sessionId, payload) {
  return request(`/api/visualizations/${sessionId}/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function renameVariable(sessionId, columnName, newName) {
  return request(`/api/variables/${sessionId}/${encodeURIComponent(columnName)}/rename`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_name: newName }),
  })
}

export function changeVariableType(sessionId, columnName, targetType) {
  return request(`/api/variables/${sessionId}/${encodeURIComponent(columnName)}/type`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_type: targetType }),
  })
}

export function deleteVariable(sessionId, columnName) {
  return request(`/api/variables/${sessionId}/${encodeURIComponent(columnName)}`, {
    method: 'DELETE',
  })
}

export function getDatasetVersions(sessionId) {
  return request(`/api/dataset-versions/${sessionId}`)
}

export function activateDatasetVersion(sessionId, versionId) {
  return request(`/api/dataset-versions/${sessionId}/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version_id: versionId }),
  })
}

/**
 * 调用 AI 智能解读接口
 *
 * @param method 分析方法名称
 * @param sections 结果 sections 数组
 * @return 包含 interpretation 文本的 Promise
 */
export async function aiInterpret(method, sections, options = {}) {
  const accepted = await request('/api/ai-interpret', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      method,
      sections,
      session_id: options.sessionId || null,
      dataset_version_id: options.datasetVersionId || null,
    }),
  })
  if (options.wait === false) return accepted
  const job = await waitForJob(accepted.job_id, options)
  if (job.status !== 'succeeded') {
    throw new Error(job.error_message || 'AI 解读失败')
  }
  return { ...(job.result || {}), job_id: accepted.job_id, job }
}

export async function aiAssist(message) {
  return request('/api/ai-assist', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
}

export async function login(credentials) {
  return publicRequest('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })
}

export async function checkToken(token = getToken()) {
  if (!token) return false
  const resp = await fetch(apiUrl('/api/me'), {
    headers: { Authorization: `Bearer ${token}` },
  })
  return resp.ok
}

export function saveAuthSession(data) {
  localStorage.setItem('spssgo_token', data.token)
  if (data.refresh_token) localStorage.setItem('spssgo_refresh_token', data.refresh_token)
  localStorage.setItem('spssgo_user', data.username)
  if (data.role) localStorage.setItem('spssgo_role', data.role)
}

export function checkAuth() {
  const token = getToken()
  if (!token) { handleAuthError(); return false }
  return true
}

export function logout() {
  localStorage.removeItem('spssgo_token')
  localStorage.removeItem('spssgo_refresh_token')
  localStorage.removeItem('spssgo_user')
  localStorage.removeItem('spssgo_role')
  localStorage.removeItem('spssgo_session_id')
  window.location.href = '/login'
}

export function getUsername() {
  return localStorage.getItem('spssgo_user') || ''
}

export function getCurrentUser() {
  return request('/api/me')
}

export function changeUsername(newUsername) {
  return request('/api/change-username', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_username: newUsername }),
  })
}

export function changePassword(oldPassword, newPassword) {
  return request('/api/change-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  })
}

export function getAdminUsers(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString() ? `?${search.toString()}` : ''
  return request(`/api/admin/users${suffix}`)
}

export function createAdminUser(payload) {
  return request('/api/admin/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function updateAdminUser(userId, payload) {
  return request(`/api/admin/users/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function resetAdminUserPassword(userId, newPassword) {
  return request(`/api/admin/users/${userId}/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_password: newPassword }),
  })
}

export function toggleAdminUserActive(userId, isActive) {
  return request(`/api/admin/users/${userId}/toggle-active`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  })
}

export function getAdminDashboard() {
  return request('/api/admin/dashboard')
}

export function getAdminSessions(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString() ? `?${search.toString()}` : ''
  return request(`/api/admin/sessions${suffix}`)
}

export function deleteAdminSession(sessionId) {
  return request(`/api/admin/sessions/${sessionId}`, { method: 'DELETE' })
}

export function cleanupAdminSessions() {
  return request('/api/admin/cleanup', { method: 'POST' })
}

export function getAdminOperations() {
  return request('/api/admin/operations')
}

export function getAdminJobs(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString() ? `?${search.toString()}` : ''
  return request(`/api/admin/jobs${suffix}`)
}

export function getAdminSandboxExecutions(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  })
  const suffix = search.toString() ? `?${search.toString()}` : ''
  return request(`/api/admin/sandbox-executions${suffix}`)
}

export function getAdminSystemInfo() {
  return request('/api/admin/system')
}

export function getAdminAiConfig() {
  return request('/api/admin/ai-config')
}

export function saveAdminAiConfig(payload) {
  return request('/api/admin/ai-config', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
