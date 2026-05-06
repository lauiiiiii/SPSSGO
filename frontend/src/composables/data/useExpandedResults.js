import { computed, ref, watch } from 'vue'
import { buildVariableMetaMap, createResultDisplayFormatter } from '../../utils/resultDisplay.js'

export function useExpandedResults(props, historyItemsSource = null) {
  const expandedResultIdx = ref(-1)
  const historyItems = computed(() => historyItemsSource?.value || props.historyItems)

  const expandedResult = computed(() => {
    if (expandedResultIdx.value < 0 || expandedResultIdx.value >= historyItems.value.length) return null
    return historyItems.value[expandedResultIdx.value]
  })

  const variableMetaMap = computed(() => buildVariableMetaMap(props.variables))
  const resultDisplayFormatter = computed(() => createResultDisplayFormatter(variableMetaMap.value))
  const displayExpandedResults = computed(() => {
    const list = expandedResult.value?.results || []
    return list.map(resultDisplayFormatter.value.normalizeResult)
  })

  watch(() => props.currentSessionId, () => {
    expandedResultIdx.value = -1
  })
  watch(historyItems, () => {
    expandedResultIdx.value = -1
  })

  function toggleResult(index) {
    expandedResultIdx.value = expandedResultIdx.value === index ? -1 : index
  }

  function closeExpandedResult() {
    expandedResultIdx.value = -1
  }

  return {
    closeExpandedResult,
    displayExpandedResults,
    expandedResult,
    expandedResultIdx,
    toggleResult,
  }
}
