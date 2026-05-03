export const TERMINAL_JOB_STATUSES = new Set(['succeeded', 'failed', 'canceled'])
export const CANCELABLE_JOB_STATUSES = new Set(['pending', 'queued', 'running', 'retrying'])
export const RETRYABLE_JOB_STATUSES = new Set(['failed', 'canceled'])

export function sortTaskJobs(jobs) {
  return [...(jobs || [])].sort((a, b) => {
    const aTerminal = TERMINAL_JOB_STATUSES.has(a.status)
    const bTerminal = TERMINAL_JOB_STATUSES.has(b.status)
    if (aTerminal !== bTerminal) return aTerminal ? 1 : -1
    return Number(b.created_at || 0) - Number(a.created_at || 0)
  })
}

export function statusLabel(status) {
  if (status === 'queued') return '排队中'
  if (status === 'running') return '执行中'
  if (status === 'succeeded') return '已完成'
  if (status === 'failed') return '失败'
  if (status === 'canceled') return '已取消'
  if (status === 'retrying') return '重试中'
  return '待处理'
}

export function jobLabel(job) {
  if (job.job_type === 'upload_ingest') return '文件解析'
  if (job.job_type === 'process_data') return '数据处理'
  if (job.job_type === 'ai_plan') return 'AI 规划'
  if (job.job_type === 'ai_interpret') return 'AI 解读'
  if (job.job_type === 'execute_method') return '结构化分析'
  if (job.job_type === 'execute_plan') return '整套分析'
  if (job.job_type === 'generate_report') return '报告导出'
  return job.job_type || '任务'
}

export function queueLabel(queue) {
  if (queue === 'ingest') return '解析队列'
  if (queue === 'process') return '处理队列'
  if (queue === 'analysis') return '分析队列'
  if (queue === 'report') return '报告队列'
  if (queue === 'ai') return 'AI 队列'
  if (queue === 'sandbox') return '沙箱队列'
  return '默认队列'
}

export function progressMessage(job) {
  const progress = job.progress || {}
  let text = progress.message || '等待执行'
  if (Number.isFinite(progress.current) && Number.isFinite(progress.total) && progress.total > 0) {
    text += ` (${progress.current}/${progress.total})`
  }
  return text
}

export function progressPercent(job) {
  const progress = job.progress || {}
  if (job.status === 'succeeded') return 100
  if (!(Number.isFinite(progress.current) && Number.isFinite(progress.total) && progress.total > 0)) return 0
  return Math.max(0, Math.min(100, Math.round((progress.current / progress.total) * 100)))
}

export function formatJobTime(value) {
  if (!value) return '刚刚'
  try {
    return new Date(Number(value) * 1000).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch (_) {
    return '刚刚'
  }
}

export function canCancelJob(job) {
  return CANCELABLE_JOB_STATUSES.has(job?.status)
}

export function canRetryJob(job) {
  return RETRYABLE_JOB_STATUSES.has(job?.status)
}
