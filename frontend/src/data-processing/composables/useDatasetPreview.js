import { computed, onMounted, ref, watch } from 'vue'
import * as api from '../../api.js'

export const PREVIEW_LIMIT_OPTIONS = [100, 500, 1000]

export function useDatasetPreview(props, viewMode) {
  const previewHeaders = ref([])
  const previewRows = ref([])
  const previewLoading = ref(false)
  const previewLimit = ref(PREVIEW_LIMIT_OPTIONS[0])
  const previewMeta = ref({
    datasetVersionId: null,
    datasetVersionNo: null,
    totalRows: 0,
  })

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

  const previewedRowCount = computed(() => previewRows.value.length)

  function createPreviewSnapshot(versionNo = previewMeta.value.datasetVersionNo) {
    return {
      headers: [...previewHeaders.value],
      rows: previewRows.value.map(row => [...row]),
      displayHeaders: [...displayHeaders.value],
      datasetVersionId: previewMeta.value.datasetVersionId,
      datasetVersionNo: versionNo,
      limit: previewLimit.value,
    }
  }

  async function loadPreview() {
    if (!props.sessionId || !props.hasData) return
    previewLoading.value = true
    try {
      const data = await api.getDataPreview(props.sessionId, previewLimit.value)
      previewHeaders.value = data.headers || []
      previewRows.value = data.rows || []
      previewMeta.value = {
        datasetVersionId: data.dataset_version_id || null,
        datasetVersionNo: data.dataset_version_no || null,
        totalRows: Number(data.total_rows || 0),
      }
    } catch (_) {
      previewHeaders.value = []
      previewRows.value = []
      previewMeta.value = {
        datasetVersionId: null,
        datasetVersionNo: null,
        totalRows: 0,
      }
    }
    previewLoading.value = false
  }

  async function setPreviewLimit(limit) {
    const nextLimit = PREVIEW_LIMIT_OPTIONS.includes(Number(limit))
      ? Number(limit)
      : PREVIEW_LIMIT_OPTIONS[0]
    if (previewLimit.value === nextLimit) return
    previewLimit.value = nextLimit
    await loadPreview()
  }

  onMounted(loadPreview)
  watch(() => props.sessionId, loadPreview)
  watch(() => props.hasData, (hasData) => {
    if (hasData) loadPreview()
    else {
      previewHeaders.value = []
      previewRows.value = []
      previewMeta.value = {
        datasetVersionId: null,
        datasetVersionNo: null,
        totalRows: 0,
      }
    }
  })

  return {
    createPreviewSnapshot,
    displayHeaders,
    displayRows,
    loadPreview,
    previewHeaders,
    previewLimit,
    previewLoading,
    previewMeta,
    previewRows,
    previewedRowCount,
    setPreviewLimit,
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
