export function useHistorySelection({
  activeHistoryIdx,
  activeMethodKey,
  analysisReportVisible,
  currentResults,
  historyItems,
  inferMethodKeyFromName,
  methodsMeta,
}) {
  function applyHistoryItem(idx) {
    activeHistoryIdx.value = idx
    const item = historyItems.value[idx]
    if (!item) return

    currentResults.value = item.results ? item.results.slice() : []
    const methodKey = item.method || inferMethodKeyFromName(item.name)
    if (methodKey && methodsMeta.value[methodKey]) {
      activeMethodKey.value = methodKey
    }
    analysisReportVisible.value = currentResults.value.length > 0
  }

  function clearHistorySelection() {
    activeHistoryIdx.value = -1
    currentResults.value = []
    analysisReportVisible.value = false
  }

  function removeHistoryItemAt(targetIndex) {
    historyItems.value.splice(targetIndex, 1)

    if (!historyItems.value.length) {
      clearHistorySelection()
      return
    }

    if (activeHistoryIdx.value === targetIndex) {
      applyHistoryItem(Math.min(targetIndex, historyItems.value.length - 1))
      return
    }

    if (activeHistoryIdx.value > targetIndex) {
      activeHistoryIdx.value -= 1
    }
  }

  return {
    applyHistoryItem,
    clearHistorySelection,
    removeHistoryItemAt,
  }
}
