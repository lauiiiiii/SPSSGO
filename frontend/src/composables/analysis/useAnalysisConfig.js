import { computed, reactive, ref, watch } from 'vue'

const CFA_METHOD_KEY = 'confirmatory_factor_analysis'
const FACTOR_SLOT_PATTERN = /^factor(\d+)_vars$/

export function useAnalysisConfig(method, methodKey, emit) {
  const slotValues = reactive({})
  const optionValues = reactive({})
  const dragOverSlot = ref(null)
  const dynamicFactorCount = ref(1)
  const maxDynamicFactors = 12
  const factorMenuKey = ref(null)
  const activeFactorKey = ref('factor1_vars')
  const factorLabels = reactive({})

  const isCfaMethod = computed(() => methodKey.value === CFA_METHOD_KEY)
  const methodSlots = computed(() => method.value?.slots || [])

  const displaySlots = computed(() => {
    if (!method.value) return []
    if (!isCfaMethod.value) return methodSlots.value
    return Array.from({ length: dynamicFactorCount.value }, (_, index) => buildFactorSlot(index + 1))
  })

  const activeFactorSlot = computed(() => (
    displaySlots.value.find(slot => slot.key === activeFactorKey.value) || displaySlots.value[0] || null
  ))
  const activeFactorItems = computed(() => {
    const key = activeFactorKey.value
    return key ? (slotValues[key] || []) : []
  })
  const activeFactorTitle = computed(() => activeFactorSlot.value?.label || '因子1')

  const canExecute = computed(() => {
    if (!method.value) return false
    for (const slot of displaySlots.value) {
      const vals = slotValues[slot.key] || []
      const min = slot.min ?? (slot.type === 'single' ? 1 : 1)
      if (vals.length < min) return false
    }
    return true
  })

  function buildFactorSlot(index) {
    const key = `factor${index}_vars`
    const firstSlot = methodSlots.value[0] || {}
    return {
      ...firstSlot,
      key,
      label: factorLabels[key] || `因子${index}`,
      type: 'multiple',
      accept: firstSlot.accept || 'numeric',
      min: index === 1 ? 2 : 0,
      hint: index === 1 ? '放入因子1对应的题项' : `可选：放入因子${index}对应的题项`,
    }
  }

  function syncCfaSlotValues() {
    for (let index = 1; index <= dynamicFactorCount.value; index += 1) {
      const key = `factor${index}_vars`
      if (!Array.isArray(slotValues[key])) slotValues[key] = []
      if (!factorLabels[key]) factorLabels[key] = `因子${index}`
    }
    for (const key of Object.keys(slotValues)) {
      const match = key.match(FACTOR_SLOT_PATTERN)
      if (match && Number(match[1]) > dynamicFactorCount.value) {
        delete slotValues[key]
      }
    }
    for (const key of Object.keys(factorLabels)) {
      const match = key.match(FACTOR_SLOT_PATTERN)
      if (match && Number(match[1]) > dynamicFactorCount.value) {
        delete factorLabels[key]
      }
    }
    if (!slotValues[activeFactorKey.value]) {
      activeFactorKey.value = 'factor1_vars'
    }
  }

  function resetConfigState(nextMethod) {
    factorMenuKey.value = null
    for (const key of Object.keys(slotValues)) delete slotValues[key]
    for (const key of Object.keys(optionValues)) delete optionValues[key]
    for (const key of Object.keys(factorLabels)) delete factorLabels[key]
    if (!nextMethod) return

    if (isCfaMethod.value) {
      dynamicFactorCount.value = 1
      activeFactorKey.value = 'factor1_vars'
      syncCfaSlotValues()
    } else {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
    }

    for (const option of (nextMethod.options || [])) {
      optionValues[option.key] = option.default || option.choices?.[0] || ''
    }
  }

  function onDragOver(slotKey) {
    dragOverSlot.value = slotKey
  }

  function onDragLeave() {
    dragOverSlot.value = null
  }

  function onDrop(event, slot) {
    dragOverSlot.value = null
    const raw = event.dataTransfer.getData('text/plain')
    if (!raw) return
    const names = raw.split(',').filter(Boolean)
    for (const varName of names) {
      addVar(slot.key, varName, slot.type)
    }
  }

  function addVar(slotKey, varName, slotType) {
    if (!slotValues[slotKey]) slotValues[slotKey] = []
    if (slotValues[slotKey].includes(varName)) return
    if (slotType === 'single') {
      slotValues[slotKey] = [varName]
    } else {
      slotValues[slotKey].push(varName)
    }
  }

  function removeVar(slotKey, varName) {
    if (!slotValues[slotKey]) return
    const index = slotValues[slotKey].indexOf(varName)
    if (index >= 0) slotValues[slotKey].splice(index, 1)
  }

  function addFactorSlot() {
    if (!isCfaMethod.value || dynamicFactorCount.value >= maxDynamicFactors) return
    dynamicFactorCount.value += 1
    syncCfaSlotValues()
    activeFactorKey.value = `factor${dynamicFactorCount.value}_vars`
    factorMenuKey.value = null
  }

  function removeFactorSlot() {
    if (!isCfaMethod.value || dynamicFactorCount.value <= 1) return
    delete slotValues[`factor${dynamicFactorCount.value}_vars`]
    delete factorLabels[`factor${dynamicFactorCount.value}_vars`]
    dynamicFactorCount.value -= 1
    syncCfaSlotValues()
    activeFactorKey.value = `factor${dynamicFactorCount.value}_vars`
    factorMenuKey.value = null
  }

  function selectFactor(slotKey) {
    activeFactorKey.value = slotKey
    factorMenuKey.value = null
  }

  function toggleFactorMenu(slotKey) {
    factorMenuKey.value = factorMenuKey.value === slotKey ? null : slotKey
  }

  function getFactorShortLabel(slotKey) {
    return factorLabels[slotKey] || displaySlots.value.find(slot => slot.key === slotKey)?.label || '因子'
  }

  function renameFactor(slotKey) {
    const current = getFactorShortLabel(slotKey)
    const next = window.prompt('请输入新的因子名称', current)
    if (next && next.trim()) {
      factorLabels[slotKey] = next.trim()
    }
    factorMenuKey.value = null
  }

  function deleteFactor(slotKey) {
    if (!isCfaMethod.value || dynamicFactorCount.value <= 1) {
      factorMenuKey.value = null
      return
    }
    const match = slotKey.match(FACTOR_SLOT_PATTERN)
    if (!match) {
      factorMenuKey.value = null
      return
    }
    const deletedIndex = Number(match[1])
    for (let index = deletedIndex; index < dynamicFactorCount.value; index += 1) {
      const nextKey = `factor${index + 1}_vars`
      const currentKey = `factor${index}_vars`
      slotValues[currentKey] = [...(slotValues[nextKey] || [])]
      factorLabels[currentKey] = factorLabels[nextKey] || `因子${index}`
    }
    delete slotValues[`factor${dynamicFactorCount.value}_vars`]
    delete factorLabels[`factor${dynamicFactorCount.value}_vars`]
    dynamicFactorCount.value -= 1
    syncCfaSlotValues()
    activeFactorKey.value = `factor${Math.min(deletedIndex, dynamicFactorCount.value)}_vars`
    factorMenuKey.value = null
  }

  function resetSlots() {
    if (isCfaMethod.value) {
      dynamicFactorCount.value = 1
      for (const key of Object.keys(slotValues)) delete slotValues[key]
      for (const key of Object.keys(factorLabels)) delete factorLabels[key]
      activeFactorKey.value = 'factor1_vars'
      factorMenuKey.value = null
      syncCfaSlotValues()
      return
    }
    for (const slot of displaySlots.value) {
      slotValues[slot.key] = []
    }
  }

  function setOptionValue(key, value) {
    optionValues[key] = value
  }

  watch([method, methodKey], ([nextMethod]) => {
    resetConfigState(nextMethod)
  }, { immediate: true })

  watch(slotValues, () => emit('update:slotValues', { ...slotValues }), { deep: true })
  watch(optionValues, () => emit('update:optionValues', { ...optionValues }), { deep: true })

  return {
    activeFactorSlot,
    activeFactorItems,
    activeFactorKey,
    activeFactorTitle,
    addFactorSlot,
    addVar,
    canExecute,
    deleteFactor,
    displaySlots,
    dragOverSlot,
    dynamicFactorCount,
    factorMenuKey,
    getFactorShortLabel,
    isCfaMethod,
    maxDynamicFactors,
    onDragLeave,
    onDragOver,
    onDrop,
    optionValues,
    removeFactorSlot,
    removeVar,
    renameFactor,
    resetSlots,
    selectFactor,
    setOptionValue,
    slotValues,
    toggleFactorMenu,
  }
}
