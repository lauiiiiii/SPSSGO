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
    label: '数据概览',
    category: '数据概览',
    description: '快速查看数据集规模、变量类型、缺失情况和变量明细',
    order: 60,
    slots: Array.isArray(methods.data_overview?.slots) && methods.data_overview.slots.length
      ? methods.data_overview.slots
      : [
          { key: 'variables', label: '变量', type: 'multiple', accept: 'any', min: 1, hint: '放入需要概览的一个或多个变量' },
        ],
    options: methods.data_overview?.options || [],
    param_builder: methods.data_overview?.param_builder || 'direct',
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
