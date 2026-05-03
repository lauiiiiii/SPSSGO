import { reactive } from 'vue'
import * as api from '../../api.js'

export function useProcessingVariableActions(props, {
  dialogSelectedVars,
  emit,
  loadPreview,
  loadVersions,
  notifySuccess,
}) {
  const varMenu = reactive({
    visible: false,
    x: 0,
    y: 0,
    target: null,
  })

  function closeVarMenu() {
    varMenu.visible = false
    varMenu.target = null
  }

  function toggleVarMenu(event, variable) {
    if (varMenu.visible && varMenu.target?.name === variable.name) {
      closeVarMenu()
      return
    }
    const rect = event.currentTarget.getBoundingClientRect()
    varMenu.visible = true
    varMenu.target = variable
    varMenu.x = rect.right + 8
    varMenu.y = rect.top - 4
  }

  function handleGlobalClick() {
    closeVarMenu()
  }

  async function handleVarTypeToggle() {
    if (!props.sessionId || !varMenu.target) return
    const targetType = varMenu.target.type === 'numeric' ? 'categorical' : 'numeric'
    try {
      const data = await api.changeVariableType(props.sessionId, varMenu.target.name, targetType)
      notifySuccess(data.message || '变量类型已更新')
      closeVarMenu()
      emit('variables-updated')
      await loadVersions()
    } catch (e) {
      alert('变量类型转换失败: ' + e.message)
    }
  }

  async function handleVarRename() {
    if (!props.sessionId || !varMenu.target) return
    const newName = window.prompt('请输入新的变量名', varMenu.target.name)
    if (newName == null) return
    const trimmed = newName.trim()
    if (!trimmed || trimmed === varMenu.target.name) {
      closeVarMenu()
      return
    }
    try {
      const oldName = varMenu.target.name
      const data = await api.renameVariable(props.sessionId, oldName, trimmed)
      if (dialogSelectedVars.value.includes(oldName)) {
        dialogSelectedVars.value = dialogSelectedVars.value.map(name => name === oldName ? trimmed : name)
      }
      notifySuccess(data.message || '变量已重命名')
      closeVarMenu()
      emit('variables-updated')
      await loadVersions()
      await loadPreview()
    } catch (e) {
      alert('变量重命名失败: ' + e.message)
    }
  }

  async function handleVarDelete() {
    if (!props.sessionId || !varMenu.target) return
    const targetName = varMenu.target.name
    if (!window.confirm(`确认删除变量“${targetName}”吗？删除后不可恢复。`)) return
    try {
      const data = await api.deleteVariable(props.sessionId, targetName)
      dialogSelectedVars.value = dialogSelectedVars.value.filter(name => name !== targetName)
      notifySuccess(data.message || '变量已删除')
      closeVarMenu()
      emit('variables-updated')
      await loadVersions()
      await loadPreview()
    } catch (e) {
      alert('删除变量失败: ' + e.message)
    }
  }

  return {
    closeVarMenu,
    handleGlobalClick,
    handleVarDelete,
    handleVarRename,
    handleVarTypeToggle,
    toggleVarMenu,
    varMenu,
  }
}
