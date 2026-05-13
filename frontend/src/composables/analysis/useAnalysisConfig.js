import { computed, reactive, ref, watch } from 'vue'

const CFA_METHOD_KEY = 'confirmatory_factor_analysis'
const RELIABILITY_METHOD_KEY = 'reliability'
const DYNAMIC_GROUP_CONFIGS = {
  [CFA_METHOD_KEY]: {
    addText: '+ 新建因子',
    defaultLabel: '因子',
    emptyTitle: '因子1',
    hintTarget: '因子',
    itemName: '题项',
    labelParamKey: null,
    moveExistingItems: true,
    promptText: '请输入新的因子名称',
    slotPattern: /^factor(\d+)_vars$/,
    slotPrefix: 'factor',
    tipText: '点击左侧切换因子，变量会加入当前选中的因子。',
  },
  [RELIABILITY_METHOD_KEY]: {
    addText: '+ 新建维度',
    defaultLabel: '维度',
    emptyTitle: '维度1',
    hintTarget: '维度',
    itemName: '题项',
    labelParamKey: 'dimension_labels',
    moveExistingItems: false,
    promptText: '请输入新的维度名称',
    slotPattern: /^dimension(\d+)_vars$/,
    slotPrefix: 'dimension',
    tipText: '点击左侧切换维度，变量会加入当前选中的维度。',
  },
}

