import { ref, watch } from 'vue'

export function useAnalysisViewState(props, emit, { resetAiInterpretation, resetCharts }) {
  const editingConfig = ref(false)

  function editConfig() {
    editingConfig.value = true
  }

  function showReport() {
    editingConfig.value = false
  }

  watch(() => props.results, (nextResults) => {
    if (nextResults?.length) {
      editingConfig.value = false
      resetAiInterpretation()
      resetCharts()
    }
  })

  function emitReportView() {
    const open = !!(props.results?.length && !props.executing && !editingConfig.value)
    emit('report-view', open)
  }
  watch([() => props.results, () => props.executing, editingConfig], emitReportView, { immediate: true })

  watch(() => [props.method, props.methodKey], () => {
    editingConfig.value = false
    resetAiInterpretation()
  }, { immediate: true })

  return {
    editConfig,
    editingConfig,
    showReport,
  }
}
