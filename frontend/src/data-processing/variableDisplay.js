export function getVarTypeLabel(variable) {
  if (variable.type === 'numeric') return '定量'
  if (variable.type === 'categorical') return '定类'
  return '字符'
}

export function getVarTagClass(variable) {
  return variable.type === 'numeric' ? 'dp-tag-quant' : 'dp-tag-cat'
}
