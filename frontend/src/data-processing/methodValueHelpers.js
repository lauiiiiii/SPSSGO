export function encodeCodeMap(rows) {
  return Object.fromEntries(
    (rows || [])
      .map(row => [row.source, row.code])
      .filter(pair => pair[1] !== '')
  )
}

export function encodeCodeLabels(rows) {
  return Object.fromEntries(
    (rows || [])
      .map(row => [row.code, row.label])
      .filter(pair => pair[0] !== '' && pair[0] != null && pair[1] !== '')
  )
}

export function encodeRangeMap(ranges) {
  return (ranges || [])
    .filter(row => row.min !== '' && row.max !== '' && row.code !== '')
    .map(row => ({ min: row.min, max: row.max, code: row.code, label: row.label }))
}

export function buildLabelRows(data) {
  const valueLabels = data?.value_labels || {}
  const labelKeys = Object.keys(valueLabels)
  if (labelKeys.length) {
    return sortLabelKeys(labelKeys).map(key => ({
      value: String(key),
      label: valueLabels[key] || '',
    }))
  }

  const values = (data?.values || []).map(value => String(value))
  const looksNumeric = values.length > 0 && values.every(value => value !== '' && !Number.isNaN(Number(value)))
  if (looksNumeric) {
    return values.map(value => ({
      value,
      label: '',
    }))
  }

  return values.map((value, index) => ({
    value: String(index + 1),
    label: value,
  }))
}

export function syncEncodeRows(options, sourceValues) {
  if (options.encodeMode !== 'new') {
    if (options.encodeMode === 'range' && !options.encodeRanges.length) {
      options.encodeRanges = [{ min: '', max: '', code: '1', label: '' }]
    }
    return
  }

  options.encodeRows = (sourceValues || []).map((value, index) => {
    const normalizedValue = String(value)
    const existing = options.encodeRows.find(row => String(row.source) === normalizedValue)
    return {
      source: normalizedValue,
      code: existing ? existing.code : String(index + 1),
      label: existing ? existing.label : '',
    }
  })
}

function sortLabelKeys(keys) {
  return [...keys].sort((a, b) => {
    const na = Number(a)
    const nb = Number(b)
    const aIsNum = !Number.isNaN(na)
    const bIsNum = !Number.isNaN(nb)
    if (aIsNum && bIsNum) return na - nb
    if (aIsNum) return -1
    if (bIsNum) return 1
    return String(a).localeCompare(String(b), 'zh-CN')
  })
}
