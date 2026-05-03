const defaultHint = [
  { text: '拖入 ' },
  { text: '定量', className: 'dp-tag-quant' },
  { text: ' 或 ' },
  { text: '定类', className: 'dp-tag-cat' },
  { text: ' 变量' },
]

const selectionHints = {
  outlier: [
    { text: '拖入 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
  invalid_sample: [
    { text: '拖入至少 2 个 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 或 ' },
    { text: '定类', className: 'dp-tag-cat' },
    { text: ' 变量' },
  ],
  balance: [
    { text: '拖入至少 1 个无空值变量，并在右侧选择分类目标变量' },
  ],
  standardize: [
    { text: '拖入至少 1 个无空值 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
  winsorize: [
    { text: '拖入至少 1 个无空值 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
  sliding_window: [
    { text: '拖入 1 个无空值 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
  dummy: [
    { text: '拖入 1 个无空值 ' },
    { text: '定类', className: 'dp-tag-cat' },
    { text: ' 变量' },
  ],
  feature_select: [
    { text: '拖入至少 2 个无空值 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
  reduce: [
    { text: '拖入至少 2 个无空值 ' },
    { text: '定量', className: 'dp-tag-quant' },
    { text: ' 变量' },
  ],
}

export function getSelectionHintSegments(methodKey) {
  return selectionHints[methodKey] || defaultHint
}
