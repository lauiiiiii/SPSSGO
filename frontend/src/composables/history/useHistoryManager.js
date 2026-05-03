import { isHistoryDeleteSuppressed, setHistoryDeleteSuppressedForHour } from '../../utils/historyDeleteSuppression.js'
import { useHistorySelection } from './useHistorySelection.js'
import * as api from '../../api.js'

export function useHistoryManager({
  activeHistoryIdx,
  activeMethodKey,
  analysisReportVisible,
  closeRenameDialog,
  currentResults,
  findMethodKeyFromItem,
  historyItems,
  methodsMeta,
  openConfirmDialog,
  openRenameDialog,
  renameDialog,
  sessionId,
}) {
  const historySelection = useHistorySelection({
    activeHistoryIdx,
    activeMethodKey,
    analysisReportVisible,
    currentResults,
    historyItems,
    inferMethodKeyFromName: findMethodKeyFromItem,
    methodsMeta,
  })

  const {
    applyHistoryItem,
    removeHistoryItemAt,
  } = historySelection

  async function deleteHistoryItem(targetId, targetIndex) {
    try {
      if (targetId) {
        await api.deleteAnalysisResult(sessionId.value, targetId)
      }
      removeHistoryItemAt(targetIndex)
    } catch (e) {
      alert('删除失败: ' + e.message)
    }
  }

  function clearCurrentAnalysis() {
    activeHistoryIdx.value = -1
    currentResults.value = []
    analysisReportVisible.value = false
  }

  function activateLatestHistory() {
    if (!historyItems.value.length) {
      activeHistoryIdx.value = -1
      return
    }
    activeHistoryIdx.value = 0
    currentResults.value = historyItems.value[0].results ? historyItems.value[0].results.slice() : []
  }

  function syncMethodFromHistoryItem(item) {
    const methodKey = item?.method || findMethodKeyFromItem(item?.name)
    if (methodKey && methodsMeta.value[methodKey]) {
      activeMethodKey.value = methodKey
    }
  }

  function activateFirstHistoryWithMethod() {
    const item = historyItems.value[0]
    if (!item) return
    activateLatestHistory()
    syncMethodFromHistoryItem(item)
  }

  async function onRenameHistory(idx) {
    const item = historyItems.value[idx]
    if (!item) return
    openRenameDialog({
      title: '重命名分析结果',
      value: item.name || '',
      targetId: item.id || '',
      targetIndex: idx,
    })
  }

  async function onDeleteHistory(idx) {
    const item = historyItems.value[idx]
    if (!item) return
    if (isHistoryDeleteSuppressed()) {
      await deleteHistoryItem(item.id || '', idx)
      return
    }
    openConfirmDialog({
      title: '删除后不可恢复',
      message: '确认删除分析结果吗？',
      type: 'history',
      targetId: item.id || '',
      targetIndex: idx,
    })
  }

  async function submitRenameDialog() {
    const idx = renameDialog.targetIndex
    const item = historyItems.value[idx]
    const trimmed = String(renameDialog.value || '').trim()
    if (!item) {
      closeRenameDialog()
      return
    }
    if (!trimmed) return
    if (trimmed === item.name) {
      closeRenameDialog()
      return
    }

    try {
      if (renameDialog.targetId) {
        await api.renameAnalysisResult(sessionId.value, renameDialog.targetId, trimmed)
      }
      item.name = trimmed
      if (item.results?.length) {
        item.results[0].name = trimmed
      }
      if (activeHistoryIdx.value === idx) {
        currentResults.value = item.results ? item.results.slice() : []
      }
      closeRenameDialog()
    } catch (e) {
      alert('重命名失败: ' + e.message)
    }
  }

  async function confirmHistoryDelete(targetId, targetIndex, suppressForHour) {
    if (suppressForHour) setHistoryDeleteSuppressedForHour()
    await deleteHistoryItem(targetId, targetIndex)
  }

  return {
    ...historySelection,
    activateFirstHistoryWithMethod,
    activateLatestHistory,
    applyHistoryItem,
    clearCurrentAnalysis,
    confirmHistoryDelete,
    onDeleteHistory,
    onRenameHistory,
    submitRenameDialog,
    syncMethodFromHistoryItem,
  }
}
