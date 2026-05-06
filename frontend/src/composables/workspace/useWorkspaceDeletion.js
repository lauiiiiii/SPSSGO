import * as api from '../../api.js'

export function useWorkspaceDeletion({
  allDataSets,
  closeConfirmDialog,
  confirmDialog,
  confirmHistoryDelete,
  currentDatasetVersionId,
  currentDatasetVersionNo,
  currentResults,
  dataFileName,
  folders,
  hasData,
  historyItems,
  saveFolders,
  sessionId,
  sessionStorageKey,
  totalRows,
  variables,
}) {
  function clearCurrentSessionState() {
    sessionId.value = ''
    localStorage.removeItem(sessionStorageKey)
    hasData.value = false
    dataFileName.value = ''
    variables.value = []
    totalRows.value = 0
    currentDatasetVersionId.value = null
    currentDatasetVersionNo.value = null
    historyItems.value = []
    currentResults.value = []
  }

  async function deleteFolder(folderId) {
    try {
      await api.deleteDatasetFolder(folderId)
    } catch (err) {
      alert(`删除文件夹失败：${err.message || err}`)
      return
    }
    folders.value = folders.value.filter(folder => String(folder.id) !== String(folderId))
  }

  async function deleteDataset(targetId, targetDatasetId = null) {
    try {
      if (targetDatasetId) {
        await api.deleteDataset(targetDatasetId)
      } else {
        await api.deleteSession(targetId)
      }
    } catch (err) {
      alert(`删除数据失败：${err.message || err}`)
      return
    }

    allDataSets.value = allDataSets.value.filter(dataSet => dataSet.sessionId !== targetId)
    for (const folder of folders.value) {
      folder.sessionIds = folder.sessionIds.filter(session => session !== targetId)
    }
    await saveFolders()

    if (sessionId.value === targetId) {
      clearCurrentSessionState()
    }
  }

  async function confirmDeleteAction() {
    const type = confirmDialog.type
    const targetId = confirmDialog.targetId
    const targetDatasetId = confirmDialog.targetDatasetId
    const targetIndex = confirmDialog.targetIndex
    const suppressForHour = confirmDialog.suppressForHour
    closeConfirmDialog()

    if (type === 'folder') {
      await deleteFolder(targetId)
      return
    }

    if (type === 'dataset') {
      await deleteDataset(targetId, targetDatasetId)
      return
    }

    if (type === 'history') {
      await confirmHistoryDelete(targetId, targetIndex, suppressForHour)
    }
  }

  return {
    clearCurrentSessionState,
    confirmDeleteAction,
  }
}
