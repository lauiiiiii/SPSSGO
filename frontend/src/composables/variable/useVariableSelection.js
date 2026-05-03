import { computed } from 'vue'

export function useVariableSelection({
  currentSlotValues,
  selectedVars,
}) {
  const usedVars = computed(() => {
    const set = new Set()
    for (const values of Object.values(currentSlotValues.value || {})) {
      if (Array.isArray(values)) values.forEach(value => set.add(value))
    }
    return set
  })

  function onVarSelect(varName) {
    if (!selectedVars.value.includes(varName)) {
      selectedVars.value.push(varName)
    }
  }

  function onVarDeselect(varName) {
    const index = selectedVars.value.indexOf(varName)
    if (index >= 0) selectedVars.value.splice(index, 1)
  }

  function onVarSelectRange(names) {
    for (const name of names) {
      if (!selectedVars.value.includes(name)) {
        selectedVars.value.push(name)
      }
    }
  }

  return {
    onVarDeselect,
    onVarSelect,
    onVarSelectRange,
    usedVars,
  }
}
