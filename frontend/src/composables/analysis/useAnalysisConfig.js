import { computed, reactive, ref, watch } from 'vue'
import * as api from '../../api.js'

const CFA_METHOD_KEY = 'confirmatory_factor_analysis'
const RELIABILITY_METHOD_KEY = 'reliability'
const SUMMARY_T_METHOD_KEY = 'summary_t_test'
const INDEPENDENT_T_METHOD_KEY = 'independent_t_test'
const PAIRED_T_METHOD_KEY = 'paired_t_test'
const SUMMARY_ONEWAY_ANOVA_METHOD_KEY = 'summary_oneway_anova'
const ONE_WAY_ANOVA_METHOD_KEY = 'anova_oneway'
const ONE_SAMPLE_EQUIVALENCE_METHOD_KEY = 'one_sample_equivalence_test'
const TWO_SAMPLE_EQUIVALENCE_METHOD_KEY = 'two_sample_equivalence_test'
const PAIRED_EQUIVALENCE_METHOD_KEY = 'paired_equivalence_test'
const MODERATED_MEDIATION_METHOD_KEY = 'moderated_mediation'
const GOODNESS_OF_FIT_CHI_SQUARE_METHOD_KEY = 'goodness_of_fit_chi_square'
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
    tipText: '先点左侧因子，再把对应题项拖入右侧；每次拖入后会清空左侧多选。',
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

