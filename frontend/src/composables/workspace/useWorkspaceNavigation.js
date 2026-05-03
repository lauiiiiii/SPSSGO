export function useWorkspaceNavigation({
  activateFirstHistoryWithMethod,
  applyHistoryItem,
  currentTab,
  sessionId,
  switchSession,
}) {
  function onTabChange(tab) {
    currentTab.value = tab
  }

  function onOpenResultFromMyData(idx) {
    currentTab.value = 'analysis'
    applyHistoryItem(idx)
  }

  async function onSwitchSession(sid) {
    await switchSession(sid)
  }

  async function onGoAnalysis(sid) {
    await switchSession(sid)
    currentTab.value = 'analysis'
    activateFirstHistoryWithMethod()
  }

  async function onGoProcessing(sid) {
    await switchSession(sid)
    currentTab.value = 'processing'
  }

  function resolveAnalysisSessionId(sid) {
    return sid || sessionId.value
  }

  return {
    onGoAnalysis,
    onGoProcessing,
    onOpenResultFromMyData,
    onSwitchSession,
    onTabChange,
    resolveAnalysisSessionId,
  }
}
