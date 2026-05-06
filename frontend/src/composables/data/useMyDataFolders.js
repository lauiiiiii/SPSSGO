import { computed, nextTick, onUnmounted, reactive, ref, watch } from 'vue'

export function useMyDataFolders(props, emit, options = {}) {
  const openFolders = reactive({})
  const showNewFolder = ref(false)
  const newFolderName = ref('')
  const newFolderInput = ref(null)
  const renamingDsId = ref('')
  const renamingFolderId = ref('')
  const renamingValue = ref('')
  const ungroupedDropActive = ref(false)
  const activeFolderDropId = ref('')
  let folderAutoOpenTimer = null

  const contextMenu = reactive({
    visible: false,
    x: 0,
    y: 0,
    type: '',
    target: null,
    inFolder: false,
  })

  const allInFolders = computed(() => {
    const set = new Set()
    for (const folder of props.folders) {
      for (const sessionId of folder.sessionIds) set.add(sessionId)
    }
    return set
  })

  const ungroupedDataSets = computed(() => (
    visibleDataSets.value.filter(dataSet => !allInFolders.value.has(dataSet.sessionId))
  ))

  const visibleDataSets = computed(() => options.allDataSets?.value || props.allDataSets)

  watch(showNewFolder, (visible) => {
    if (visible) nextTick(() => { newFolderInput.value?.focus() })
  })

  function folderDataSets(folder) {
    const sessionIds = new Set(folder.sessionIds)
    return visibleDataSets.value.filter(dataSet => sessionIds.has(dataSet.sessionId))
  }

  function toggleFolder(id) {
    const wasOpen = openFolders[id]
    // 手风琴效果：展开当前时关闭其他已打开的文件夹
    for (const key in openFolders) {
      openFolders[key] = false
    }
    openFolders[id] = !wasOpen
  }

  function scheduleFolderAutoOpen(folderId) {
    clearFolderAutoOpen()
    folderAutoOpenTimer = setTimeout(() => {
      openFolders[folderId] = true
      folderAutoOpenTimer = null
    }, 500)
  }

  function clearFolderAutoOpen() {
    if (folderAutoOpenTimer) {
      clearTimeout(folderAutoOpenTimer)
      folderAutoOpenTimer = null
    }
  }

  function confirmNewFolder() {
    const name = newFolderName.value.trim()
    if (name) emit('create-folder', name)
    newFolderName.value = ''
    showNewFolder.value = false
  }

  function openDsMenu(event, dataSet, inFolder) {
    contextMenu.visible = true
    contextMenu.x = event.clientX
    contextMenu.y = event.clientY
    contextMenu.type = 'ds'
    contextMenu.target = dataSet
    contextMenu.inFolder = !!inFolder
  }

  function openDsMenuByButton(event, dataSet, inFolder) {
    const rect = event.currentTarget.getBoundingClientRect()
    openDsMenu({
      clientX: rect.right - 180,
      clientY: rect.bottom + 8,
    }, dataSet, inFolder)
  }

  function openFolderMenu(event, folder) {
    contextMenu.visible = true
    contextMenu.x = event.clientX
    contextMenu.y = event.clientY
    contextMenu.type = 'folder'
    contextMenu.target = folder
  }

  function closeMenu() {
    contextMenu.visible = false
  }

  function focusRenameInput() {
    nextTick(() => {
      const el = document.querySelector('.md-card-input')
      if (el) {
        el.focus()
        el.select()
      }
    })
  }

  function startRenameDs() {
    renamingDsId.value = contextMenu.target.sessionId
    renamingValue.value = contextMenu.target.topic || contextMenu.target.fileName
    contextMenu.visible = false
    focusRenameInput()
  }

  function confirmRenameDs(dataSet) {
    const name = renamingValue.value.trim()
    if (name && name !== (dataSet.topic || dataSet.fileName)) {
      emit('rename-dataset', dataSet.sessionId, name)
    }
    renamingDsId.value = ''
  }

  function startRenameFolder() {
    renamingFolderId.value = contextMenu.target.id
    renamingValue.value = contextMenu.target.name
    contextMenu.visible = false
    focusRenameInput()
  }

  function confirmRenameFolder() {
    const name = renamingValue.value.trim()
    if (name) emit('rename-folder', renamingFolderId.value, name)
    renamingFolderId.value = ''
  }

  function deleteFolder() {
    emit('delete-folder', contextMenu.target.id)
    contextMenu.visible = false
  }

  function moveDsToFolder(folderId) {
    emit('move-to-folder', contextMenu.target.sessionId, folderId)
    contextMenu.visible = false
  }

  function onDragStart(event, sessionId) {
    event.dataTransfer.setData('text/plain', sessionId)
    event.dataTransfer.effectAllowed = 'move'
  }

  function onDropToFolder(event, folderId) {
    const sessionId = event.dataTransfer.getData('text/plain')
    if (sessionId) emit('move-to-folder', sessionId, folderId)
  }

  function onFolderCardDragOver(folderId) {
    activeFolderDropId.value = folderId
    if (!openFolders[folderId]) scheduleFolderAutoOpen(folderId)
  }

  function onFolderCardDragLeave(event, folderId) {
    clearFolderAutoOpen()
    if (!event.currentTarget.contains(event.relatedTarget) && activeFolderDropId.value === folderId) {
      activeFolderDropId.value = ''
    }
  }

  function onDropToFolderCard(event, folderId) {
    clearFolderAutoOpen()
    activeFolderDropId.value = ''
    onDropToFolder(event, folderId)
  }

  function onFolderBodyDragOver(folderId) {
    clearFolderAutoOpen()
    activeFolderDropId.value = folderId
  }

  function onFolderBodyDragLeave(event, folderId) {
    if (!event.currentTarget.contains(event.relatedTarget) && activeFolderDropId.value === folderId) {
      activeFolderDropId.value = ''
    }
  }

  function onDropToFolderBody(event, folderId) {
    clearFolderAutoOpen()
    activeFolderDropId.value = ''
    onDropToFolder(event, folderId)
  }

  function onUngroupedDragOver() {
    ungroupedDropActive.value = true
  }

  function onUngroupedDragLeave(event) {
    if (!event.currentTarget.contains(event.relatedTarget)) {
      ungroupedDropActive.value = false
    }
  }

  function onDropToUngrouped(event) {
    clearFolderAutoOpen()
    ungroupedDropActive.value = false
    const sessionId = event.dataTransfer.getData('text/plain')
    if (sessionId) emit('move-to-folder', sessionId, '')
  }

  onUnmounted(clearFolderAutoOpen)

  return {
    activeFolderDropId,
    closeMenu,
    confirmNewFolder,
    confirmRenameDs,
    confirmRenameFolder,
    contextMenu,
    deleteFolder,
    folderDataSets,
    moveDsToFolder,
    newFolderInput,
    newFolderName,
    onDragStart,
    onDropToFolderBody,
    onDropToFolderCard,
    onDropToUngrouped,
    onFolderBodyDragLeave,
    onFolderBodyDragOver,
    onFolderCardDragLeave,
    onFolderCardDragOver,
    onUngroupedDragLeave,
    onUngroupedDragOver,
    openDsMenu,
    openDsMenuByButton,
    openFolderMenu,
    openFolders,
    renamingDsId,
    renamingFolderId,
    renamingValue,
    showNewFolder,
    startRenameDs,
    startRenameFolder,
    toggleFolder,
    ungroupedDataSets,
    ungroupedDropActive,
  }
}
