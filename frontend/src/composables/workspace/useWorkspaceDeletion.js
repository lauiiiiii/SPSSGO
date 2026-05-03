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

  function deleteFolder(folderId) {
    folders.value = folders.value.filter(folder => folder.id !== folderId)
    saveFolders()
  }

  async function deleteDataset(targetId) {
    try {
      await api.deleteSession(targetId)
    } catch (_) { /* backend may not support, still remove from UI */ }

    allDataSets.value = allDataSets.value.filter(dataSet => dataSet.sessionId !== targetId)
    for (const folder of folders.value) {
      folder.sessionIds = folder.sessionIds.filter(session => session !== targetId)
    }
    saveFolders()

    if (sessionId.value === targetId) {
      clearCurrentSessionState()
    }
  }

  async function confirmDeleteAction() {
    const type = confirmDialog.type
    const targetId = confirmDialog.targetId
    const targetIndex = confirmDialog.targetIndex
    const suppressForHour = confirmDialog.suppressForHour
    closeConfirmDialog()

    if (type === 'folder') {
      deleteFolder(targetId)
      return
    }

    if (type === 'dataset') {
      await deleteDataset(targetId)
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
