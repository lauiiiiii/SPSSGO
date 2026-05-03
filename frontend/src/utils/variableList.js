export function filterVariables({ variables, usedVars, typeFilter, query }) {
  let list = (variables || []).filter(variable => !usedVars.has(variable.name))
  if (typeFilter && typeFilter !== 'all') {
    list = list.filter(variable => variable.type === typeFilter)
  }
  const normalizedQuery = String(query || '').trim().toLowerCase()
  if (normalizedQuery) {
    list = list.filter(variable => (
      String(variable.name).toLowerCase().includes(normalizedQuery) ||
      String(variable.display_name || '').toLowerCase().includes(normalizedQuery)
    ))
  }
  return list
}

export function getShiftRangeNames(variables, fromIndex, toIndex) {
  if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return []
  const start = Math.min(fromIndex, toIndex)
  const end = Math.max(fromIndex, toIndex)
  return variables.slice(start, end + 1).map(variable => variable.name)
}

export function buildVariableDragPayload(variableName, selectedVars) {
  const isSelected = selectedVars.includes(variableName)
  return isSelected && selectedVars.length > 1
    ? selectedVars.join(',')
    : variableName
}

export function positionVariableMenu(rect, options = {}) {
  const menuWidth = options.width || 150
  const menuHeight = options.height || 190
  return {
    top: Math.min(window.innerHeight - menuHeight, Math.max(8, rect.top - 8)),
    left: Math.min(window.innerWidth - menuWidth - 8, rect.right + 8),
  }
}
