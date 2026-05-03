import { defineAsyncComponent } from 'vue'
import * as api from '../api.js'
import {
  buildLabelRows,
  encodeCodeLabels,
  encodeCodeMap,
  encodeRangeMap,
  syncEncodeRows,
} from './methodValueHelpers.js'

const LabelMethod = defineAsyncComponent(() => import('./methods/LabelMethod.vue'))
const EncodeMethod = defineAsyncComponent(() => import('./methods/EncodeMethod.vue'))
const OutlierMethod = defineAsyncComponent(() => import('./methods/OutlierMethod.vue'))
const InvalidSampleMethod = defineAsyncComponent(() => import('./methods/InvalidSampleMethod.vue'))
const GenerateMethod = defineAsyncComponent(() => import('./methods/GenerateMethod.vue'))
const StandardizeMethod = defineAsyncComponent(() => import('./methods/StandardizeMethod.vue'))
const DummyMethod = defineAsyncComponent(() => import('./methods/DummyMethod.vue'))
const MissingMethod = defineAsyncComponent(() => import('./methods/MissingMethod.vue'))
const SlidingWindowMethod = defineAsyncComponent(() => import('./methods/SlidingWindowMethod.vue'))
const WinsorizeMethod = defineAsyncComponent(() => import('./methods/WinsorizeMethod.vue'))
const DownsampleMethod = defineAsyncComponent(() => import('./methods/DownsampleMethod.vue'))
const WeightMethod = defineAsyncComponent(() => import('./methods/WeightMethod.vue'))
const TransformMethod = defineAsyncComponent(() => import('./methods/TransformMethod.vue'))
const BalanceMethod = defineAsyncComponent(() => import('./methods/BalanceMethod.vue'))
const FeatureSelectMethod = defineAsyncComponent(() => import('./methods/FeatureSelectMethod.vue'))
const ReduceMethod = defineAsyncComponent(() => import('./methods/ReduceMethod.vue'))

