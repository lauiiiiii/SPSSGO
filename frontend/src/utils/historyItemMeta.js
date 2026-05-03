import { formatShortDateTime } from './dateFormat.js'

export function formatHistoryChipTitle(item) {
  const parts = [item?.name || '分析结果']
  if (item?.created_at) parts.push(formatShortDateTime(item.created_at))
  return parts.join(' · ')
}
