export function buildVariableMetaMap(variables) {
  const map = {}
  for (const variable of variables || []) {
    if (variable && variable.name) map[variable.name] = variable
  }
  return map
}

export function sortVariableNamesByLength(variableMetaMap) {
  return Object.keys(variableMetaMap || {}).sort((a, b) => b.length - a.length)
}

export function createResultDisplayFormatter(variableMetaMap) {
  const variableNamesByLength = sortVariableNamesByLength(variableMetaMap)

  function getVariableDisplayName(name) {
    if (name == null) return ''
    return (variableMetaMap[name] && variableMetaMap[name].display_name) || String(name)
  }

  function formatText(value) {
    if (value == null) return ''
    if (typeof value !== 'string') return value
    let text = value
    for (const name of variableNamesByLength) {
      const displayName = getVariableDisplayName(name)
      if (displayName && displayName !== name) {
        text = text.split(name).join(displayName)
      }
    }
    return text
  }

  function formatCell(cell) {
    if (typeof cell === 'string') return formatText(cell)
    if (cell == null) return ''
    return cell
  }

  function normalizeSection(section) {
    const normalized = { ...section }
    normalized.title = formatText(section?.title || '')
    if (section?.type === 'table') {
      normalized.headers = (section.headers || []).map(formatCell)
      normalized.rows = (section.rows || []).map(row => (row || []).map(formatCell))
      normalized.note = formatText(section.note || '')
      normalized.description = formatText(section.description || '')
    } else if (section && (section.type === 'advice' || section.type === 'smart_analysis')) {
      normalized.content = formatText(section.content || '')
    } else if (section?.type === 'references') {
      normalized.items = (section.items || []).map(formatText)
    } else if (section?.type === 'charts') {
      normalized.description = formatText(section.description || '')
      normalized.charts = (section.charts || []).map(chart => ({
        ...chart,
        title: formatText(chart?.title || ''),
        varName: formatText(chart?.varName || ''),
      }))
    }
    return normalized
  }

  function normalizeResult(result) {
    return {
      name: formatText(result?.name || ''),
      description: formatText(result?.description || ''),
      headers: (result?.headers || []).map(formatCell),
      rows: (result?.rows || []).map(row => (row || []).map(formatCell)),
      sections: (result?.sections || []).map(normalizeSection),
    }
  }

  return {
    formatCell,
    formatText,
    normalizeResult,
    normalizeSection,
  }
}
