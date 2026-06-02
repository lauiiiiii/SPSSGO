import * as api from '../../api.js'

export function useAnalysisExecution({
  activeHistoryIdx,
  activeMethodKey,
  activeMethodMeta,
  currentOptionValues,
  currentResults,
  currentSlotValues,
  executing,
  handleTrackedJobProgress,
  historyItems,
  mapStoredResults,
  sessionId,
  syncResultContext,
}) {
  function buildExecutionParams() {
    const params = {}

    for (const [key, value] of Object.entries(currentSlotValues.value || {})) {
      if (Array.isArray(value) && value.length === 1) {
        const slot = activeMethodMeta.value?.slots.find(item => item.key === key)
        params[key] = slot?.type === 'single' ? value[0] : value
      } else {
        params[key] = value
      }
    }

    for (const [key, value] of Object.entries(currentOptionValues.value || {})) {
      params[key] = value
    }

    return params
  }

  async function refreshHistoryFromServer() {
    const resultData = await api.getResults(sessionId.value)
    syncResultContext(resultData)
    historyItems.value = mapStoredResults(resultData.results || [])
  }

  function prependLocalHistoryResults() {
    for (const result of currentResults.value) {
      historyItems.value.unshift({
        name: result.name,
        method: activeMethodKey.value,
        dataset_version_id: result.dataset_version_id || null,
        dataset_version_no: result.dataset_version_no || null,
        created_at: result.created_at || null,
        results: [result],
      })
    }
  }

  function activateLatestHistoryResult() {
    if (historyItems.value.length) {
      activeHistoryIdx.value = 0
      currentResults.value = historyItems.value[0].results || []
    } else {
      activeHistoryIdx.value = -1
    }
  }

  async function executeCurrentMethod() {
    if (!activeMethodKey.value || executing.value) return
    if (activeMethodMeta.value?.reserved) return

    executing.value = true
    currentResults.value = []

    try {
      const response = await api.executeMethod(
        sessionId.value,
        activeMethodKey.value,
        buildExecutionParams(),
        { onProgress: handleTrackedJobProgress },
      )
      if (response.job) handleTrackedJobProgress(response.job)
      if (!response.success) {
        alert('分析失败: ' + (response.error || '未知错误'))
        return
      }

      currentResults.value = response.results || []
      try {
        await refreshHistoryFromServer()
      } catch (_) {
        prependLocalHistoryResults()
      }
      activateLatestHistoryResult()
    } catch (e) {
      alert('执行失败: ' + e.message)
    } finally {
      executing.value = false
    }
  }

  return {
    executeCurrentMethod,
  }
}
