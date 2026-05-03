export function createStoredResultMapper(methodsMeta) {
  function inferMethodKeyFromName(name) {
    const text = String(name || '').trim()
    if (!text) return ''

    let matchedKey = ''
    let matchedLen = 0
    for (const [key, meta] of Object.entries(methodsMeta.value || {})) {
      const label = String(meta?.label || '').trim()
      if (!label) continue
      const hit = text === label || text.startsWith(label + ':') || text.startsWith(label + '：') || text.startsWith(label + ' ')
      if (hit && label.length > matchedLen) {
        matchedKey = key
        matchedLen = label.length
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
      dataset_version_id: result.dataset_version_id || null,
      dataset_version_no: result.dataset_version_no || null,
      created_at: result.created_at || null,
      results: [{
        id: result.id,
        name: result.analysis_name,
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

  function mapStoredResults(results) {
    return (results || []).slice().reverse().map(mapStoredResult)
  }

  return {
    inferMethodKeyFromName,
    mapStoredResult,
    mapStoredResults,
  }
}