export function useAnalysisConfig(method, methodKey, emit, sessionId = ref('')) {
  const slotValues = reactive({})
  const optionValues = reactive({})
  const dragOverSlot = ref(null)
  const dynamicFactorCount = ref(1)
  const maxDynamicFactors = 12
  const factorMenuKey = ref(null)
  const activeFactorKey = ref('factor1_vars')
  const renameFocusToken = ref({ key: '', nonce: 0 })
  const factorLabels = reactive({})
  const secondOrderModels = ref([])
  const activeSecondOrderKey = ref('second_order_1')
  const goodnessOfFitCategories = ref([])
  const goodnessOfFitLoading = ref(false)

  const dynamicGroupConfig = computed(() => DYNAMIC_GROUP_CONFIGS[methodKey.value] || null)
  const isCfaMethod = computed(() => Boolean(dynamicGroupConfig.value))
  const isSummaryTMethod = computed(() => methodKey.value === SUMMARY_T_METHOD_KEY)
  const isIndependentTMethod = computed(() => methodKey.value === INDEPENDENT_T_METHOD_KEY)
  const isPairedTMethod = computed(() => methodKey.value === PAIRED_T_METHOD_KEY)
  const isSummaryOneWayAnovaMethod = computed(() => methodKey.value === SUMMARY_ONEWAY_ANOVA_METHOD_KEY)
  const isOneWayAnovaMethod = computed(() => methodKey.value === ONE_WAY_ANOVA_METHOD_KEY)
  const isOneSampleEquivalenceMethod = computed(() => methodKey.value === ONE_SAMPLE_EQUIVALENCE_METHOD_KEY)
  const isTwoSampleEquivalenceMethod = computed(() => methodKey.value === TWO_SAMPLE_EQUIVALENCE_METHOD_KEY)
  const isPairedEquivalenceMethod = computed(() => methodKey.value === PAIRED_EQUIVALENCE_METHOD_KEY)
  const isModeratedMediationMethod = computed(() => methodKey.value === MODERATED_MEDIATION_METHOD_KEY)
  const isGoodnessOfFitChiSquareMethod = computed(() => methodKey.value === GOODNESS_OF_FIT_CHI_SQUARE_METHOD_KEY)
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
  const firstOrderFactorChoices = computed(() => {
    if (!isCfaMethod.value) return []
    return displaySlots.value
      .map(slot => ({
        key: slot.key,
        label: getFactorShortLabel(slot.key),
        count: Array.isArray(slotValues[slot.key]) ? slotValues[slot.key].length : 0,
      }))
      .filter(item => item.count > 0)
  })
  const activeSecondOrderModel = computed(() => (
    secondOrderModels.value.find(model => model.key === activeSecondOrderKey.value) || secondOrderModels.value[0] || null
  ))
  const activeSecondOrderFactorName = computed(() => activeSecondOrderModel.value?.label || '二阶模型1')
  const activeSecondOrderMembers = computed(() => activeSecondOrderModel.value?.members || [])
  const secondOrderMemberOwnerMap = computed(() => {
    const ownerMap = {}
    for (const model of secondOrderModels.value) {
      for (const member of model.members || []) {
        if (!ownerMap[member]) ownerMap[member] = model
      }
    }
    return ownerMap
  })
  const secondOrderFactorChoices = computed(() => firstOrderFactorChoices.value.map(factor => {
    const owner = secondOrderMemberOwnerMap.value[factor.key] || null
    return {
      ...factor,
      ownerKey: owner?.key || '',
      ownerLabel: owner?.label || '',
      disabled: Boolean(owner && owner.key !== activeSecondOrderKey.value),
    }
  }))
  const maxSecondOrderModels = 8

  const canExecute = computed(() => {
    if (!method.value) return false
    if (isGoodnessOfFitChiSquareMethod.value) return goodnessOfFitReady()
    if (isIndependentTMethod.value) return independentTReady()
    if (isPairedTMethod.value) return pairedTReady()
    if (isSummaryTMethod.value) return summaryTReady()
    if (isSummaryOneWayAnovaMethod.value) return summaryOneWayAnovaReady()
    if (isOneWayAnovaMethod.value) return oneWayAnovaReady()
    if (isOneSampleEquivalenceMethod.value) return oneSampleEquivalenceReady()
    if (isTwoSampleEquivalenceMethod.value) return twoSampleEquivalenceReady()
    if (isPairedEquivalenceMethod.value) return pairedEquivalenceReady()
    if (isModeratedMediationMethod.value && !moderatedMediationPathReady()) return false
    if (isCfaMethod.value) {
      const groupLengths = displaySlots.value.map(slot => (slotValues[slot.key] || []).length)
      const validGroupLengths = groupLengths.filter(length => length > 0)
      const firstOrderReady = validGroupLengths.length > 0 && validGroupLengths.every(length => length >= 2)
      if (!firstOrderReady) return false
      if (optionValues.second_order_model) {
        return secondOrderModels.value.length > 0 && secondOrderModels.value.every(model => model.members.length >= 2)
      }
      return true
    }
    for (const slot of displaySlots.value) {
      const vals = slotValues[slot.key] || []
      if (slot.required === false && vals.length === 0) continue
      const min = slot.min ?? (slot.type === 'single' ? 1 : 1)
      const max = Number(slot.max)
      if (vals.length < min) return false
      if (Number.isFinite(max) && vals.length > max) return false
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

  function buildSummaryOneWayGroups(count = 3) {
    return Array.from({ length: count }, (_, index) => ({
      label: `样本${index + 1}`,
      n: '',
      mean: '',
      std: '',
    }))
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
    syncSecondOrderMembers()
  }

  function syncSecondOrderMembers() {
    const availableKeys = new Set(firstOrderFactorChoices.value.map(item => item.key))
    if (!secondOrderModels.value.length) {
      secondOrderModels.value = [{
        key: 'second_order_1',
        label: '二阶模型1',
        members: availableKeys.size >= 2 ? [...availableKeys] : [],
      }]
    } else {
      secondOrderModels.value = secondOrderModels.value.map(model => {
        const members = model.members.filter(key => availableKeys.has(key))
        return {
          ...model,
          members,
        }
      })
    }
    if (!secondOrderModels.value.some(model => model.key === activeSecondOrderKey.value)) {
      activeSecondOrderKey.value = secondOrderModels.value[0]?.key || 'second_order_1'
    }
  }

  function resetConfigState(nextMethod) {
    factorMenuKey.value = null
    secondOrderModels.value = []
    activeSecondOrderKey.value = 'second_order_1'
    for (const key of Object.keys(slotValues)) delete slotValues[key]
    for (const key of Object.keys(optionValues)) delete optionValues[key]
    for (const key of Object.keys(factorLabels)) delete factorLabels[key]
    goodnessOfFitCategories.value = []
    if (!nextMethod) return

    if (isSummaryTMethod.value) {
      Object.assign(optionValues, {
        test_type: 'one_sample',
        mean: '',
        std: '',
        n: '',
        test_value: '0',
        group1_mean: '',
        group1_std: '',
        group1_n: '',
        group2_mean: '',
        group2_std: '',
        group2_n: '',
        diff_test_value: '0',
        confidence_level: '95',
        alternative: '等于',
      })
    } else if (isSummaryOneWayAnovaMethod.value) {
      Object.assign(optionValues, {
        groups: buildSummaryOneWayGroups(),
        confidence_level: '95',
      })
    } else if (isIndependentTMethod.value) {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
      Object.assign(optionValues, {
        data_format: '样本在同一列',
      })
    } else if (isOneWayAnovaMethod.value) {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
      Object.assign(optionValues, {
        data_format: '样本在同一列',
        post_hoc: 'LSD',
        include_effect_size: true,
      })
    } else if (isOneSampleEquivalenceMethod.value) {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
      Object.assign(optionValues, {
        alternative: '下限<检验均值-目标值<上限',
        target_value: '',
        lower: '-0.1',
        upper: '0.1',
        scale_by_target: true,
      })
    } else if (isTwoSampleEquivalenceMethod.value) {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
      Object.assign(optionValues, {
        data_format: '样本在同一列',
        reference_level: '',
        relationship: '检验均值 - 参考均值',
        alternative: '下限<检验均值 - 参考均值<上限',
        lower: '-0.1',
        upper: '0.1',
        scale_by_reference: true,
      })
    } else if (isPairedEquivalenceMethod.value) {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
      Object.assign(optionValues, {
        relationship: '检验均值 - 参考均值',
        alternative: '下限<检验均值 - 参考均值<上限',
        lower: '-0.1',
        upper: '0.1',
        scale_by_reference: true,
      })
    } else if (isCfaMethod.value) {
      dynamicFactorCount.value = 1
      activeFactorKey.value = slotKeyFor(1)
      syncCfaSlotValues()
    } else {
      for (const slot of nextMethod.slots || []) {
        slotValues[slot.key] = []
      }
    }

    for (const option of (nextMethod.options || [])) {
      if ((isSummaryTMethod.value || isSummaryOneWayAnovaMethod.value || isIndependentTMethod.value || isOneWayAnovaMethod.value || isOneSampleEquivalenceMethod.value || isTwoSampleEquivalenceMethod.value || isPairedEquivalenceMethod.value) && Object.prototype.hasOwnProperty.call(optionValues, option.key)) {
        continue
      }
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
    emit('reset-variable-selection')
  }

  function isUsedInOtherStaticSlot(slotKey, varName) {
    if (isCfaMethod.value || displaySlots.value.length <= 1) return false
    return displaySlots.value.some(slot => (
      slot.key !== slotKey && Array.isArray(slotValues[slot.key]) && slotValues[slot.key].includes(varName)
    ))
  }

  function addVar(slotKey, varName, slotType) {
    if (!slotValues[slotKey]) slotValues[slotKey] = []
    if (slotValues[slotKey].includes(varName)) return
    if (isUsedInOtherStaticSlot(slotKey, varName)) return
    const slot = displaySlots.value.find(item => item.key === slotKey)
    const max = Number(slot?.max)
    if (slotType !== 'single' && Number.isFinite(max) && slotValues[slotKey].length >= max) return
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
    syncSecondOrderMembers()
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
    if (isSummaryTMethod.value || isSummaryOneWayAnovaMethod.value || isIndependentTMethod.value || isPairedTMethod.value || isOneSampleEquivalenceMethod.value || isTwoSampleEquivalenceMethod.value) {
      resetConfigState(method.value)
      return
    }
    if (isCfaMethod.value) {
      dynamicFactorCount.value = 1
      for (const key of Object.keys(slotValues)) delete slotValues[key]
      for (const key of Object.keys(factorLabels)) delete factorLabels[key]
      activeFactorKey.value = slotKeyFor(1)
      factorMenuKey.value = null
      secondOrderModels.value = []
      activeSecondOrderKey.value = 'second_order_1'
      syncCfaSlotValues()
      syncSecondOrderMembers()
      return
    }
    for (const slot of displaySlots.value) {
      slotValues[slot.key] = []
    }
  }

  function setOptionValue(key, value) {
    optionValues[key] = value
    if (isModeratedMediationMethod.value && ['moderate_x_m', 'moderate_m_y', 'moderate_x_y'].includes(key)) {
      optionValues.model = moderatedMediationModel()
    }
    if (isTwoSampleEquivalenceMethod.value && key === 'data_format') {
      if (value === '样本在不同列') {
        slotValues.group_var = []
        optionValues.reference_level = ''
      } else {
        slotValues.reference_var = []
      }
    }
    if (isIndependentTMethod.value && key === 'data_format') {
      if (value === '样本在不同列') {
        slotValues.group_var = []
      }
    }
    if (isOneWayAnovaMethod.value && key === 'data_format') {
      if (value === '样本在不同列') {
        slotValues.group_var = []
        slotValues.test_vars = []
      } else {
        slotValues.group_columns = []
      }
    }
    if (key === 'second_order_model') syncSecondOrderMembers()
  }

  function setGoodnessOfFitExpectedRatio(label, value) {
    const current = optionValues.expected_ratios && typeof optionValues.expected_ratios === 'object'
      ? optionValues.expected_ratios
      : {}
    optionValues.expected_ratios = {
      ...current,
      [String(label)]: value,
    }
  }

  function filledNumber(value, mode = 'any') {
    if (value === '' || value === null || value === undefined) return false
    const number = Number(value)
    if (!Number.isFinite(number)) return false
    if (mode === 'positive') return number > 0
    if (mode === 'non_negative') return number >= 0
    return true
  }

  function goodnessOfFitReady() {
    return (slotValues.variable || []).length === 1
  }

  function summaryTReady() {
    if (optionValues.test_type === 'independent') {
      return (
        filledNumber(optionValues.group1_mean)
        && filledNumber(optionValues.group1_std, 'positive')
        && filledNumber(optionValues.group1_n, 'positive')
        && filledNumber(optionValues.group2_mean)
        && filledNumber(optionValues.group2_std, 'positive')
        && filledNumber(optionValues.group2_n, 'positive')
        && filledNumber(optionValues.diff_test_value)
      )
    }
    return (
      filledNumber(optionValues.mean)
      && filledNumber(optionValues.std, 'positive')
      && filledNumber(optionValues.n, 'positive')
      && filledNumber(optionValues.test_value)
    )
  }

  function independentTReady() {
    const testSelected = slotValues.test_vars || []
    if (optionValues.data_format === '样本在不同列') {
      return testSelected.length === 2
    }
    return (slotValues.group_var || []).length === 1 && testSelected.length >= 1
  }

  function pairedTReady() {
    const firstSelected = slotValues.var1 || []
    const secondSelected = slotValues.var2 || []
    return firstSelected.length >= 1 && firstSelected.length === secondSelected.length
  }

  function summaryOneWayAnovaReady() {
    const groups = Array.isArray(optionValues.groups) ? optionValues.groups : []
    return groups.length >= 3 && groups.every(group => (
      filledNumber(group.n, 'positive')
      && Number(group.n) > 1
      && filledNumber(group.mean)
      && filledNumber(group.std, 'non_negative')
    ))
  }

  function oneSampleEquivalenceReady() {
    const variableSlot = displaySlots.value[0]
    const selected = variableSlot ? (slotValues[variableSlot.key] || []) : []
    return (
      selected.length === 1
      && filledNumber(optionValues.target_value)
      && filledNumber(optionValues.lower)
      && filledNumber(optionValues.upper)
      && Number(optionValues.lower) < Number(optionValues.upper)
    )
  }

  function twoSampleEquivalenceReady() {
    const testSelected = slotValues.test_var || []
    const groupSelected = slotValues.group_var || []
    const refSelected = slotValues.reference_var || []
    const slotsReady = optionValues.data_format === '样本在不同列'
      ? testSelected.length === 1 && refSelected.length === 1
      : testSelected.length === 1 && groupSelected.length === 1
    return (
      slotsReady
      && filledNumber(optionValues.lower)
      && filledNumber(optionValues.upper)
      && Number(optionValues.lower) < Number(optionValues.upper)
    )
  }

  function oneWayAnovaReady() {
    if (optionValues.data_format === '样本在不同列') {
      return (slotValues.group_columns || []).length >= 3
    }
    return (slotValues.group_var || []).length === 1 && (slotValues.test_vars || []).length >= 1
  }

  function pairedEquivalenceReady() {
    const testSelected = slotValues.test_var || slotValues.var1 || []
    const refSelected = slotValues.reference_var || slotValues.var2 || []
    return (
      testSelected.length === 1
      && refSelected.length === 1
      && filledNumber(optionValues.lower)
      && filledNumber(optionValues.upper)
      && Number(optionValues.lower) < Number(optionValues.upper)
    )
  }

  function moderatedMediationModel() {
    const xM = Boolean(optionValues.moderate_x_m)
    const mY = Boolean(optionValues.moderate_m_y)
    const xY = Boolean(optionValues.moderate_x_y)
    if (!xM && !mY && xY) return '5'
    if (xM && !mY && !xY) return '7'
    if (xM && !mY && xY) return '8'
    if (!xM && mY && !xY) return '14'
    if (!xM && mY && xY) return '15'
    if (xM && mY && !xY) return '58'
    if (xM && mY && xY) return '59'
    return ''
  }

  function moderatedMediationPathReady() {
    return Boolean(optionValues.moderate_x_m || optionValues.moderate_m_y || optionValues.moderate_x_y)
  }

  function addSummaryOneWayGroup() {
    const groups = Array.isArray(optionValues.groups) ? optionValues.groups : []
    optionValues.groups = [
      ...groups,
      {
        label: `样本${groups.length + 1}`,
        n: '',
        mean: '',
        std: '',
      },
    ]
  }

  function removeSummaryOneWayGroup(index) {
    const groups = Array.isArray(optionValues.groups) ? optionValues.groups : []
    if (groups.length <= 3) return
    optionValues.groups = groups
      .filter((_, itemIndex) => itemIndex !== index)
      .map((group, itemIndex) => ({
        ...group,
        label: group.label || `样本${itemIndex + 1}`,
      }))
  }

  function updateSummaryOneWayGroup(index, key, value) {
    const groups = Array.isArray(optionValues.groups) ? optionValues.groups : []
    optionValues.groups = groups.map((group, itemIndex) => (
      itemIndex === index ? { ...group, [key]: value } : group
    ))
  }

  function setSecondOrderFactorName(value) {
    const next = String(value || '').trim()
    const activeKey = activeSecondOrderKey.value
    secondOrderModels.value = secondOrderModels.value.map(model => (
      model.key === activeKey ? { ...model, label: next || model.label || '二阶模型1' } : model
    ))
  }

  function addSecondOrderModel() {
    if (secondOrderModels.value.length >= maxSecondOrderModels) return
    const nextIndex = secondOrderModels.value.length + 1
    const key = `second_order_${Date.now()}_${nextIndex}`
    secondOrderModels.value = [
      ...secondOrderModels.value,
      { key, label: `二阶模型${nextIndex}`, members: [] },
    ]
    activeSecondOrderKey.value = key
  }

  function selectSecondOrderModel(key) {
    if (secondOrderModels.value.some(model => model.key === key)) {
      activeSecondOrderKey.value = key
    }
  }

  function deleteSecondOrderModel(key) {
    if (secondOrderModels.value.length <= 1) return
    const deletedIndex = secondOrderModels.value.findIndex(model => model.key === key)
    secondOrderModels.value = secondOrderModels.value.filter(model => model.key !== key)
    if (activeSecondOrderKey.value === key) {
      const nextIndex = Math.min(Math.max(deletedIndex, 0), secondOrderModels.value.length - 1)
      activeSecondOrderKey.value = secondOrderModels.value[nextIndex]?.key || 'second_order_1'
    }
  }

  function toggleSecondOrderMember(slotKey) {
    const choices = firstOrderFactorChoices.value.map(item => item.key)
    if (!choices.includes(slotKey)) return
    const owner = secondOrderMemberOwnerMap.value[slotKey]
    if (owner && owner.key !== activeSecondOrderKey.value) return
    const activeKey = activeSecondOrderKey.value
    secondOrderModels.value = secondOrderModels.value.map(model => {
      if (model.key !== activeKey) return model
      return {
        ...model,
        members: model.members.includes(slotKey)
          ? model.members.filter(key => key !== slotKey)
          : [...model.members, slotKey],
      }
    })
  }

  watch([method, methodKey], ([nextMethod]) => {
    resetConfigState(nextMethod)
  }, { immediate: true })

  watch(
    () => [isGoodnessOfFitChiSquareMethod.value, sessionId.value, slotValues.variable?.[0] || ''],
    async ([enabled, sid, variable]) => {
      if (!enabled || !sid || !variable) {
        goodnessOfFitCategories.value = []
        return
      }
      const requestKey = `${sid}:${variable}`
      goodnessOfFitLoading.value = true
      try {
        const data = await api.getVariableValues(sid, variable)
        if (`${sessionId.value}:${slotValues.variable?.[0] || ''}` !== requestKey) return
        const values = (data.values || []).map(value => String(value))
        goodnessOfFitCategories.value = values
        const existing = optionValues.expected_ratios && typeof optionValues.expected_ratios === 'object'
          ? optionValues.expected_ratios
          : {}
        const next = {}
        values.forEach(value => {
          next[value] = existing[value] ?? ''
        })
        optionValues.expected_ratios = next
      } catch (_) {
        goodnessOfFitCategories.value = []
      } finally {
        if (`${sessionId.value}:${slotValues.variable?.[0] || ''}` === requestKey) {
          goodnessOfFitLoading.value = false
        }
      }
    },
    { immediate: true },
  )

  function emitSlotValues() {
    const payload = { ...slotValues }
    const labelParamKey = dynamicGroupConfig.value?.labelParamKey
    if (labelParamKey) {
      payload[labelParamKey] = { ...factorLabels }
    }
    emit('update:slotValues', payload)
  }

  function emitOptionValues() {
    const payload = { ...optionValues }
    if (isModeratedMediationMethod.value) {
      payload.model = moderatedMediationModel()
      payload.moderated_paths = {
        x_m: Boolean(optionValues.moderate_x_m),
        m_y: Boolean(optionValues.moderate_m_y),
        x_y: Boolean(optionValues.moderate_x_y),
      }
    }
    if (isCfaMethod.value && optionValues.second_order_model) {
      const factorLabelMap = {}
      for (const item of firstOrderFactorChoices.value) {
        factorLabelMap[item.key] = item.label
      }
      payload.second_order_models = secondOrderModels.value.map(model => ({
        name: model.label || '二阶模型1',
        members: model.members.filter(key => factorLabelMap[key]),
      }))
      const firstModel = payload.second_order_models[0] || { name: '二阶模型1', members: [] }
      payload.second_order_factor = firstModel.name
      payload.second_order_members = firstModel.members
    }
    emit('update:optionValues', payload)
  }

  watch(slotValues, emitSlotValues, { deep: true })
  watch(factorLabels, emitSlotValues, { deep: true })
  watch(firstOrderFactorChoices, syncSecondOrderMembers, { deep: true })
  watch(optionValues, emitOptionValues, { deep: true })
  watch([secondOrderModels, activeSecondOrderKey], emitOptionValues, { deep: true })

  return {
    activeSecondOrderFactorName,
    activeSecondOrderKey,
    activeSecondOrderMembers,
    activeFactorSlot,
    activeFactorItems,
    activeFactorKey,
    activeFactorTitle,
    addSecondOrderModel,
    addFactorSlot,
    addSummaryOneWayGroup,
    addVar,
    canExecute,
    deleteFactor,
    deleteSecondOrderModel,
    displaySlots,
    dragOverSlot,
    dynamicFactorCount,
    dynamicGroupAddText,
    dynamicGroupItemName,
    dynamicGroupTip,
    factorMenuKey,
    getFactorShortLabel,
    goodnessOfFitCategories,
    goodnessOfFitLoading,
    isCfaMethod,
    isGoodnessOfFitChiSquareMethod,
    isIndependentTMethod,
    isPairedTMethod,
    isOneSampleEquivalenceMethod,
    isOneWayAnovaMethod,
    isPairedEquivalenceMethod,
    isModeratedMediationMethod,
    isTwoSampleEquivalenceMethod,
    isSummaryOneWayAnovaMethod,
    isSummaryTMethod,
    maxDynamicFactors,
    maxSecondOrderModels,
    onDragLeave,
    onDragOver,
    onDrop,
    optionValues,
    removeFactorSlot,
    removeSummaryOneWayGroup,
    removeVar,
    renameFactor,
    renameFactorInline,
    renameFocusToken,
    resetSlots,
    selectFactor,
    selectSecondOrderModel,
    setGoodnessOfFitExpectedRatio,
    setOptionValue,
    setSecondOrderFactorName,
    slotValues,
    firstOrderFactorChoices,
    secondOrderModels,
    secondOrderFactorChoices,
    toggleFactorMenu,
    toggleSecondOrderMember,
    updateSummaryOneWayGroup,
  }
}
