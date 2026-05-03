export const SESSION_STATUS_LABELS = {
  created: '已创建',
  planning: '规划中',
  plan_ready: '待执行',
  executing: '执行中',
  done: '已完成',
  error: '错误',
}

export function getSessionStatusLabel(status) {
  return SESSION_STATUS_LABELS[status] || status || '—'
}
