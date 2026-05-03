import { ref } from 'vue'
import * as api from '../../api.js'

const FOLDERS_KEY = 'spssgo_folders'

export function useDatasetLibrary({
  activeHistoryIdx,
  activeMethodKey,
  confirmDialog,
  currentDatasetVersionId,
  currentDatasetVersionNo,
  currentResults,
  dataFileName,
  hasData,
  historyItems,
  mapStoredResults,
  sessionId,
  totalRows,
  variables,
}) {
  const allDataSets = ref([])
  const folders = ref(loadFolders())

  function loadFolders() {
    try { return JSON.parse(localStorage.getItem(FOLDERS_KEY)) || [] } catch (_) { return [] }
  }

  function saveFolders() {
    localStorage.setItem(FOLDERS_KEY, JSON.stringify(folders.value))
  }

  function onCreateFolder(name) {
    folders.value.push({ id: Date.now().toString(36), name, sessionIds: [] })
    saveFolders()
  }

  function onDeleteFolder(folderId) {
    const folder = folders.value.find(item => item.id === folderId)
    confirmDialog.visible = true
    confirmDialog.title = '删除文件夹'
    confirmDialog.message = '确认删除文件夹「' + ((folder && folder.name) || '') + '」吗？文件夹内的数据不会被删除，只会移出该文件夹。'
    confirmDialog.type = 'folder'
    confirmDialog.targetId = folderId
  }

  function onRenameFolder(folderId, newName) {
    const folder = folders.value.find(item => item.id === folderId)
    if (folder) {
      folder.name = newName
      saveFolders()
    }
  }

  function onMoveToFolder(targetSessionId, folderId) {
    for (const folder of folders.value) {
      folder.sessionIds = folder.sessionIds.filter(item => item !== targetSessionId)
    }
    if (folderId) {
      const target = folders.value.find(item => item.id === folderId)
      if (target) target.sessionIds.push(targetSessionId)
    }
    saveFolders()
  }

  async function onRenameDataSet(sid, newName) {
    try {
      await api.renameSession(sid, newName)
      const dataSet = allDataSets.value.find(item => item.sessionId === sid)
      if (dataSet) dataSet.topic = newName
    } catch (_) { /* ignore */ }
  }

  async function loadAllDataSets() {
    try {
      const data = await api.getSessions()
      const sessions = data.sessions || []
      const results = await Promise.all(
        sessions.map(session => api.getFiles(session.id).then(files => {
          const dataFiles = files.data_files || []
          return {
            sessionId: session.id,
            fileName: dataFiles.length > 0 ? dataFiles[0].name : '',
            createdAt: session.created_at,
            topic: session.research_topic || '',
            isCurrent: session.id === sessionId.value,
            hasData: dataFiles.length > 0,
          }
        }).catch(() => null))
      )
      allDataSets.value = results.filter(item => item && item.hasData)
      for (const dataSet of allDataSets.value) {
        dataSet.isCurrent = dataSet.sessionId === sessionId.value
      }
    } catch (_) { /* ignore */ }
  }

  async function switchSession(sid) {
    if (sid === sessionId.value) return

    let newHasData = false
    let newFileName = ''
    let newVars = []
    let newTotalRows = 0
    let newHistory = []
    let newCurrentDatasetVersionId = null
    let newCurrentDatasetVersionNo = null

    try {
      const [files, resData, varsData] = await Promise.all([
        api.getFiles(sid),
        api.getResults(sid),
        api.getVariables(sid).catch(() => ({ variables: [], total_rows: 0 })),
      ])

      const dataFiles = files.data_files || []
      if (dataFiles.length > 0) {
        newHasData = true
        newFileName = dataFiles[0].name
        newVars = varsData.variables || []
        newTotalRows = varsData.total_rows || 0
      }

      const dbResults = resData.results || []
      newCurrentDatasetVersionId = resData.current_dataset_version_id || null
      newCurrentDatasetVersionNo = resData.current_dataset_version_no || null
      if (dbResults.length) {
        newHistory = mapStoredResults(dbResults)
      }
    } catch (_) { /* ignore */ }

    sessionId.value = sid
    localStorage.setItem('spssgo_session_id', sid)
    hasData.value = newHasData
    dataFileName.value = newFileName
    variables.value = newVars
    totalRows.value = newTotalRows
    historyItems.value = newHistory
    activeHistoryIdx.value = -1
    currentResults.value = []
    currentDatasetVersionId.value = newCurrentDatasetVersionId
    currentDatasetVersionNo.value = newCurrentDatasetVersionNo
    activeMethodKey.value = ''

    for (const dataSet of allDataSets.value) {
      dataSet.isCurrent = dataSet.sessionId === sid
    }
  }

  async function onDeleteDataSet(sid) {
    const dataSet = allDataSets.value.find(item => item.sessionId === sid)
    confirmDialog.visible = true
    confirmDialog.title = '删除数据'
    confirmDialog.message = '确认删除数据「' + ((dataSet && (dataSet.topic || dataSet.fileName)) || '') + '」吗？删除后不可恢复。'
    confirmDialog.type = 'dataset'
    confirmDialog.targetId = sid
  }

  async function onExportDataSet(sid) {
    const dataSet = allDataSets.value.find(item => item.sessionId === sid)
    const name = dataSet ? (dataSet.topic || dataSet.fileName || 'data.xlsx') : 'data.xlsx'
    try {
      const buf = await api.getDataFileBuffer(sid)
      const blob = new Blob([buf])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('导出失败: ' + e.message)
    }
  }

  async function onCopyDataSet(sid) {
    const dataSet = allDataSets.value.find(item => item.sessionId === sid)
    const fileName = dataSet ? (dataSet.topic || dataSet.fileName || 'data.xlsx') : 'data.xlsx'
    try {
      const buf = await api.getDataFileBuffer(sid)
      const blob = new Blob([buf])
      const file = new File([blob], fileName, { type: blob.type || 'application/octet-stream' })
      const data = await api.createSession()
      const newSid = data.session_id
      await api.uploadFile(newSid, file)
      if (dataSet && dataSet.topic) {
        await api.renameSession(newSid, dataSet.topic + ' 副本').catch(() => {})
      }
      await loadAllDataSets()
    } catch (e) {
      alert('复制失败: ' + e.message)
    }
  }

  return {
    allDataSets,
    folders,
    loadAllDataSets,
    onCopyDataSet,
    onCreateFolder,
    onDeleteDataSet,
    onDeleteFolder,
    onExportDataSet,
    onMoveToFolder,
    onRenameDataSet,
    onRenameFolder,
    saveFolders,
    switchSession,
  }
}
