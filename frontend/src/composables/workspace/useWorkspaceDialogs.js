import { reactive } from 'vue'

export function useWorkspaceDialogs() {
  const confirmDialog = reactive({
    visible: false,
    title: '',
    message: '',
    type: '',
    targetId: '',
    targetIndex: -1,
    suppressForHour: false,
  })

  const renameDialog = reactive({
    visible: false,
    title: '',
    value: '',
    targetId: '',
    targetIndex: -1,
  })

  function closeConfirmDialog() {
    confirmDialog.visible = false
    confirmDialog.title = ''
    confirmDialog.message = ''
    confirmDialog.type = ''
    confirmDialog.targetId = ''
    confirmDialog.targetIndex = -1
    confirmDialog.suppressForHour = false
  }

  function closeRenameDialog() {
    renameDialog.visible = false
    renameDialog.title = ''
    renameDialog.value = ''
    renameDialog.targetId = ''
    renameDialog.targetIndex = -1
  }

  function openConfirmDialog({ message, targetId = '', targetIndex = -1, title, type }) {
    confirmDialog.visible = true
    confirmDialog.title = title
    confirmDialog.message = message
    confirmDialog.type = type
    confirmDialog.targetId = targetId
    confirmDialog.targetIndex = targetIndex
    confirmDialog.suppressForHour = false
  }

  function openRenameDialog({ targetId = '', targetIndex = -1, title, value = '' }) {
    renameDialog.visible = true
    renameDialog.title = title
    renameDialog.value = value
    renameDialog.targetId = targetId
    renameDialog.targetIndex = targetIndex
  }

  return {
    closeConfirmDialog,
    closeRenameDialog,
    confirmDialog,
    openConfirmDialog,
    openRenameDialog,
    renameDialog,
  }
}
