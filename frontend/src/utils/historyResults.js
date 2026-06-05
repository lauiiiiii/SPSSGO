export function createStoredResultMapper(methodsMeta) {
  const VISUALIZATION_CODE = '[可视化绘图]'

  function isVisualizationResult(result) {
    return result?.code === VISUALIZATION_CODE
  }

  function inferMethodKeyFromName(name) {
    const text = String(name || '').trim()
    if (!text) return ''

    let matchedKey = ''
    let matchedLen = 0
    for (const [key, meta] of Object.entries(methodsMeta.value || {})) {
      const labels = [meta?.label, ...(meta?.aliases || [])]
        .map(label => String(label || '').trim())
        .filter(Boolean)
      for (const label of labels) {
        const hit = text === label || text.startsWith(label + ':') || text.startsWith(label + '：') || text.startsWith(label + ' ')
        if (hit && label.length > matchedLen) {
          matchedKey = key
          matchedLen = label.length
        }
      }
    }
    return matchedKey
  }

  function mapStoredResult(result) {
    const methodKey = inferMethodKeyFromName(result.analysis_name)
    return {
      id: result.id,
      name: result.analysis_name,
      method: methodKey,
      code: result.code || '',
      dataset_version_id: result.dataset_version_id || null,
      dataset_version_no: result.dataset_version_no || null,
      created_at: result.created_at || null,
      results: [{
        id: result.id,
        name: result.analysis_name,
        code: result.code || '',
        sections: result.sections,
        headers: result.table_headers,
        rows: result.table_rows,
        description: result.description,
        job_id: result.job_id || null,
        dataset_version_id: result.dataset_version_id || null,
        dataset_version_no: result.dataset_version_no || null,
        created_at: result.created_at || null,
      }],
    }
  }

  function mapStoredResults(results, options = {}) {
    const kind = options.kind || 'analysis'
    return (results || [])
      .filter(result => {
        if (kind === 'all') return true
        if (kind === 'visualization') return isVisualizationResult(result)
        return !isVisualizationResult(result)
      })
      .slice()
      .reverse()
      .map(mapStoredResult)
  }

  return {
    inferMethodKeyFromName,
    isVisualizationResult,
    mapStoredResult,
    mapStoredResults,
  }
}
