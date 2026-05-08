import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import * as api from '../../api.js'
import {
  buildMethodParams,
  createDefaultDialogOptions,
  createDefaultMethodRuntime,
  getInitialSelection,
  getMethodActions,
  getMethodAutoSaveKey,
  getMethodEffectKey,
  processingMethodMap,
  runMethodAutoSave,
  runMethodEffect,
  validateMethod,
} from '../methodRegistry.js'

export function useProcessingMethodDialog(props, {
  emit,
  loadPreview,
  loadVersions,
  notifySuccess,
  onPreviewMutated,
  variableMetaMap,
}) {
  const activeMethod = ref('')
  const processing = ref(false)
  const errorMsg = ref('')
  const dialogSelectedVars = ref([])
  const methodRuntime = reactive(createDefaultMethodRuntime())
  const dialogOptions = reactive(createDefaultDialogOptions())

  const activeMethodMeta = computed(() => processingMethodMap[activeMethod.value] || null)
  const activeMethodLabel = computed(() => activeMethodMeta.value ? activeMethodMeta.value.label : '')
  const activeMethodComponent = computed(() => activeMethodMeta.value?.component || null)
  const dialogHelpText = computed(() => activeMethodMeta.value?.helpText || '')
  const methodNeedsMultiVar = computed(() => activeMethodMeta.value?.selectionMode === 'multi')
  const methodMinVars = computed(() => activeMethodMeta.value?.minVars || 0)
  const methodActions = computed(() => getMethodActions(activeMethod.value, {
    options: dialogOptions,
    runtime: methodRuntime,
    sessionId: props.sessionId,
    selectedVars: dialogSelectedVars.value,
  }))

  const labelHintText = computed(() => {
    if (!dialogSelectedVars.value.length) return '请先在左侧选择一个定类变量。数据标签仅用于给分类编码绑定文字含义，不会改变统计计算结果。'
    const selectedVar = variableMetaMap.value[dialogSelectedVars.value[0]]
    if (selectedVar && selectedVar.type !== 'categorical') {
      return '当前变量是定量变量，数据标签不适用。'
    }
    return '当前变量没有可用标签值'
  })
  const labelEditable = computed(() => {
    if (!dialogSelectedVars.value.length) return false
    const selectedVar = variableMetaMap.value[dialogSelectedVars.value[0]]
    return !!selectedVar && isLabelCompatible(selectedVar)
  })
  const encodeHintText = computed(() => {
    if (!dialogSelectedVars.value.length) return '请先在左侧选择一个变量。输入支持一项定量变量或定类变量。'
    if (dialogOptions.encodeMode === 'range') return '范围编码适用于连续数值变量；若是分类变量，则会基于其编码值进行分组。请先输入不重复的分组区间。'
    if (dialogOptions.encodeMode === 'auto') return '自动分组会基于数值信息进行切分；若是分类变量，则会基于其编码值进行分组。'
    return '当前变量没有可编码的取值，请先检查该变量是否存在有效数据。'
  })

  let methodAutoSaveTimer = null

  const activeMethodEffectKey = computed(() => getMethodEffectKey(activeMethod.value, {
    activeMethod: activeMethod.value,
    sessionId: props.sessionId,
    selectedVars: dialogSelectedVars.value,
    options: dialogOptions,
    runtime: methodRuntime,
  }))

  const activeMethodAutoSaveKey = computed(() => getMethodAutoSaveKey(activeMethod.value, {
    activeMethod: activeMethod.value,
    sessionId: props.sessionId,
    selectedVars: dialogSelectedVars.value,
    options: dialogOptions,
    runtime: methodRuntime,
    variableMetaMap: variableMetaMap.value,
  }))

  watch(activeMethodEffectKey, async () => {
    await runMethodEffect(activeMethod.value, {
      activeMethod: activeMethod.value,
      sessionId: props.sessionId,
      selectedVars: dialogSelectedVars.value,
      options: dialogOptions,
      runtime: methodRuntime,
    })
  }, { immediate: true })

  watch(activeMethodAutoSaveKey, (nextKey) => {
    clearMethodAutoSaveTimer()
    if (!nextKey) return
    methodAutoSaveTimer = setTimeout(async () => {
      methodAutoSaveTimer = null
      try {
        await runMethodAutoSave(activeMethod.value, {
          sessionId: props.sessionId,
          selectedVars: dialogSelectedVars.value,
          options: dialogOptions,
          runtime: methodRuntime,
          emit,
          loadPreview,
        })
        if (onPreviewMutated) onPreviewMutated()
      } catch (_) {
        // Ignore autosave failures so the dialog remains usable.
      }
    }, 600)
  })

  onBeforeUnmount(clearMethodAutoSaveTimer)

  function isVariableSelectable(variable) {
    const selector = activeMethodMeta.value?.isVariableSelectable
    if (!selector) return true
    return !!selector({ variable, variableMetaMap: variableMetaMap.value })
  }

  function resetDialogState() {
    dialogSelectedVars.value = []
    const nextDefaults = createDefaultDialogOptions()
    for (const key of Object.keys(dialogOptions)) {
      delete dialogOptions[key]
    }
    Object.assign(dialogOptions, nextDefaults)
    const nextRuntime = createDefaultMethodRuntime()
    for (const key of Object.keys(methodRuntime)) {
      delete methodRuntime[key]
    }
    Object.assign(methodRuntime, nextRuntime)
  }

  function openMethod(key) {
    if (!props.hasData) {
      alert('请先上传数据文件')
      return
    }
    activeMethod.value = key
    resetDialogState()
    dialogSelectedVars.value = getInitialSelection(key, { variables: props.variables })
  }

  function toggleDialogVar(variable) {
    if (!isVariableSelectable(variable)) {
      showVariableSelectionError()
      return
    }

    const idx = dialogSelectedVars.value.indexOf(variable.name)
    if (idx >= 0) {
      dialogSelectedVars.value.splice(idx, 1)
      return
    }

    if (activeMethodMeta.value?.selectionMode === 'single') {
      dialogSelectedVars.value = [variable.name]
      return
    }

    dialogSelectedVars.value.push(variable.name)
  }

  function removeDialogVar(name) {
    dialogSelectedVars.value = dialogSelectedVars.value.filter(n => n !== name)
  }

  function closeDialogOverlays() {
    clearMethodAutoSaveTimer()
    activeMethod.value = ''
  }

  async function executeProcess() {
    if (processing.value || !props.sessionId) return

    const method = activeMethod.value
    if (dialogSelectedVars.value.length < methodMinVars.value) {
      showError(methodMinVars.value > 1 ? `请至少选择 ${methodMinVars.value} 个变量` : '请先选择一个变量')
      return
    }
    const validationError = validateMethod(method, {
      options: dialogOptions,
      selectedVars: dialogSelectedVars.value,
      variableMetaMap: variableMetaMap.value,
    })
    if (validationError) {
      showError(validationError)
      return
    }
    const params = buildMethodParams(method, {
      options: dialogOptions,
      selectedVars: dialogSelectedVars.value,
      variableMetaMap: variableMetaMap.value,
    })

    processing.value = true
    try {
      const data = await api.processData(props.sessionId, method, params)
      if (data.success) {
        activeMethod.value = ''
        notifySuccess(data.message || '处理完成')
        if (onPreviewMutated) onPreviewMutated()
        await loadVersions()
        await loadPreview()
        emit('variables-updated')
      } else {
        alert('处理失败: ' + (data.error || '未知错误'))
      }
    } catch (e) {
      alert('处理失败: ' + e.message)
    }
    processing.value = false
  }

  function clearMethodAutoSaveTimer() {
    if (methodAutoSaveTimer) {
      clearTimeout(methodAutoSaveTimer)
      methodAutoSaveTimer = null
    }
  }

  function showError(message) {
    errorMsg.value = message
    setTimeout(() => { errorMsg.value = '' }, 2600)
  }

  function showVariableSelectionError() {
    if (activeMethod.value === 'label') {
      showError('数据标签仅支持定类变量')
    } else if (activeMethod.value === 'outlier') {
      showError('异常值处理仅支持无空值的定量变量')
    } else if (activeMethod.value === 'balance') {
      showError('样本均衡不支持含空值变量，请先进行缺失值处理')
    } else if (activeMethod.value === 'winsorize') {
      showError('缩尾/截尾处理仅支持无空值的定量变量')
    } else if (activeMethod.value === 'sliding_window') {
      showError('时序数据滑窗转换仅支持 1 个无空值定量变量')
    } else if (activeMethod.value === 'dummy') {
      showError('虚拟变量转换仅支持 1 个无空值定类变量')
    }
  }

  return {
    activeMethod,
    activeMethodComponent,
    activeMethodLabel,
    closeDialogOverlays,
    dialogHelpText,
    dialogOptions,
    dialogSelectedVars,
    encodeHintText,
    errorMsg,
    executeProcess,
    isVariableSelectable,
    labelEditable,
    labelHintText,
    methodActions,
    methodMinVars,
    methodNeedsMultiVar,
    methodRuntime,
    openMethod,
    processing,
    removeDialogVar,
    toggleDialogVar,
  }
}

function isLabelCompatible(variable) {
  return variable.type === 'categorical'
}
