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

  ensureSlotMethod('post_hoc_multiple_comparison', {
    label: methods.post_hoc_multiple_comparison?.label || '事后多重比较',
    category: methods.post_hoc_multiple_comparison?.category || '差异对比分析包',
    description: methods.post_hoc_multiple_comparison?.description || '在方差分析显著后，对组间差异进行事后多重比较',
    order: methods.post_hoc_multiple_comparison?.order ?? 35,
    slots: [
      { key: 'group_var', label: '分组变量', type: 'single', accept: 'categorical', hint: '放入分组变量（3组及以上）' },
      { key: 'test_vars', label: '检验变量', type: 'multiple', accept: 'numeric', min: 1, hint: '放入需要比较的定量变量' },
    ],
    options: [
      {
        key: 'method',
        label: '比较方法',
        choices: [
          'LSD方法(默认)',
          'Scheffe',
          'Tukey',
          'Bonferroni校正',
          'sidak',
          'Tamhane T2(方差不齐)',
          'SNK Q检验',
          'Duncan检验',
          'Games-Howell(方差不齐)',
        ],
        default: 'LSD方法(默认)',
      },
      {
        key: 'use_letters',
        label: '字母标记法',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'include_effect_size',
        label: '效应量',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'show_p_marks',
        label: 'P值标识',
        type: 'checkbox',
        default: true,
      },
      ...(methods.post_hoc_multiple_comparison?.options || [])
        .filter(option => !['method', 'use_letters', 'include_effect_size', 'show_p_marks'].includes(option.key)),
    ],
    param_builder: methods.post_hoc_multiple_comparison?.param_builder || 'direct',
  })

  ensureSlotMethod('two_way_anova', {
    label: methods.two_way_anova?.label || '双因素方差分析',
    category: methods.two_way_anova?.category || '差异对比分析包',
    description: methods.two_way_anova?.description || '检验两个分类因素及其交互作用对因变量的影响',
    order: methods.two_way_anova?.order ?? 40,
    slots: [
      { key: 'factors', label: '分组变量X', type: 'multiple', accept: 'categorical', min: 2, max: 2, hint: '放入2个分组因素' },
      { key: 'dependent', label: '因变量Y', type: 'single', accept: 'numeric', hint: '放入因变量' },
      { key: 'covariates', label: '协变量', type: 'multiple', accept: 'numeric', min: 0, hint: '可选，放入需要控制的协变量' },
    ],
    options: [
      {
        key: 'include_interaction',
        label: '分析交互效应',
        type: 'checkbox',
        default: true,
      },
      {
        key: 'do_post_hoc',
        label: '事后多重比较',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'post_hoc_method',
        label: '方法选择',
        choices: ['LSD', 'bonf', 'sidak'],
        default: 'LSD',
      },
      ...(methods.two_way_anova?.options || [])
        .filter(option => !['include_interaction', 'do_post_hoc', 'post_hoc_method'].includes(option.key)),
    ],
    param_builder: methods.two_way_anova?.param_builder || 'direct',
  })

  ensureSlotMethod('three_way_anova', {
    label: methods.three_way_anova?.label || '三因素方差分析',
    category: methods.three_way_anova?.category || '差异对比分析包',
    description: methods.three_way_anova?.description || '检验三个分类因素及其交互作用对因变量的影响',
    order: methods.three_way_anova?.order ?? 45,
    slots: [
      { key: 'factors', label: '分组变量X', type: 'multiple', accept: 'categorical', min: 3, max: 3, hint: '放入3个分组因素' },
      { key: 'dependent', label: '因变量Y', type: 'single', accept: 'numeric', hint: '放入因变量' },
      { key: 'covariates', label: '协变量', type: 'multiple', accept: 'numeric', min: 0, hint: '可选，放入需要控制的协变量' },
    ],
    options: [
      {
        key: 'include_interaction',
        label: '分析交互效应',
        type: 'checkbox',
        default: true,
      },
      {
        key: 'second_order_interaction',
        label: '二阶交互效应',
        type: 'checkbox',
        default: true,
      },
      {
        key: 'third_order_interaction',
        label: '三阶交互效应',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'include_effect_size',
        label: '效应量',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'do_post_hoc',
        label: '事后多重比较',
        type: 'checkbox',
        default: false,
      },
      {
        key: 'post_hoc_method',
        label: '方法选择',
        choices: ['LSD', 'Tukey法', 'Bonferroni校正', 'Sidak法'],
        default: 'LSD',
      },
      ...(methods.three_way_anova?.options || [])
        .filter(option => !['include_interaction', 'second_order_interaction', 'third_order_interaction', 'include_effect_size', 'do_post_hoc', 'post_hoc_method'].includes(option.key)),
    ],
    param_builder: methods.three_way_anova?.param_builder || 'direct',
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
