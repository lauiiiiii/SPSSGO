import * as api from '../../api.js'

export function useVariableActions({
  sessionId,
  selectedVars,
  loadVariables,
  loadAllDataSets,
  setDatasetVersion,
}) {
  function getSessionId() {
    return typeof sessionId === 'function' ? sessionId() : sessionId?.value
  }

  function applySelectedVarsRename(renameMap) {
    if (!selectedVars?.value || !renameMap.size) return
    selectedVars.value = selectedVars.value.map(name => renameMap.get(name) || name)
  }

  async function refreshAfterMutation(result) {
    setDatasetVersion?.(result)
    await loadVariables?.()
    await loadAllDataSets?.()
  }

  async function changeType(varName, targetType) {
    const sid = getSessionId()
    if (!sid || !varName) return
    try {
      const result = await api.changeVariableType(sid, varName, targetType)
      await refreshAfterMutation(result)
    } catch (e) {
      alert('变量类型修改失败: ' + e.message)
    }
  }

  async function deleteVariable(varName) {
    const sid = getSessionId()
    if (!sid || !varName) return
    if (!confirm(`确认删除变量「${varName}」吗？删除后会生成新的数据版本。`)) return
    try {
      const result = await api.deleteVariable(sid, varName)
      if (selectedVars?.value) {
        selectedVars.value = selectedVars.value.filter(name => name !== varName)
      }
      await refreshAfterMutation(result)
    } catch (e) {
      alert('删除变量失败: ' + e.message)
    }
  }

  async function renameVariable(oldName, newName) {
    const sid = getSessionId()
    if (!sid || !oldName || !newName || oldName === newName) return
    try {
      const result = await api.renameVariable(sid, oldName, newName)
      applySelectedVarsRename(new Map([[oldName, newName]]))
      await refreshAfterMutation(result)
    } catch (e) {
      alert('变量重命名失败: ' + e.message)
    }
  }

  async function renameBatch(changes) {
    const sid = getSessionId()
    if (!sid || !Array.isArray(changes) || !changes.length) return
    const renameMap = new Map()
    try {
      let latestResult = null
      for (const change of changes) {
        const oldName = String(change.oldName || '').trim()
        const newName = String(change.newName || '').trim()
        if (!oldName || !newName || oldName === newName) continue
        latestResult = await api.renameVariable(sid, oldName, newName)
        renameMap.set(oldName, newName)
      }
      if (renameMap.size) {
        applySelectedVarsRename(renameMap)
        await refreshAfterMutation(latestResult)
      }
    } catch (e) {
      await loadVariables?.()
      alert('批量命名失败: ' + e.message)
    }
  }

  return {
    changeType,
    deleteVariable,
    renameVariable,
    renameBatch,
  }
}
