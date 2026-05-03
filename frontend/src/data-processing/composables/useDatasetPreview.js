import { computed, onMounted, ref, watch } from 'vue'
import * as api from '../../api.js'

export function useDatasetPreview(props, viewMode) {
  const previewHeaders = ref([])
  const previewRows = ref([])
  const previewLoading = ref(false)

  const variableMetaMap = computed(() => {
    const map = {}
    for (const variable of props.variables) {
      map[variable.name] = variable
    }
    return map
  })

  const displayHeaders = computed(() => previewHeaders.value.map(header => {
    const variable = variableMetaMap.value[header]
    return variable?.display_name || header
  }))

  const displayRows = computed(() => {
    if (viewMode.value === 'code') return previewRows.value
    return previewRows.value.map(row => row.map((cell, index) => {
      const header = previewHeaders.value[index]
      return formatPreviewCell(variableMetaMap.value[header], cell)
    }))
  })

  async function loadPreview() {
    if (!props.sessionId || !props.hasData) return
    previewLoading.value = true
    try {
      const data = await api.getDataPreview(props.sessionId)
      previewHeaders.value = data.headers || []
      previewRows.value = data.rows || []
    } catch (_) {
      previewHeaders.value = []
      previewRows.value = []
    }
    previewLoading.value = false
  }

  onMounted(loadPreview)
  watch(() => props.sessionId, loadPreview)
  watch(() => props.hasData, (hasData) => {
    if (hasData) loadPreview()
  })

  return {
    displayHeaders,
    displayRows,
    loadPreview,
    previewHeaders,
    previewLoading,
    previewRows,
    variableMetaMap,
  }
}

function formatPreviewCell(variable, cell) {
  const valueLabels = variable?.value_labels || {}
  if (!valueLabels || cell === '' || cell == null) return cell

  const direct = valueLabels[String(cell)]
  if (direct) return direct

  const numeric = Number(cell)
  if (!Number.isNaN(numeric)) {
    const numericKey = String(Number.isInteger(numeric) ? numeric : numeric)
    if (valueLabels[numericKey]) return valueLabels[numericKey]
    const floatKey = String(numeric.toFixed(1))
    if (valueLabels[floatKey]) return valueLabels[floatKey]
  }
  return cell
}