export function useAnalysisConfig(method, methodKey, emit) {
  const slotValues = reactive({})
  const optionValues = reactive({})
  const dragOverSlot = ref(null)
  const dynamicFactorCount = ref(1)
  const maxDynamicFactors = 12
  const factorMenuKey = ref(null)
  const activeFactorKey = ref('factor1_vars')
  const renameFocusToken = ref({ key: '', nonce: 0 })
  const factorLabels = reactive({})

  const dynamicGroupConfig = computed(() => DYNAMIC_GROUP_CONFIGS[methodKey.value] || null)
  const isCfaMethod = computed(() => Boolean(dynamicGroupConfig.value))
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
  const activeFactorTitle = computed(() => activeFactorSlot.value?.label || dynamicGroupConfig.value?.emptyTitle || '因子1')
  const dynamicGroupAddText = computed(() => dynamicGroupConfig.value?.addText || '+ 新建因子')
  const dynamicGroupItemName = computed(() => dynamicGroupConfig.value?.itemName || '题项')
  const dynamicGroupTip = computed(() => dynamicGroupConfig.value?.tipText || '')

  const canExecute = computed(() => {
    if (!method.value) return false
    if (isCfaMethod.value) {
      const groupLengths = displaySlots.value.map(slot => (slotValues[slot.key] || []).length)
      return groupLengths.some(length => length >= 2) && groupLengths.every(length => length === 0 || length >= 2)
    }
    for (const slot of displaySlots.value) {
      const vals = slotValues[slot.key] || []
      const min = slot.min ?? (slot.type === 'single' ? 1 : 1)
      if (vals.length < min) return false
    }
    return true
  })

  function slotKeyFor(index) {
    const config = dynamicGroupConfig.value || DYNAMIC_GROUP_CONFIGS[CFA_METHOD_KEY]
    return `${config.slotPrefix}${index}_vars`
  }

  function slotPattern() {
    return dynamicGroupConfig.value?.slotPattern || DYNAMIC_GROUP_CONFIGS[CFA_METHOD_KEY].slotPattern
  }

  function buildFactorSlot(index) {
    const config = dynamicGroupConfig.value || DYNAMIC_GROUP_CONFIGS[CFA_METHOD_KEY]
    const key = slotKeyFor(index)
    const firstSlot = methodSlots.value[0] || {}
    return {
      ...firstSlot,
      key,
      label: factorLabels[key] || `${config.defaultLabel}${index}`,
      type: 'multiple',
      accept: firstSlot.accept || 'numeric',
      min: 0,
      hint: `放入${config.hintTarget}${index}对应的题项`,
    }
  }

  function syncCfaSlotValues() {
    for (let index = 1; index <= dynamicFactorCount.value; index += 1) {
      const key = slotKeyFor(index)
      if (!Array.isArray(slotValues[key])) slotValues[key] = []
      if (!factorLabels[key]) factorLabels[key] = `${dynamicGroupConfig.value?.defaultLabel || '因子'}${index}`
    }
    for (const key of Object.keys(slotValues)) {
      const match = key.match(slotPattern())
      if (match && Number(match[1]) > dynamicFactorCount.value) {
        delete slotValues[key]
      }
    }
    for (const key of Object.keys(factorLabels)) {
      const match = key.match(slotPattern())
      if (match && Number(match[1]) > dynamicFactorCount.value) {
        delete factorLabels[key]
      }
    }
    if (!slotValues[activeFactorKey.value]) {
      activeFactorKey.value = slotKeyFor(1)
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
      activeFactorKey.value = slotKeyFor(1)
      syncCfaSlotValues()
    } else {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
    }

    for (const option of (nextMethod.options || [])) {
      if (option.type === 'checkbox') {
        optionValues[option.key] = Boolean(option.default)
      } else if (option.type === 'multiple') {
        const defaultValues = Array.isArray(option.default)
          ? option.default
          : [option.default || option.choices?.[0]].filter(Boolean)
        optionValues[option.key] = defaultValues
      } else {
        optionValues[option.key] = option.default || option.choices?.[0] || ''
      }
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
    if (isCfaMethod.value && slotType !== 'single') {
      for (const key of Object.keys(slotValues)) {
        if (key !== slotKey && key.match(slotPattern()) && Array.isArray(slotValues[key])) {
          if (!dynamicGroupConfig.value?.moveExistingItems && slotValues[key].includes(varName)) return
          slotValues[key] = slotValues[key].filter(item => item !== varName)
        }
      }
    }
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
    activeFactorKey.value = slotKeyFor(dynamicFactorCount.value)
    factorMenuKey.value = null
  }

  function removeFactorSlot() {
    if (!isCfaMethod.value || dynamicFactorCount.value <= 1) return
    delete slotValues[slotKeyFor(dynamicFactorCount.value)]
    delete factorLabels[slotKeyFor(dynamicFactorCount.value)]
    dynamicFactorCount.value -= 1
    syncCfaSlotValues()
    activeFactorKey.value = slotKeyFor(dynamicFactorCount.value)
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
    return factorLabels[slotKey] || displaySlots.value.find(slot => slot.key === slotKey)?.label || dynamicGroupConfig.value?.defaultLabel || '因子'
  }

  function renameFactor(slotKey) {
    if (!slotKey || !factorLabels[slotKey]) return
    activeFactorKey.value = slotKey
    renameFocusToken.value = { key: slotKey, nonce: Date.now() }
    factorMenuKey.value = null
  }

  function renameFactorInline(slotKey, value) {
    if (!slotKey || !factorLabels[slotKey]) return
    const next = String(value || '').trim()
    if (!next) return
    factorLabels[slotKey] = next
  }

  function deleteFactor(slotKey) {
    if (!isCfaMethod.value || dynamicFactorCount.value <= 1) {
      factorMenuKey.value = null
      return
    }
    const match = slotKey.match(slotPattern())
    if (!match) {
      factorMenuKey.value = null
      return
    }
    const deletedIndex = Number(match[1])
    for (let index = deletedIndex; index < dynamicFactorCount.value; index += 1) {
      const nextKey = slotKeyFor(index + 1)
      const currentKey = slotKeyFor(index)
      slotValues[currentKey] = [...(slotValues[nextKey] || [])]
      factorLabels[currentKey] = factorLabels[nextKey] || `${dynamicGroupConfig.value?.defaultLabel || '因子'}${index}`
    }
    delete slotValues[slotKeyFor(dynamicFactorCount.value)]
    delete factorLabels[slotKeyFor(dynamicFactorCount.value)]
    dynamicFactorCount.value -= 1
    syncCfaSlotValues()
    activeFactorKey.value = slotKeyFor(Math.min(deletedIndex, dynamicFactorCount.value))
    factorMenuKey.value = null
  }

  function resetSlots() {
    if (isCfaMethod.value) {
      dynamicFactorCount.value = 1
      for (const key of Object.keys(slotValues)) delete slotValues[key]
      for (const key of Object.keys(factorLabels)) delete factorLabels[key]
      activeFactorKey.value = slotKeyFor(1)
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

  function emitSlotValues() {
    const payload = { ...slotValues }
    const labelParamKey = dynamicGroupConfig.value?.labelParamKey
    if (labelParamKey) {
      payload[labelParamKey] = { ...factorLabels }
    }
    emit('update:slotValues', payload)
  }

  watch(slotValues, emitSlotValues, { deep: true })
  watch(factorLabels, emitSlotValues, { deep: true })
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
    dynamicGroupAddText,
    dynamicGroupItemName,
    dynamicGroupTip,
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
    renameFactorInline,
    renameFocusToken,
    resetSlots,
    selectFactor,
    setOptionValue,
    slotValues,
    toggleFactorMenu,
  }
}
