export function formatReportMetaTime(value) {
  if (!value) return ''
  try {
    return new Date(Number(value) * 1000).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (_) {
    return ''
  }
}

export function buildReportMetaTags({
  result,
}) {
  if (!result) return []
  const tags = []
  if (result.created_at) {
    tags.push(`生成于 ${formatReportMetaTime(result.created_at)}`)
  }
  return tags
}
