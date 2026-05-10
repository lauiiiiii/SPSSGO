export function normalizeMethodMetaMap(rawMethods) {
  const methods = { ...(rawMethods || {}) }
  const ensureSlotMethod = (key, patch) => {
    if (!methods[key]) {
      methods[key] = patch
      return
    }
    methods[key] = { ...methods[key], ...patch }
  }

  ensureSlotMethod('data_overview', {
    label: '数据探查',
    category: '常用方法',
    description: '全面检查数据集规模、变量类型、缺失与异常，评估数据可用度',
    order: 60,
    slots: Array.isArray(methods.data_overview?.slots) && methods.data_overview.slots.length
      ? methods.data_overview.slots
      : [
          { key: 'variables', label: '变量', type: 'multiple', accept: 'any', min: 1, hint: '放入需要探查的一个或多个变量' },
        ],
    options: methods.data_overview?.options || [],
    param_builder: methods.data_overview?.param_builder || 'direct',
  })

  ensureSlotMethod('frequency', {
    label: methods.frequency?.label || '频数分析',
    category: methods.frequency?.category || '常用方法',
    description: methods.frequency?.description || '统计各类别的频次和百分比分布',
    order: methods.frequency?.order ?? 10,
    slots: [
      { key: 'variables', label: '分析变量', type: 'multiple', accept: 'any', min: 1, hint: '放入需要统计频次的一个或多个变量' },
    ],
    options: methods.frequency?.options || [],
    param_builder: methods.frequency?.param_builder || 'direct',
  })

  ensureSlotMethod('cross_tabulation', {
    label: methods.cross_tabulation?.label || '卡方（交叉）分析',
    category: methods.cross_tabulation?.category || '常用方法',
    description: methods.cross_tabulation?.description || '用于探索多组变量之间交叉列联分布和关联强度',
    order: methods.cross_tabulation?.order ?? 20,
    slots: [
      { key: 'group_var', label: '变量', prefixLabel: '分组', type: 'single', accept: 'any', hint: '放入 1 个分组变量' },
      { key: 'variables', label: '变量X', type: 'multiple', accept: 'any', min: 1, hint: '放入 1 个或多个需要交叉分析的 X 变量' },
    ],
    options: methods.cross_tabulation?.options?.length
      ? methods.cross_tabulation.options
      : [
          {
            key: 'percent_base',
            label: '占比口径',
            choices: ['百分数(按列)', '百分数(按行)'],
            default: '百分数(按列)',
          },
        ],
    param_builder: methods.cross_tabulation?.param_builder || 'direct',
  })

  ensureSlotMethod('confirmatory_factor_analysis', {
    label: '验证性因子分析',
    category: methods.confirmatory_factor_analysis?.category || '问卷分析包',
    description: '支持多因子测量模型的验证性因子分析，可分别放入多个因子题项',
    order: methods.confirmatory_factor_analysis?.order || 80,
    slots: Array.isArray(methods.confirmatory_factor_analysis?.slots) && methods.confirmatory_factor_analysis.slots.length
      ? methods.confirmatory_factor_analysis.slots.slice(0, 1)
      : [
          { key: 'factor1_vars', label: '因子1题项', type: 'multiple', accept: 'numeric', min: 2, hint: '放入因子1对应的题项' },
        ],
    options: methods.confirmatory_factor_analysis?.options || [],
    param_builder: methods.confirmatory_factor_analysis?.param_builder || 'direct',
  })

  return methods
}
