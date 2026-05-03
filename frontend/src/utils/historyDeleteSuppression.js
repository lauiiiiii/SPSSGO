const HISTORY_DELETE_SUPPRESS_KEY = 'spssgo_history_delete_suppress_until'

export function isHistoryDeleteSuppressed() {
  try {
    const until = Number(localStorage.getItem(HISTORY_DELETE_SUPPRESS_KEY) || 0)
    if (until > Date.now()) return true
    if (until) localStorage.removeItem(HISTORY_DELETE_SUPPRESS_KEY)
  } catch (_) { /* ignore */ }
  return false
}

export function setHistoryDeleteSuppressedForHour() {
  try {
    localStorage.setItem(HISTORY_DELETE_SUPPRESS_KEY, String(Date.now() + 60 * 60 * 1000))
  } catch (_) { /* ignore */ }
}
