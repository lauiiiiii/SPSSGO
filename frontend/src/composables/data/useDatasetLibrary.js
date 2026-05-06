import { ref } from 'vue'
import * as api from '../../api.js'

const LEGACY_FOLDERS_KEY = 'spssgo_folders'

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
  const folderDataSetsAll = ref([])
  const folders = ref([])
  const datasetTotal = ref(0)
  const datasetPage = ref(1)
  const datasetPageSize = ref(50)

  function findDataSetBySessionId(sid) {
    return allDataSets.value.find(item => item.sessionId === sid)
      || folderDataSetsAll.value.find(item => item.sessionId === sid)
      || null
  }

  async function loadFolders() {
    try {
      const data = await api.getDatasetFolders()
      folders.value = (data.folders || []).map(folder => ({
        id: folder.id,
        name: folder.name || '',
        createdAt: folder.created_at || null,
        sessionIds: folder.sessionIds || folder.session_ids || [],
      }))
      await migrateLegacyFoldersIfNeeded()
    } catch (_) { /* ignore */ }
  }

  function saveFolders() {
    return loadFolders()
  }

  async function onCreateFolder(name) {
    try {
      const data = await api.createDatasetFolder(name)
      if (data.folder) {
        folders.value.push({
          id: data.folder.id,
          name: data.folder.name || name,
          createdAt: data.folder.created_at || null,
          sessionIds: data.folder.sessionIds || [],
        })
      } else {
        await loadFolders()
      }
    } catch (e) {
      alert('创建文件夹失败: ' + e.message)
    }
  }

  function onDeleteFolder(folderId) {
    const folder = folders.value.find(item => String(item.id) === String(folderId))
    confirmDialog.visible = true
    confirmDialog.title = '删除文件夹'
    confirmDialog.message = '确认删除文件夹「' + ((folder && folder.name) || '') + '」吗？文件夹内的数据不会被删除，只会移出该文件夹。'
    confirmDialog.type = 'folder'
    confirmDialog.targetId = folderId
  }

  async function onRenameFolder(folderId, newName) {
    const folder = folders.value.find(item => String(item.id) === String(folderId))
    const previousName = folder?.name
    if (folder) folder.name = newName
    try {
      await api.renameDatasetFolder(folderId, newName)
    } catch (e) {
      if (folder) folder.name = previousName
      alert('重命名文件夹失败: ' + e.message)
    }
  }

  async function onMoveToFolder(targetSessionId, folderId) {
    const previousFolders = folders.value.map(folder => ({ ...folder, sessionIds: [...folder.sessionIds] }))
    for (const folder of folders.value) {
      folder.sessionIds = folder.sessionIds.filter(item => item !== targetSessionId)
    }
    if (folderId) {
      const target = folders.value.find(item => String(item.id) === String(folderId))
      if (target) target.sessionIds.push(targetSessionId)
    }
    try {
      await api.moveDatasetToFolder(targetSessionId, folderId || null)
      await Promise.all([loadAllDataSets(datasetPage.value, datasetPageSize.value), loadFolderDataSets()])
    } catch (e) {
      folders.value = previousFolders
      alert('移动数据集失败: ' + e.message)
    }
  }

  async function migrateLegacyFoldersIfNeeded() {
    if (folders.value.length) return
    let legacyFolders = []
    try {
      legacyFolders = JSON.parse(localStorage.getItem(LEGACY_FOLDERS_KEY) || '[]') || []
    } catch (_) {
      legacyFolders = []
    }
    if (!legacyFolders.length) return

    const migrated = []
    for (const legacy of legacyFolders) {
      const name = (legacy.name || '').trim()
      if (!name) continue
      const created = await api.createDatasetFolder(name)
      const folder = created.folder
      if (!folder?.id) continue
      const sessionIds = Array.isArray(legacy.sessionIds) ? legacy.sessionIds : []
      for (const legacySessionId of sessionIds) {
        await api.moveDatasetToFolder(legacySessionId, folder.id).catch(() => {})
      }
      migrated.push({
        id: folder.id,
        name: folder.name || name,
        createdAt: folder.created_at || null,
        sessionIds,
      })
    }
    folders.value = migrated
    localStorage.removeItem(LEGACY_FOLDERS_KEY)
  }

  async function onRenameDataSet(sid, newName) {
    try {
      const dataSet = findDataSetBySessionId(sid)
      if (dataSet?.datasetId) {
        await api.renameDataset(dataSet.datasetId, newName)
      } else {
        await api.renameSession(sid, newName)
      }
      if (dataSet) dataSet.topic = newName
    } catch (_) { /* ignore */ }
  }

  async function loadAllDataSets(page = datasetPage.value, pageSize = datasetPageSize.value) {
    try {
      const data = await api.getDatasets({ page, page_size: pageSize, in_folder: 0 })
      const datasets = data.datasets || []
      datasetTotal.value = data.total || 0
      datasetPage.value = data.page || page
      datasetPageSize.value = data.page_size || pageSize
      allDataSets.value = datasets.map(dataset => ({
        datasetId: dataset.id,
        sessionId: dataset.session_id,
        fileName: dataset.original_filename || '',
        createdAt: dataset.created_at,
        lastUsedAt: dataset.last_used_at || dataset.created_at,
        topic: dataset.name || '',
        isCurrent: dataset.session_id === sessionId.value,
        hasData: true,
        rowCount: dataset.row_count || 0,
        columnCount: dataset.column_count || 0,
        versionCount: dataset.version_count || 0,
        resultCount: dataset.result_count || 0,
        currentVersionNo: dataset.current_version_no || null,
        currentVersionId: dataset.current_version_id || null,
        fileSize: dataset.file_size || '',
      }))
      for (const dataSet of allDataSets.value) {
        dataSet.isCurrent = dataSet.sessionId === sessionId.value
      }
      await loadFolders()
    } catch (_) {
      datasetTotal.value = 0
      await loadAllDataSetsFromSessions()
    }
  }

  async function loadFolderDataSets() {
    try {
      const data = await api.getDatasets({ in_folder: 1, page_size: 500 })
      const datasets = data.datasets || []
      folderDataSetsAll.value = datasets.map(dataset => ({
        datasetId: dataset.id,
        sessionId: dataset.session_id,
        fileName: dataset.original_filename || '',
        createdAt: dataset.created_at,
        lastUsedAt: dataset.last_used_at || dataset.created_at,
        topic: dataset.name || '',
        isCurrent: dataset.session_id === sessionId.value,
        hasData: true,
        rowCount: dataset.row_count || 0,
        columnCount: dataset.column_count || 0,
        versionCount: dataset.version_count || 0,
        resultCount: dataset.result_count || 0,
        currentVersionNo: dataset.current_version_no || null,
        currentVersionId: dataset.current_version_id || null,
        fileSize: dataset.file_size || '',
        folderId: dataset.folder_id || null,
      }))
      for (const dataSet of folderDataSetsAll.value) {
        dataSet.isCurrent = dataSet.sessionId === sessionId.value
      }
    } catch (_) {
      folderDataSetsAll.value = []
    }
  }

  async function loadAllDataSetsFromSessions() {
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
            lastUsedAt: session.created_at,
            topic: session.research_topic || '',
            isCurrent: session.id === sessionId.value,
            hasData: dataFiles.length > 0,
          }
        }).catch(() => null))
      )
      allDataSets.value = results.filter(item => item && item.hasData)
      await loadFolders()
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
    for (const dataSet of folderDataSetsAll.value) {
      dataSet.isCurrent = dataSet.sessionId === sid
    }
    const activeDataSet = findDataSetBySessionId(sid)
    if (activeDataSet && activeDataSet.datasetId) {
      // 不实时更新 lastUsedAt，避免触发排序导致卡片位置跳动
      api.touchDataset(activeDataSet.datasetId).catch(() => {})
    }
  }

  async function onDeleteDataSet(sid) {
    const dataSet = findDataSetBySessionId(sid)
    confirmDialog.visible = true
    confirmDialog.title = '删除数据'
    confirmDialog.message = '确认删除数据「' + ((dataSet && (dataSet.topic || dataSet.fileName)) || '') + '」吗？删除后不可恢复。'
    confirmDialog.type = 'dataset'
    confirmDialog.targetId = sid
    confirmDialog.targetDatasetId = dataSet?.datasetId || null
  }

  async function onExportDataSet(sid) {
    const dataSet = findDataSetBySessionId(sid)
    const name = dataSet ? (dataSet.topic || dataSet.fileName || 'data.xlsx') : 'data.xlsx'
    try {
      const buf = await api.exportDataFileBuffer(sid, 'xlsx')
      const blob = new Blob([buf])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = buildCurrentVersionExportName(name, dataSet)
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('导出失败: ' + e.message)
    }
  }

  async function onCopyDataSet(sid) {
    const dataSet = findDataSetBySessionId(sid)
    const fileName = dataSet ? (dataSet.topic || dataSet.fileName || 'data.xlsx') : 'data.xlsx'
    try {
      const buf = await api.exportDataFileBuffer(sid, 'xlsx')
      const blob = new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const copyName = buildCurrentVersionExportName(fileName, dataSet)
      const file = new File([blob], copyName, { type: blob.type })
      const data = await api.createSession()
      const newSid = data.session_id
      const uploaded = await api.uploadFile(newSid, file)
      if (dataSet && dataSet.topic) {
        if (uploaded?.dataset_id) {
          await api.renameDataset(uploaded.dataset_id, `${dataSet.topic} 副本`).catch(() => {})
        } else {
          await api.renameSession(newSid, `${dataSet.topic} 副本`).catch(() => {})
        }
      }
      await loadAllDataSets()
    } catch (e) {
      alert('复制失败: ' + e.message)
    }
  }

  function buildCurrentVersionExportName(name, dataSet) {
    const base = String(name || 'data').replace(/\.[^.]+$/, '')
    const version = dataSet?.currentVersionNo ? `_v${dataSet.currentVersionNo}` : ''
    return `${base}${version}.xlsx`
  }

  return {
    allDataSets,
    datasetPage,
    datasetPageSize,
    datasetTotal,
    folderDataSetsAll,
    folders,
    loadAllDataSets,
    loadFolderDataSets,
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
