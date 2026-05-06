import { onMounted } from 'vue'
import { normalizeMethodMetaMap } from '../../data/methodMetaDefaults.js'
import * as api from '../../api.js'

export function useAppBootstrap({
  hasData,
  dataFileName,
  historyItems,
  loadAllDataSets,
  loadFolderDataSets,
  mapStoredResults,
  methodCategories,
  methodsMeta,
  sessionId,
  startTaskJobPolling,
  syncResultContext,
  totalRows,
  variables,
}) {
  const SESSION_KEY = 'spssgo_session_id'

  async function loadVariables() {
    if (!sessionId.value) return
    try {
      const data = await api.getVariables(sessionId.value)
      variables.value = data.variables || []
      totalRows.value = data.total_rows || 0
    } catch (e) {
      console.error('加载变量失败', e)
    }
  }

  async function loadMethods() {
    try {
      const data = await api.getMethods()
      methodsMeta.value = normalizeMethodMetaMap(data.methods || {})
      methodCategories.value = data.categories || []
    } catch (e) {
      console.error('加载方法列表失败', e)
    }
  }

  async function restoreSavedSession() {
    const savedSessionId = localStorage.getItem(SESSION_KEY)
    if (!savedSessionId) return

    try {
      const files = await api.getFiles(savedSessionId)
      const dataFiles = files.data_files || []
      sessionId.value = savedSessionId

      if (dataFiles.length > 0) {
        hasData.value = true
        dataFileName.value = dataFiles[0].name
        await loadVariables()
      }

      try {
        const resultData = await api.getResults(savedSessionId)
        syncResultContext(resultData)
        const storedResults = resultData.results || []
        if (storedResults.length) {
          historyItems.value = mapStoredResults(storedResults)
        }
      } catch (_) { /* ignore */ }
    } catch (_) {
      localStorage.removeItem(SESSION_KEY)
    }
  }

  onMounted(async () => {
    if (!api.checkAuth()) return
    await loadMethods()
    await restoreSavedSession()
    await loadAllDataSets()
    if (loadFolderDataSets) await loadFolderDataSets()
    startTaskJobPolling()
  })

  return {
    loadVariables,
    sessionStorageKey: SESSION_KEY,
  }
}
