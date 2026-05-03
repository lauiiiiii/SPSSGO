export const MAX_PREVIEW_ROWS = 200

export function columnLetter(index) {
  let result = ''
  let current = index
  while (current >= 0) {
    result = String.fromCharCode(65 + (current % 26)) + result
    current = Math.floor(current / 26) - 1
  }
  return result
}

export function isCellNumber(value) {
  if (!value || value === '') return false
  return !Number.isNaN(Number(value)) && String(value).trim() !== ''
}

export function workbookToPreviewSheets(workbook, sheetToJson, maxRows = MAX_PREVIEW_ROWS) {
  const sheets = []
  let totalRows = 0

  for (const name of workbook.SheetNames) {
    const worksheet = workbook.Sheets[name]
    const jsonData = sheetToJson(worksheet, { header: 1, defval: '' })
    const sheet = sheetRowsToPreview(name, jsonData, maxRows)
    if (sheets.length === 0) {
      totalRows = Math.max(0, jsonData.length - 1)
    }
    sheets.push(sheet)
  }

  return { sheets, totalRows }
}

export function sheetRowsToPreview(name, jsonData, maxRows = MAX_PREVIEW_ROWS) {
  if (!jsonData.length) return { name, headers: [], rows: [] }

  const rawHeaders = jsonData[0]
  let lastNonEmpty = rawHeaders.length - 1
  while (lastNonEmpty >= 0 && (rawHeaders[lastNonEmpty] === '' || rawHeaders[lastNonEmpty] == null)) {
    lastNonEmpty--
  }

  const colCount = lastNonEmpty + 1
  if (colCount === 0) return { name, headers: [], rows: [] }

  const headers = rawHeaders.slice(0, colCount).map(header => String(header))
  const rows = jsonData.slice(1, maxRows + 1).map(row => {
    const cells = row.slice(0, colCount).map(cell => cell === null || cell === undefined ? '' : String(cell))
    while (cells.length < colCount) cells.push('')
    return cells
  })

  while (rows.length > 0 && rows[rows.length - 1].every(cell => cell === '')) {
    rows.pop()
  }

  return { name, headers, rows }
}
