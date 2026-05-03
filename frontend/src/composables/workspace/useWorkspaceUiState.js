import { watch } from 'vue'

export function useWorkspaceUiState({
  activeHistoryIdx,
  activeMethodKey,
  aiRef,
  analysisReportVisible,
  clearCurrentAnalysis,
  currentResults,
  selectedVars,
  taskCenterOpen,
}) {
  function resetSelectedVars() {
    if (selectedVars.value.length) {
      selectedVars.value = []
    }
  }

  watch(activeMethodKey, (nextKey, prevKey) => {
    if (nextKey !== prevKey) {
      resetSelectedVars()
    }
  })

  function onSelectMethod(key) {
    activeMethodKey.value = key
    currentResults.value = []
    activeHistoryIdx.value = -1
    analysisReportVisible.value = false
  }

  function onNewAnalysis() {
    clearCurrentAnalysis()
  }

  function toggleAi() {
    if (aiRef.value) {
      aiRef.value.open = !aiRef.value.open
    }
  }

  function toggleTaskCenter() {
    taskCenterOpen.value = !taskCenterOpen.value
  }

  return {
    onNewAnalysis,
    onSelectMethod,
    toggleAi,
    toggleTaskCenter,
  }
}
