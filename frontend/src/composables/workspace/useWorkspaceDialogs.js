import { reactive } from 'vue'

export function useWorkspaceDialogs() {
  const confirmDialog = reactive({
    visible: false,
    title: '',
    message: '',
    type: '',
    context: '',
    targetId: '',
    targetDatasetId: null,
    targetIndex: -1,
    suppressForHour: false,
  })

  const renameDialog = reactive({
    visible: false,
    title: '',
    value: '',
    targetId: '',
    context: '',
    targetIndex: -1,
  })

  function closeConfirmDialog() {
    confirmDialog.visible = false
    confirmDialog.title = ''
    confirmDialog.message = ''
    confirmDialog.type = ''
    confirmDialog.context = ''
    confirmDialog.targetId = ''
    confirmDialog.targetDatasetId = null
    confirmDialog.targetIndex = -1
    confirmDialog.suppressForHour = false
  }

  function closeRenameDialog() {
    renameDialog.visible = false
    renameDialog.title = ''
    renameDialog.value = ''
    renameDialog.targetId = ''
    renameDialog.context = ''
    renameDialog.targetIndex = -1
  }

  function openConfirmDialog({ context = '', message, targetDatasetId = null, targetId = '', targetIndex = -1, title, type }) {
    confirmDialog.visible = true
    confirmDialog.title = title
    confirmDialog.message = message
    confirmDialog.type = type
    confirmDialog.context = context
    confirmDialog.targetId = targetId
    confirmDialog.targetDatasetId = targetDatasetId
    confirmDialog.targetIndex = targetIndex
    confirmDialog.suppressForHour = false
  }

  function openRenameDialog({ context = '', targetId = '', targetIndex = -1, title, value = '' }) {
    renameDialog.visible = true
    renameDialog.title = title
    renameDialog.value = value
    renameDialog.targetId = targetId
    renameDialog.context = context
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