export const methodDefinitions = [
  {
    key: 'label',
    label: '数据标签',
    component: LabelMethod,
    helpText: '为什么只支持定类变量？\n数据标签用于给分类编码绑定文字含义，适合性别、地区、学历、量表选项这类定类变量。它只影响展示，不改变原始数据和统计计算结果。\n定量变量本身已经有实际数值意义，比如年龄、收入、分数，因此不支持通过“数据标签”来处理。',
    selectionMode: 'single',
    minVars: 1,
    createOptions: () => ({
      labelMap: {},
    }),
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      label_map: options.labelMap,
    }),
    getInitialSelection: ({ variables }) => {
      const firstCategorical = (variables || []).find(variable => variable.type === 'categorical')
      return firstCategorical ? [firstCategorical.name] : []
    },
    getEffectKey: ({ activeMethod, selectedVars, sessionId }) => (
      activeMethod === 'label' && sessionId ? `label|${sessionId}|${selectedVars[0] || ''}` : ''
    ),
    async runEffect({ activeMethod, selectedVars, sessionId, options, runtime }) {
      if (activeMethod !== 'label' || selectedVars.length !== 1 || !sessionId) {
        runtime.labelRows = []
        options.labelMap = {}
        runtime.labelAutoSaveSuspended = false
        return
      }

      try {
        const data = await api.getVariableValues(sessionId, selectedVars[0])
        const rows = buildLabelRows(data)
        runtime.labelRows = rows
        runtime.labelAutoSaveSuspended = true
        const map = {}
        for (const row of rows) {
          map[row.value] = options.labelMap[row.value] || row.label || ''
        }
        options.labelMap = map
        setTimeout(() => { runtime.labelAutoSaveSuspended = false }, 0)
      } catch (_) {
        runtime.labelRows = []
        options.labelMap = {}
        runtime.labelAutoSaveSuspended = false
      }
    },
    getAutoSaveKey: ({ activeMethod, selectedVars, sessionId, options, runtime, variableMetaMap }) => {
      if (runtime.labelAutoSaveSuspended) return ''
      if (activeMethod !== 'label' || !sessionId || selectedVars.length !== 1) return ''
      const targetVar = variableMetaMap[selectedVars[0]]
      if (!targetVar || targetVar.type !== 'categorical') return ''
      const nextMap = options.labelMap || {}
      if (!Object.keys(nextMap).length) return ''
      return `label|${selectedVars[0]}|${JSON.stringify(nextMap)}`
    },
    async runAutoSave({ sessionId, selectedVars, options, emit, loadPreview }) {
      if (!sessionId || !selectedVars.length) return
      await api.processData(sessionId, 'label', {
        variables: [selectedVars[0]],
        label_map: options.labelMap,
      })
      emit('variables-updated')
      await loadPreview()
    },
    validate: ({ selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请先选择一个定类变量'
      const targetVar = variableMetaMap[selectedVars[0]]
      if (!targetVar || targetVar.type !== 'categorical') return '数据标签仅支持定类变量'
      return ''
    },
  },
  {
    key: 'encode',
    label: '数据编码',
    component: EncodeMethod,
    helpText: '将变量数值再次进行编码，可进一步浓缩或整合原始数据。支持新编码、范围编码和自动分组。新编码适合逐值重编码，范围编码适合按数值区间合并，自动分组适合按均值或分位数快速生成分组变量。输入为一项定量或定类变量，输出为对变量各取值重新编码后的结果。',
    selectionMode: 'single',
    minVars: 1,
    createOptions: () => ({
      encodeMode: 'new',
      encodeNewVar: true,
      encodeNewVarName: '',
      encodeRows: [],
      encodeRanges: [{ min: '', max: '', code: '1', label: '' }],
      encodeAutoStrategy: 'mean_2',
      encodeBins: 5,
    }),
    getActions: ({ options }) => ({
      addRange() {
        options.encodeRanges.push({
          min: '',
          max: '',
          code: String(options.encodeRanges.length + 1),
          label: '',
        })
      },
      removeRange(idx) {
        if (options.encodeRanges.length <= 1) return
        options.encodeRanges.splice(idx, 1)
      },
    }),
    getEffectKey: ({ activeMethod, selectedVars, sessionId, options }) => (
      activeMethod === 'encode' && sessionId
        ? `encode|${sessionId}|${selectedVars[0] || ''}|${options.encodeMode || ''}`
        : ''
    ),
    async runEffect({ activeMethod, selectedVars, sessionId, options, runtime }) {
      if (activeMethod !== 'encode' || selectedVars.length !== 1 || !sessionId) {
        runtime.encodeSourceValues = []
        runtime.encodeMeta.sampleSize = 0
        runtime.encodeMeta.recommendedGroups = 5
        return
      }

      try {
        const data = await api.getVariableValues(sessionId, selectedVars[0])
        runtime.encodeSourceValues = data.values || []
        runtime.encodeMeta.sampleSize = data.sample_size || 0
        runtime.encodeMeta.recommendedGroups = data.recommended_groups || 5
        if (!options.encodeBins || options.encodeBins < 2) {
          options.encodeBins = runtime.encodeMeta.recommendedGroups
        }
        syncEncodeRows(options, runtime.encodeSourceValues)
      } catch (_) {
        runtime.encodeSourceValues = []
        runtime.encodeMeta.sampleSize = 0
        runtime.encodeMeta.recommendedGroups = 5
      }
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      mode: options.encodeMode,
      new_var: options.encodeNewVar,
      new_var_name: options.encodeNewVarName,
      auto_strategy: options.encodeAutoStrategy,
      code_map: encodeCodeMap(options.encodeRows),
      code_labels: encodeCodeLabels(options.encodeRows),
      range_map: encodeRangeMap(options.encodeRanges),
      bins: options.encodeBins,
    }),
  },
  {
    key: 'outlier',
    label: '异常值处理',
    component: OutlierMethod,
    helpText: '异常值处理用于识别并排除偏离整体数据分布或超出合理范围的数据点。支持 3σ、IQR、MAD 三种自动识别方式，也支持自定义范围识别。输入为一项或多项定量变量，输出为将异常值置空，或将异常值填补为其它有效值。\n注意：异常值处理不支持含空值变量，请先完成缺失值处理；多列处理时各列独立判断、互不影响。',
    selectionMode: 'multi',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      outlierDetect: 'auto',
      outlierMethod: '3sigma',
      outlierAction: 'null',
      outlierReplace: '',
      outlierCustomVal: '',
      outlierMin: null,
      outlierMax: null,
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return '异常值处理仅支持定量变量'
        }
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }
      if (options.outlierDetect === 'custom') {
        if (options.outlierMin == null || options.outlierMax == null || options.outlierMin === '' || options.outlierMax === '') {
          return '自定义识别时请填写最小值和最大值'
        }
        if (Number(options.outlierMin) >= Number(options.outlierMax)) {
          return '自定义范围的最小值必须小于最大值'
        }
      }
      if (options.outlierAction === 'replace') {
        if (!options.outlierReplace) return '请选择异常值替换方式'
        if (options.outlierReplace === 'custom' && (options.outlierCustomVal === '' || options.outlierCustomVal == null)) {
          return '自定义替换时请输入替换值'
        }
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      detect: options.outlierDetect,
      method: options.outlierMethod,
      action: options.outlierAction,
      replace_with: options.outlierReplace,
      custom_val: options.outlierCustomVal,
      min_val: options.outlierMin,
      max_val: options.outlierMax,
    }),
  },
  {
    key: 'invalid_sample',
    label: '无效样本处理',
    component: InvalidSampleMethod,
    helpText: '无效样本处理用于对整行样本进行识别与管理，目的是排除重复、无效样本，使分析数据更符合研究预期。支持“相同数据出现 XX% 及以上”与“缺失比例出现 XX% 及以上”两类规则。输入为两项或以上的定量或定类变量，输出为删除无效样本，或生成标记变量（1 有效，0 无效）。\n注意：对于“相同数据出现 XX% 及以上”的识别，若变量为定类变量，实际上识别的是相同编码出现的比例，通常不建议直接对定类变量使用此规则。',
    selectionMode: 'multi',
    minVars: 2,
    createOptions: () => ({
      invalidMode: 'rule',
      invalidSameDigit: true,
      invalidSameDigitPct: 80,
      invalidMissing: false,
      invalidMissingPct: 50,
      invalidAction: 'mark',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length < 2) return '请至少选择 2 个变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || !['numeric', 'categorical'].includes(variable.type)) {
          return '无效样本处理仅支持定量变量或定类变量'
        }
      }
      if (options.invalidMode !== 'rule') {
        return '当前版本仅支持规则判断'
      }
      if (!options.invalidSameDigit && !options.invalidMissing) {
        return '请至少选择一种无效样本识别规则'
      }
      if (options.invalidSameDigit && (Number(options.invalidSameDigitPct) < 0 || Number(options.invalidSameDigitPct) > 100)) {
        return '相同数据出现比例必须在 0 到 100 之间'
      }
      if (options.invalidMissing && (Number(options.invalidMissingPct) < 0 || Number(options.invalidMissingPct) > 100)) {
        return '缺失比例必须在 0 到 100 之间'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      mode: options.invalidMode,
      same_digit: options.invalidSameDigit,
      same_digit_pct: options.invalidSameDigitPct,
      missing: options.invalidMissing,
      missing_pct: options.invalidMissingPct,
      action: options.invalidAction,
    }),
  },
  {
    key: 'generate',
    label: '生成变量',
    component: GenerateMethod,
    selectionMode: 'single',
    minVars: 1,
    createOptions: () => ({
      generateName: '',
      generateExpr: '',
    }),
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      name: options.generateName,
      expr: options.generateExpr,
    }),
  },
  {
    key: 'standardize',
    label: '数据标准化',
    component: StandardizeMethod,
    helpText: '数据标准化用于消除不同指标的量纲差异，并在需要时统一指标方向。支持 Min-Max、Z-score、总和归一化、中心化、均值化、区间化、初值化、最小值化、最大值化以及正向/负向/中间型/区间型指标处理。\n注意：数据标准化仅支持无空值定量变量。',
    selectionMode: 'multi',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      stdMethod: 'zscore',
      stdNewVar: true,
      stdIntervalMin: 0,
      stdIntervalMax: 1,
      stdBestValue: '',
      stdRangeMin: '',
      stdRangeMax: '',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return `变量 ${variableName} 不是定量变量，数据标准化仅支持定量变量`
        }
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }

      if (options.stdMethod === 'interval') {
        const lower = Number(options.stdIntervalMin)
        const upper = Number(options.stdIntervalMax)
        if (!Number.isFinite(lower) || !Number.isFinite(upper)) return '请为区间化填写合法的上下限'
        if (lower >= upper) return '区间化要求下限小于上限'
      }
      if (options.stdMethod === 'middle') {
        const bestValue = Number(options.stdBestValue)
        if (!Number.isFinite(bestValue)) return '请为中间型指标处理填写合法的理想值'
      }
      if (options.stdMethod === 'range') {
        const lower = Number(options.stdRangeMin)
        const upper = Number(options.stdRangeMax)
        if (!Number.isFinite(lower) || !Number.isFinite(upper)) return '请为区间型指标处理填写合法的理想区间'
        if (lower >= upper) return '区间型指标处理要求下限小于上限'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      method: options.stdMethod,
      new_var: options.stdNewVar,
      interval_min: options.stdIntervalMin,
      interval_max: options.stdIntervalMax,
      best_value: options.stdBestValue,
      range_min: options.stdRangeMin,
      range_max: options.stdRangeMax,
    }),
  },
  {
    key: 'dummy',
    label: '虚拟变量转换',
    component: DummyMethod,
    selectionMode: 'single',
    minVars: 1,
    helpText: '虚拟变量转换用于将无序定类变量转换为可参与回归或机器学习建模的数值型变量。支持独热编码和哑变量化两种形式。\n注意：虚拟变量转换仅支持 1 个无空值定类变量。独热编码会为每个类别生成一个 0/1 变量；哑变量化会少一列，未生成的那一类作为参照项。',
    isVariableSelectable: ({ variable }) => variable?.type === 'categorical' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      dummyMode: 'dummy',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length !== 1) return '虚拟变量转换要求且仅支持 1 个定类变量'
      const variable = variableMetaMap[selectedVars[0]]
      if (!variable || variable.type !== 'categorical') {
        return '虚拟变量转换仅支持定类变量'
      }
      if (Number(variable.missing || 0) > 0) {
        return `变量 ${selectedVars[0]} 含有空值，请先进行缺失值处理`
      }
      if (!['dummy', 'onehot'].includes(options.dummyMode)) {
        return '请选择哑变量化或独热编码'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      mode: options.dummyMode,
    }),
  },
  {
    key: 'missing',
    label: '缺失值处理',
    component: MissingMethod,
    helpText: '缺失值处理用于对空值进行剔除、标记或填补。支持按行列缺失比例/个数进行剔除标记，也支持统计量填充、规则填充、插值填充和模型填充。\n注意：定类变量与定量变量的填充方法不同。定类变量的统计量填充通常只适合众数；插值填充和模型填充通常仅支持定量变量。',
    selectionMode: 'multi',
    minVars: 1,
    createOptions: () => ({
      missingAction: 'fill',
      missingDropMode: 'row_ratio',
      missingDropThreshold: 50,
      missingDropAction: 'delete',
      missingAction: 'fill',
      missingFillCategory: 'stat',
      missingFill: 'mean',
      missingCustomVal: '',
      missingKnnK: 5,
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable) return `变量 ${variableName} 不存在`
      }

      if (options.missingAction === 'drop_mark') {
        const threshold = Number(options.missingDropThreshold)
        if (!Number.isFinite(threshold)) return '剔除阈值不合法'
        if (['row_ratio', 'col_ratio'].includes(options.missingDropMode) && (threshold < 0 || threshold > 100)) {
          return '缺失比例阈值必须在 0 到 100 之间'
        }
        if (['row_count', 'col_count'].includes(options.missingDropMode) && threshold < 1) {
          return '缺失个数阈值必须大于等于 1'
        }
        return ''
      }

      if (options.missingFillCategory === 'stat') {
        const usesNumericOnly = ['mean', 'median', 'plus_3sigma', 'minus_3sigma'].includes(options.missingFill)
        if (usesNumericOnly) {
          for (const variableName of selectedVars) {
            if (variableMetaMap[variableName]?.type !== 'numeric') {
              return `定类变量 ${variableName} 的统计填充仅支持众数填充`
            }
          }
        }
      }

      if (options.missingFillCategory === 'interpolate' || options.missingFillCategory === 'model') {
        for (const variableName of selectedVars) {
          if (variableMetaMap[variableName]?.type !== 'numeric') {
            return `${options.missingFillCategory === 'interpolate' ? '插值填充' : '模型填充'}仅支持定量变量，变量 ${variableName} 不符合要求`
          }
        }
      }

      if (options.missingFill === 'custom' && !String(options.missingCustomVal ?? '').length) {
        return '固定值 M 填充时请输入自定义值'
      }
      if (options.missingFill === 'knn') {
        const k = Number(options.missingKnnK)
        if (!Number.isInteger(k) || k < 1) return 'k 值必须为大于等于 1 的整数'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      action: options.missingAction,
      drop_mode: options.missingDropMode,
      drop_threshold: options.missingDropThreshold,
      drop_action: options.missingDropAction,
      fill_category: options.missingFillCategory,
      fill: options.missingFill,
      custom_val: options.missingCustomVal,
      knn_k: options.missingKnnK,
    }),
  },
  {
    key: 'sliding_window',
    label: '时序数据滑窗转换',
    component: SlidingWindowMethod,
    helpText: '时序数据滑窗转换用于将单一时间序列转换为可用于回归建模的数据。设定步阶后，系统会用前 N 个历史数据作为自变量 X1~XN，用当前值作为因变量 Y，从而将时间序列预测问题转换为监督学习问题。\n注意：时序数据滑窗转换仅支持 1 个无空值定量变量；转换后前几行会因凑不够前序窗口而为空，建模前不要直接对这些空行做数据填补。',
    selectionMode: 'single',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      windowSize: 3,
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length !== 1) return '时序数据滑窗转换要求且仅支持 1 个定量变量'
      const variable = variableMetaMap[selectedVars[0]]
      if (!variable || variable.type !== 'numeric') {
        return '时序数据滑窗转换仅支持定量变量'
      }
      if (Number(variable.missing || 0) > 0) {
        return `变量 ${selectedVars[0]} 含有空值，请先进行缺失值处理`
      }
      const windowSize = Number(options.windowSize)
      if (!Number.isInteger(windowSize) || windowSize < 1) {
        return '步阶必须为大于等于 1 的整数'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      window_size: options.windowSize,
    }),
  },
  {
    key: 'winsorize',
    label: '缩尾/截尾处理',
    component: WinsorizeMethod,
    helpText: '缩尾/截尾处理用于对连续变量尾部极端值进行处理。缩尾会把超出指定百分位范围的值替换为对应分位数；截尾可选择仅将极端值置空，或删除极端值所在整行样本。\n注意：缩尾/截尾处理不支持含空值变量，请先完成缺失值处理；多列处理中各列独立处理、互不影响。',
    selectionMode: 'multi',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      winsorizeMode: 'winsorize',
      winsorizeTrimAction: 'null',
      winsorizePercent: 5,
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return '缩尾/截尾处理仅支持定量变量'
        }
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }
      const percent = Number(options.winsorizePercent)
      if (!(percent > 0 && percent < 50)) {
        return '百分位必须大于 0 且小于 50'
      }
      if (options.winsorizeMode === 'trim' && !['null', 'row_delete'].includes(options.winsorizeTrimAction)) {
        return '请选择截尾处理方式'
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      mode: options.winsorizeMode,
      trim_action: options.winsorizeTrimAction,
      percent: options.winsorizePercent,
    }),
  },
  {
    key: 'downsample',
    label: '数据降采样',
    component: DownsampleMethod,
    helpText: '数据降采样用于按固定规则减少样本数量，同时尽量保留原始数据中的关键趋势和模式。支持固定间隔的直接采样，以及基于分组统计量的稀释采样。\n注意：系统会按每 N 个样本分为一组，若最后一组样本数量不足 N，则该组会被直接剔除。',
    selectionMode: 'multi',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric',
    createOptions: () => ({
      downsampleMode: 'direct',
      downsampleFactor: 10,
      downsamplePosition: 1,
      downsampleAggregate: 'mean',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return `变量 ${variableName} 不是定量变量，数据降采样仅支持定量变量`
        }
      }
      const factor = Number(options.downsampleFactor)
      if (!Number.isInteger(factor) || factor < 1) return '降采样因子必须为大于等于 1 的整数'
      if (options.downsampleMode === 'direct') {
        const position = Number(options.downsamplePosition)
        if (!Number.isInteger(position) || position < 1 || position > factor) {
          return '采样位置必须在 1 到降采样因子之间'
        }
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      mode: options.downsampleMode,
      factor: options.downsampleFactor,
      position: options.downsamplePosition,
      aggregate: options.downsampleAggregate,
    }),
  },
  {
    key: 'weight',
    label: '样本加权',
    component: WeightMethod,
    selectionMode: 'single',
    minVars: 1,
    createOptions: () => ({
      weightVar: '',
    }),
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      weight_var: options.weightVar,
    }),
  },
  {
    key: 'transform',
    label: '数据变换',
    component: TransformMethod,
    helpText: '数据变换用于将原始定量变量转换为更适合分析的形式。支持傅里叶变换、傅里叶逆变换、Box-Cox、Box-Cox 逆变换、连续小波、离散小波、Johnson 和 Yeo-Johnson 变换。\n注意：数据变换仅支持 1 个无空值定量变量；Box-Cox 更适合正值数据，Yeo-Johnson 支持零值和负值。',
    selectionMode: 'single',
    minVars: 1,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      transformMethod: 'boxcox',
      transformNewVar: true,
      transformLambda: '',
      transformShift: 0,
      transformWavelet: 'morl',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length !== 1) return '数据变换要求且仅支持 1 个定量变量'
      const variable = variableMetaMap[selectedVars[0]]
      if (!variable || variable.type !== 'numeric') {
        return '数据变换仅支持定量变量'
      }
      if (Number(variable.missing || 0) > 0) {
        return `变量 ${selectedVars[0]} 含有空值，请先进行缺失值处理`
      }
      if (options.transformMethod === 'inverse_boxcox') {
        if (options.transformLambda !== '' && !Number.isFinite(Number(options.transformLambda))) {
          return 'Box-Cox 逆变换的 lambda 不合法'
        }
        if (!Number.isFinite(Number(options.transformShift))) {
          return 'Box-Cox 逆变换的平移常数不合法'
        }
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      method: options.transformMethod,
      new_var: options.transformNewVar,
      lambda: options.transformLambda,
      shift: options.transformShift,
      wavelet: options.transformWavelet,
    }),
  },
  {
    key: 'balance',
    label: '样本均衡',
    component: BalanceMethod,
    helpText: '样本均衡用于处理分类任务中因变量不同类别样本数量不均衡的问题。支持过采样、欠采样和组合采样三种方式，使不同类别样本数量尽量接近。\n注意：样本均衡不支持含空值变量，请先完成缺失值处理。',
    selectionMode: 'multi',
    minVars: 1,
    isVariableSelectable: ({ variable }) => Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      balanceTarget: '',
      balanceMethod: 'oversample',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (!selectedVars.length) return '请至少选择 1 个变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable) return `变量 ${variableName} 不存在`
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }
      if (!options.balanceTarget) return '请选择目标变量（分类变量）'
      const targetVar = variableMetaMap[options.balanceTarget]
      if (!targetVar || targetVar.type !== 'categorical') {
        return '目标变量必须为定类变量'
      }
      if (Number(targetVar.missing || 0) > 0) {
        return `目标变量 ${options.balanceTarget} 含有空值，请先进行缺失值处理`
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      target: options.balanceTarget,
      method: options.balanceMethod,
    }),
  },
  {
    key: 'feature_select',
    label: '特征筛选',
    component: FeatureSelectMethod,
    helpText: '特征筛选用于从多个候选特征中识别更有效的变量。它会在变量名后标明“应保留”或“应剔除”，适合特征较多、希望减少噪声和过拟合风险的场景。',
    selectionMode: 'multi',
    minVars: 2,
    createOptions: () => ({
      featureMethod: 'random_forest',
      featureTarget: '',
      featureKeepCount: 5,
      featureVarianceThreshold: 0.01,
      featureVifThreshold: 5,
    }),
    isVariableSelectable: ({ variable }) => (
      variable.type === 'numeric' && Number(variable.missing || 0) === 0
    ),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length < 2) return '请至少选择 2 个无空值定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return `变量 ${variableName} 不是定量变量，特征筛选仅支持定量变量`
        }
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }

      if (options.featureMethod === 'variance') {
        if (Number(options.featureVarianceThreshold) < 0) return '方差阈值不能小于 0'
        return ''
      }
      if (options.featureMethod === 'vif') {
        if (Number(options.featureVifThreshold) <= 1) return 'VIF 阈值必须大于 1'
        return ''
      }

      if (!options.featureTarget) return '请选择目标变量'
      if (selectedVars.includes(options.featureTarget)) return '目标变量不能与待筛选特征重复'
      const targetVar = variableMetaMap[options.featureTarget]
      if (!targetVar) return '目标变量不存在'
      if (Number(targetVar.missing || 0) > 0) {
        return `目标变量 ${options.featureTarget} 含有空值，请先进行缺失值处理`
      }
      if (options.featureMethod === 'pearson' && targetVar.type !== 'numeric') {
        return '相关系数法要求目标变量为定量变量'
      }
      if (options.featureMethod === 'chi2' && targetVar.type !== 'categorical') {
        return '卡方检验法要求目标变量为定类变量'
      }

      const keepCount = Number(options.featureKeepCount)
      if (!Number.isInteger(keepCount) || keepCount <= 0) return '目标维度必须为大于 0 的整数'
      if (keepCount > selectedVars.length) return '目标维度不能超过待筛选特征数量'
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      method: options.featureMethod,
      target: options.featureTarget,
      keep_count: options.featureKeepCount,
      variance_threshold: options.featureVarianceThreshold,
      vif_threshold: options.featureVifThreshold,
    }),
  },
  {
    key: 'reduce',
    label: '数据降维',
    component: ReduceMethod,
    helpText: '数据降维用于将原始高维特征映射到更少维度的变量中，以减少冗余和噪声，同时尽量保留原始数据中的主要信息。支持 PCA、LDA、ISOMap、LLE、KPCA 和 t-SNE。\n注意：数据降维仅支持无空值定量变量；其中 LDA 需要额外选择一个无空值定类目标变量。',
    selectionMode: 'multi',
    minVars: 2,
    isVariableSelectable: ({ variable }) => variable?.type === 'numeric' && Number(variable?.missing || 0) === 0,
    createOptions: () => ({
      reduceMethod: 'pca',
      reducePcaMode: 'variance_ratio',
      reduceVarianceRatio: 0.8,
      reduceComponents: 2,
      reduceTarget: '',
      reduceNeighbors: 5,
      reduceKernel: 'rbf',
    }),
    validate: ({ options, selectedVars, variableMetaMap }) => {
      if (selectedVars.length < 2) return '请至少选择 2 个无空值定量变量'
      for (const variableName of selectedVars) {
        const variable = variableMetaMap[variableName]
        if (!variable || variable.type !== 'numeric') {
          return `变量 ${variableName} 不是定量变量，数据降维仅支持定量变量`
        }
        if (Number(variable.missing || 0) > 0) {
          return `变量 ${variableName} 含有空值，请先进行缺失值处理`
        }
      }

      if (options.reduceMethod === 'pca') {
        if (options.reducePcaMode === 'variance_ratio') {
          const ratio = Number(options.reduceVarianceRatio)
          if (!(ratio > 0 && ratio < 1)) return '总方差解释率必须在 0 到 1 之间'
        } else {
          const count = Number(options.reduceComponents)
          if (!Number.isInteger(count) || count < 1) return '主成分个数必须为大于等于 1 的整数'
          if (count >= selectedVars.length) return '主成分个数必须小于原始变量数'
        }
      } else {
        const count = Number(options.reduceComponents)
        if (!Number.isInteger(count) || count < 1) return '降维后变量个数必须为大于等于 1 的整数'
        if (count >= selectedVars.length && options.reduceMethod !== 'lda') return '降维后变量个数必须小于原始变量数'
      }

      if (['isomap', 'lle', 'tsne'].includes(options.reduceMethod)) {
        const neighbors = Number(options.reduceNeighbors)
        if (!Number.isInteger(neighbors) || neighbors < 2) return '邻居数必须为大于等于 2 的整数'
      }

      if (options.reduceMethod === 'lda') {
        if (!options.reduceTarget) return '请选择目标变量（分类变量）'
        if (selectedVars.includes(options.reduceTarget)) return '目标变量不能与待降维特征重复'
        const targetVar = variableMetaMap[options.reduceTarget]
        if (!targetVar || targetVar.type !== 'categorical') return 'LDA 要求目标变量为定类变量'
        if (Number(targetVar.missing || 0) > 0) {
          return `目标变量 ${options.reduceTarget} 含有空值，请先进行缺失值处理`
        }
      }
      return ''
    },
    buildParams: ({ options, selectedVars }) => ({
      variables: selectedVars,
      components: options.reduceComponents,
      method: options.reduceMethod,
      pca_mode: options.reducePcaMode,
      variance_ratio: options.reduceVarianceRatio,
      target: options.reduceTarget,
      n_neighbors: options.reduceNeighbors,
      kernel: options.reduceKernel,
    }),
  },
]
