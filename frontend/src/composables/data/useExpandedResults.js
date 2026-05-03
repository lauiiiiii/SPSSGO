import { computed, ref, watch } from 'vue'
import { buildVariableMetaMap, createResultDisplayFormatter } from '../../utils/resultDisplay.js'

export function useExpandedResults(props) {
  const expandedResultIdx = ref(-1)

  const expandedResult = computed(() => {
    if (expandedResultIdx.value < 0 || expandedResultIdx.value >= props.historyItems.length) return null
    return props.historyItems[expandedResultIdx.value]
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
