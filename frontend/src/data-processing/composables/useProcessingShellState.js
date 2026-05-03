import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

export function useProcessingShellState(props) {
  const viewMode = ref('code')
  const successMsg = ref('')

  const numericVars = computed(() => props.variables.filter(variable => variable.type === 'numeric'))
  const catVars = computed(() => props.variables.filter(variable => variable.type !== 'numeric'))

  function notifySuccess(message) {
    successMsg.value = message
    setTimeout(() => { successMsg.value = '' }, 3000)
  }

  return {
    catVars,
    notifySuccess,
    numericVars,
    successMsg,
    viewMode,
  }
}

export function useProcessingOverlayControls({ closeProcessingDialog, closeVarMenu, handleGlobalClick, openProcessingMethod }) {
  function closeDialogOverlays() {
    closeProcessingDialog()
    closeVarMenu()
  }

  function openMethod(key) {
    closeVarMenu()
    openProcessingMethod(key)
  }

  onMounted(() => {
    window.addEventListener('click', handleGlobalClick)
  })
  onBeforeUnmount(() => {
    window.removeEventListener('click', handleGlobalClick)
  })

  return {
    closeDialogOverlays,
    openMethod,
  }
}
