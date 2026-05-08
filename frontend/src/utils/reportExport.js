// 这里只放分析结果导出和复制的富文本组装，别把页面交互塞进来。
// 复制链路要优先兼容 Word/WPS，别再回到“网页表格看着像，粘过去就变形”的老路。

const TABLE_COPY_STYLE = 'padding:8px 12px;text-align:center;vertical-align:middle;font-size:10.5pt;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;color:#000'
const EXPORT_CELL_STYLE = 'padding:6px 10px;text-align:center;font-size:10.5pt;font-family:"Times New Roman","宋体",serif;border:1px solid #ccc'
const RTF_TABLE_WIDTH = 9000
const RTF_TABLE_FONT_SIZE = 21
const RTF_BODY_FONT_SIZE = 24
const RTF_TITLE_FONT_SIZE = 28
const RTF_SECTION_TITLE_SIZE = 24
const RTF_NOTE_FONT_SIZE = 20
const RTF_LINE_TOP = 24
const RTF_LINE_MIDDLE = 12
const RTF_LINE_BOTTOM = 24
const RTF_FONT_SWITCH = '\\loch\\f0\\hich\\f0\\dbch\\f1'
const HTML_TABLE_FONT = 'font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;font-size:10.5pt;color:#000'

function normalizeCopyPayload(payloadOrHtml, plain) {
  if (payloadOrHtml && typeof payloadOrHtml === 'object' && ('html' in payloadOrHtml || 'plain' in payloadOrHtml || 'rtf' in payloadOrHtml)) {
    return {
      rtf: String(payloadOrHtml.rtf || ''),
      html: String(payloadOrHtml.html || ''),
      plain: String(payloadOrHtml.plain || ''),
    }
  }
  return {
    rtf: '',
    html: String(payloadOrHtml || ''),
    plain: String(plain || ''),
  }
}

function buildClipboardItemData(payload, includeRtf) {
  const item = {}
  if (includeRtf && payload.rtf) item['text/rtf'] = new Blob([payload.rtf], { type: 'text/rtf' })
  if (payload.html) item['text/html'] = new Blob([payload.html], { type: 'text/html' })
  if (payload.plain) item['text/plain'] = new Blob([payload.plain], { type: 'text/plain' })
  return item
}

export async function writeRichClipboard(payloadOrHtml, plain) {
  const payload = normalizeCopyPayload(payloadOrHtml, plain)
  try {
    if (navigator.clipboard && typeof navigator.clipboard.write === 'function' && typeof ClipboardItem !== 'undefined') {
      const fullPayload = buildClipboardItemData(payload, true)
      if (Object.keys(fullPayload).length) {
        try {
          await navigator.clipboard.write([new ClipboardItem(fullPayload)])
          return true
        } catch {
          // 有些浏览器对 text/rtf 挑剔得很，先退到 html/plain，别把主流程卡死。
        }
      }
      const fallbackPayload = buildClipboardItemData(payload, false)
      if (Object.keys(fallbackPayload).length) {
        await navigator.clipboard.write([new ClipboardItem(fallbackPayload)])
        return true
      }
    }
  } catch {
    // 富文本剪贴板各家实现不统一，失败就降级，不和它硬碰硬。
  }
  try {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(payload.plain)
      return true
    }
  } catch {
    // 这里别直接放弃，execCommand 虽老，但很多环境还能救命。
  }
  return fallbackCopyText(payload.plain)
}

function createRichPayloadBuilder() {
  return { html: '', plain: '', rtf: '' }
}

function appendHtmlParagraph(builder, text, style = '') {
  if (!text) return
  builder.html += `<p style="${style}">${toHtmlText(text)}</p>`
}

function appendPlainParagraph(builder, text, suffix = '\n\n') {
  if (!text) return
  builder.plain += `${text}${suffix}`
}

function appendRtfParagraph(builder, text, options = {}) {
  if (!text) return
  builder.rtf += buildRtfParagraph(text, options)
}

function finalizeRichPayload(builder) {
  return {
    html: builder.html,
    plain: builder.plain,
    rtf: wrapRtfDocument(builder.rtf),
  }
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function toHtmlText(value) {
  return escapeHtml(value).replace(/\n/g, '<br>')
}

function escapeRtfText(value) {
  let result = ''
  for (const ch of String(value ?? '')) {
    const code = ch.codePointAt(0)
    if (ch === '\\' || ch === '{' || ch === '}') {
      result += `\\${ch}`
    } else if (ch === '\n') {
      result += '\\line '
    } else if (ch === '\t') {
      result += '\\tab '
    } else if (code > 127) {
      if (code <= 0xffff) {
        const signed = code > 0x7fff ? code - 0x10000 : code
        result += `\\u${signed}?`
      } else {
        result += '?'
      }
    } else {
      result += ch
    }
  }
  return result
}

function wrapRtfDocument(content) {
  return [
    '{\\rtf1\\ansi\\deff0\\uc1',
    '{\\fonttbl{\\f0 Times New Roman;}{\\f1 SimSun;}}',
    '{\\colortbl;\\red0\\green0\\blue0;}',
    '\\viewkind4\\paperw11907\\paperh16840\\margl1800\\margr1800\\margt1440\\margb1440',
    content,
    '}',
  ].join('')
}

function buildRtfParagraph(text, options = {}) {
  const {
    bold = false,
    align = 'l',
    firstLineIndent = false,
    size = RTF_BODY_FONT_SIZE,
    spacingBefore = 0,
    spacingAfter = 120,
  } = options
  const alignToken = align === 'c' ? '\\qc' : '\\ql'
  const boldToken = bold ? '\\b' : ''
  const boldReset = bold ? '\\b0' : ''
  const firstIndentToken = firstLineIndent ? '\\fi420' : '\\fi0'
  return `\\pard${alignToken}${firstIndentToken}\\sl360\\slmult1\\sb${spacingBefore}\\sa${spacingAfter}${RTF_FONT_SWITCH}\\cf1\\fs${size}${boldToken} ${escapeRtfText(text)}${boldReset}\\par`
}

function buildRtfCellBorder(position, width) {
  if (!width) return `\\clbrdr${position}\\brdrnone`
  return `\\clbrdr${position}\\brdrs\\brdrw${width}\\brdrcf1`
}

function buildRtfTable(section) {
  const headers = section.headers || []
  const rows = section.rows || []
  if (!headers.length) return ''
  const columnCount = headers.length
  const cellWidth = Math.max(900, Math.floor(RTF_TABLE_WIDTH / columnCount))
  let content = '\\pard\\sa40\\par'
  content += buildRtfTableRow(headers, {
    columnCount,
    cellWidth,
    topBorderWidth: RTF_LINE_TOP,
    bottomBorderWidth: rows.length ? RTF_LINE_MIDDLE : RTF_LINE_BOTTOM,
    bold: true,
  })
  rows.forEach((row, index) => {
    content += buildRtfTableRow(row, {
      columnCount,
      cellWidth,
      topBorderWidth: 0,
      bottomBorderWidth: index === rows.length - 1 ? RTF_LINE_BOTTOM : 0,
      bold: false,
    })
  })
  content += '\\pard\\sa120\\par'
  return content
}

function buildRtfTableRow(cells, options) {
  const {
    columnCount,
    cellWidth,
    topBorderWidth,
    bottomBorderWidth,
    bold,
  } = options
  let row = '\\trowd\\trgaph0\\trleft0\\trautofit1'
  for (let index = 0; index < columnCount; index += 1) {
    row += '\\clvertalc'
    row += buildRtfCellBorder('t', topBorderWidth)
    row += buildRtfCellBorder('b', bottomBorderWidth)
    row += buildRtfCellBorder('l', 0)
    row += buildRtfCellBorder('r', 0)
    row += `\\cellx${(index + 1) * cellWidth}`
  }
  const normalizedCells = Array.from({ length: columnCount }, (_, index) => String(cells[index] ?? ''))
  normalizedCells.forEach(cell => {
    const boldToken = bold ? '\\b' : ''
    const boldReset = bold ? '\\b0' : ''
    row += `\\pard\\intbl\\qc\\sl300\\slmult1\\sa0\\sb0${RTF_FONT_SWITCH}\\cf1\\fs${RTF_TABLE_FONT_SIZE}${boldToken} ${escapeRtfText(cell)}${boldReset}\\cell`
  })
  row += '\\row'
  return row
}

function buildOfficeCellStyle(options = {}) {
  const {
    bold = false,
    topBorder = 'none',
    bottomBorder = 'none',
  } = options
  let style = `${TABLE_COPY_STYLE};border-left:none;border-right:none;border-top:${topBorder};border-bottom:${bottomBorder};mso-border-left-alt:none;mso-border-right-alt:none;mso-border-top-alt:${topBorder};mso-border-bottom-alt:${bottomBorder}`
  if (bold) style += ';font-weight:700'
  return style
}

function headerCellText(cell) {
  return cell && typeof cell === 'object' ? cell.text : cell
}

function headerCellSpan(cell, key) {
  const value = cell && typeof cell === 'object' ? Number(cell[key]) : 1
  return Number.isFinite(value) && value > 1 ? value : 1
}

function buildOfficeTableHtml(section) {
  const headers = section.headers || []
  const rows = section.rows || []
  if (!headers.length) return ''
  const headerRows = section.headerRows?.length ? section.headerRows : [headers]
  // Word/WPS 对 table 级边框不稳定，线要压到单元格上才不容易丢。
  let html = `<table border="0" cellspacing="0" cellpadding="0" style="border-collapse:collapse;table-layout:fixed;width:100%;margin:8px 0;border:none;mso-table-lspace:0pt;mso-table-rspace:0pt;mso-border-alt:none;mso-border-insideh:none;mso-border-insidev:none;${HTML_TABLE_FONT}">`
  html += '<thead>'
  headerRows.forEach((headerRow, rowIndex) => {
    html += '<tr>'
    headerRow.forEach(cell => {
      const topBorder = rowIndex === 0 ? '2px solid #000' : 'none'
      const isGroupedHeader = headerCellSpan(cell, 'colspan') > 1
      const bottomBorder = (isGroupedHeader || rowIndex === headerRows.length - 1) && rows.length ? '1px solid #000' : 'none'
      html += `<th align="center" valign="middle" colspan="${headerCellSpan(cell, 'colspan')}" rowspan="${headerCellSpan(cell, 'rowspan')}" style="${buildOfficeCellStyle({ bold: true, topBorder, bottomBorder })}">${escapeHtml(headerCellText(cell))}</th>`
    })
    html += '</tr>'
  })
  html += '</thead><tbody>'
  rows.forEach((row, rowIndex) => {
    const bottomBorder = rowIndex === rows.length - 1 ? '2px solid #000' : 'none'
    html += '<tr>'
    const cells = section.bodyRowspanColumns ? (row || []) : headers.map((_, index) => row?.[index] ?? '')
    cells.forEach(cell => {
      html += `<td align="center" valign="middle" colspan="${headerCellSpan(cell, 'colspan')}" rowspan="${headerCellSpan(cell, 'rowspan')}" style="${buildOfficeCellStyle({ bottomBorder })}">${escapeHtml(headerCellText(cell))}</td>`
    })
    html += '</tr>'
  })
  html += '</tbody></table>'
  return html
}

function appendTableSection(builder, section) {
  builder.html += buildOfficeTableHtml(section)
  const exportRows = section.exportRows || section.rows || []
  builder.rtf += buildRtfTable({ ...section, rows: exportRows })
  if (section.headers?.length) {
    builder.plain += section.headers.join('\t') + '\n'
    exportRows.forEach(row => {
      const normalizedRow = section.headers.map((_, index) => String(row?.[index] ?? ''))
      builder.plain += normalizedRow.join('\t') + '\n'
    })
  }
}

export function buildTableSectionCopyPayload(section) {
  const builder = createRichPayloadBuilder()
  appendTableSection(builder, section || {})
  if (section?.note) {
    appendHtmlParagraph(builder, section.note, 'font-size:10pt;color:#666;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;margin:6px 0 0')
    appendPlainParagraph(builder, section.note, '\n')
    appendRtfParagraph(builder, section.note, { size: RTF_NOTE_FONT_SIZE, spacingBefore: 60, spacingAfter: 60 })
  }
  return finalizeRichPayload(builder)
}

export function buildAllResultsCopyPayload(results) {
  const builder = createRichPayloadBuilder()

  for (const result of results || []) {
    if (result.name) {
      appendPlainParagraph(builder, `【${result.name}】`)
      appendHtmlParagraph(builder, result.name, 'margin:16px 0 8px;font-size:14pt;font-weight:700;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
      appendRtfParagraph(builder, result.name, { bold: true, size: RTF_TITLE_FONT_SIZE, spacingBefore: 120, spacingAfter: 100 })
    }
    if (result.sections?.length) {
      for (const section of result.sections) {
        appendSection(builder, section)
      }
    } else {
      appendSimpleResult(builder, result)
    }
  }

  return finalizeRichPayload(builder)
}

function appendSection(builder, section) {
  if (section.type === 'table' && section.headers?.length) {
    if (section.title) {
      appendPlainParagraph(builder, section.title, '\n')
      appendHtmlParagraph(builder, section.title, 'margin:10px 0 6px;font-size:12pt;font-weight:700;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
      appendRtfParagraph(builder, section.title, { bold: true, size: RTF_SECTION_TITLE_SIZE, spacingBefore: 80, spacingAfter: 60 })
    }
    appendTableSection(builder, section)
    if (section.description) {
      appendHtmlParagraph(builder, section.description, 'text-indent:2em;line-height:1.8;font-size:12pt;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;margin:8px 0')
      appendPlainParagraph(builder, section.description, '\n')
      appendRtfParagraph(builder, section.description, { firstLineIndent: true, size: RTF_BODY_FONT_SIZE })
    }
    if (section.note) {
      appendHtmlParagraph(builder, section.note, 'font-size:10pt;color:#666;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;margin:6px 0 0')
      appendPlainParagraph(builder, section.note, '\n')
      appendRtfParagraph(builder, section.note, { size: RTF_NOTE_FONT_SIZE, spacingBefore: 60, spacingAfter: 60 })
    }
    builder.plain += '\n'
    return
  }

  if (section.type === 'advice' || section.type === 'smart_analysis') {
    appendHtmlParagraph(builder, section.title, 'margin:10px 0 6px;font-size:12pt;font-weight:700;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
    appendHtmlParagraph(builder, section.content, 'text-indent:2em;line-height:1.8;font-size:12pt;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
    appendPlainParagraph(builder, `${section.title}\n${section.content}`)
    appendRtfParagraph(builder, section.title, { bold: true, size: RTF_SECTION_TITLE_SIZE, spacingBefore: 80, spacingAfter: 60 })
    appendRtfParagraph(builder, section.content, { firstLineIndent: true, size: RTF_BODY_FONT_SIZE })
    return
  }

  if (section.type === 'references' && section.items?.length) {
    appendHtmlParagraph(builder, section.title, 'margin:10px 0 6px;font-size:12pt;font-weight:700;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
    builder.html += '<ul style="margin:6px 0 12px 22px;padding:0;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif">'
    for (const item of section.items) {
      builder.html += `<li style="margin:4px 0">${escapeHtml(item)}</li>`
      builder.rtf += buildRtfParagraph(`• ${item}`, { size: RTF_NOTE_FONT_SIZE, spacingBefore: 0, spacingAfter: 40 })
    }
    builder.html += '</ul>'
    appendPlainParagraph(builder, `${section.title}\n${section.items.join('\n')}`)
    return
  }

  if (section.type === 'charts' && section.charts?.length) {
    appendHtmlParagraph(builder, section.title, 'margin:10px 0 6px;font-size:12pt;font-weight:700;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
    appendPlainParagraph(builder, section.title, '\n')
    appendRtfParagraph(builder, section.title, { bold: true, size: RTF_SECTION_TITLE_SIZE, spacingBefore: 80, spacingAfter: 60 })
    for (const chart of section.charts) {
      const chartTitle = chart.title || chart.data?.displayTitle || '图表'
      appendHtmlParagraph(builder, chartTitle, 'margin:6px 0 4px;font-size:11pt;font-weight:600;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
      appendPlainParagraph(builder, chartTitle, '\n')
      appendRtfParagraph(builder, chartTitle, { bold: true, size: RTF_BODY_FONT_SIZE, spacingBefore: 40, spacingAfter: 40 })
      const dataTable = buildChartDataTable(chart)
      if (dataTable) {
        builder.html += dataTable.html
        builder.plain += dataTable.plain
        builder.rtf += dataTable.rtf
      }
    }
    if (section.description) {
      appendHtmlParagraph(builder, section.description, 'text-indent:2em;line-height:1.8;font-size:12pt;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif;margin:8px 0')
      appendPlainParagraph(builder, section.description, '\n')
      appendRtfParagraph(builder, section.description, { firstLineIndent: true, size: RTF_BODY_FONT_SIZE })
    }
    builder.plain += '\n'
  }
}

function appendSimpleResult(builder, result) {
  if (result.headers?.length) {
    appendTableSection(builder, result)
    builder.plain += '\n'
  }
  if (result.description) {
    appendHtmlParagraph(builder, result.description, 'text-indent:2em;line-height:1.8;font-size:12pt;color:#000;font-family:&quot;Times New Roman&quot;,&quot;宋体&quot;,serif')
    appendPlainParagraph(builder, result.description)
    appendRtfParagraph(builder, result.description, { firstLineIndent: true, size: RTF_BODY_FONT_SIZE })
  }
}

export function buildSimpleResultCopyPayload(result) {
  const builder = createRichPayloadBuilder()
  appendSimpleResult(builder, result || {})
  return finalizeRichPayload(builder)
}

export function buildReportExportHtml(title, results) {
  let html = `<html><head><meta charset="utf-8"><style>body{font-family:"宋体","Times New Roman",serif;padding:20px}table{border-collapse:collapse;width:100%;margin:10px 0}th,td{${EXPORT_CELL_STYLE}}th{font-weight:bold;background:#f5f5f5}</style></head><body>`
  html += `<h2>${title}</h2>`
  for (const result of results || []) {
    if (result.sections?.length) {
      for (const section of result.sections) {
        html += buildExportSectionHtml(section)
      }
    } else {
      if (result.name) html += `<h3>${result.name}</h3>`
      html += buildExportTableHtml(result.headers, result.rows)
      if (result.description) html += `<p>${result.description}</p>`
    }
  }
  html += '</body></html>'
  return html
}

function buildExportSectionHtml(section) {
  if (section.type === 'table') {
    let html = `<h3>${section.title}</h3>`
    html += buildExportTableHtml(section.headers, section.rows, section.headerRows, section.bodyRowspanColumns)
    if (section.description) html += `<p>${section.description}</p>`
    if (section.note) html += `<p style="color:#666;font-size:9pt">${section.note}</p>`
    return html
  }
  if (section.type === 'advice' || section.type === 'smart_analysis') {
    return `<h3>${section.title}</h3><p>${section.content}</p>`
  }
  if (section.type === 'references') {
    let html = `<h4>${section.title}</h4><ul>`
    for (const item of (section.items || [])) html += `<li style="font-size:9pt;color:#666">${item}</li>`
    html += '</ul>'
    return html
  }
  if (section.type === 'charts' && section.charts?.length) {
    let html = `<h3>${section.title}</h3>`
    for (const chart of section.charts) {
      const chartTitle = chart.title || chart.data?.displayTitle || '图表'
      html += `<h4>${chartTitle}</h4>`
      const dataTable = buildChartDataTable(chart)
      if (dataTable) html += dataTable.html
    }
    if (section.description) html += `<p>${section.description}</p>`
    return html
  }
  return ''
}

function buildExportTableHtml(headers, rows, headerRows = null, bodyRowspanColumns = 0) {
  if (!headers?.length) return ''
  const normalizedHeaderRows = headerRows?.length ? headerRows : [headers]
  let html = '<table><thead>'
  for (const headerRow of normalizedHeaderRows) {
    html += '<tr>'
    for (const header of headerRow) {
      html += `<th colspan="${headerCellSpan(header, 'colspan')}" rowspan="${headerCellSpan(header, 'rowspan')}">${escapeHtml(headerCellText(header))}</th>`
    }
    html += '</tr>'
  }
  html += '</thead><tbody>'
  for (const row of (rows || [])) {
    html += '<tr>'
    const cells = bodyRowspanColumns ? (row || []) : row
    for (const cell of cells) {
      html += `<td colspan="${headerCellSpan(cell, 'colspan')}" rowspan="${headerCellSpan(cell, 'rowspan')}">${escapeHtml(headerCellText(cell))}</td>`
    }
    html += '</tr>'
  }
  html += '</tbody></table>'
  return html
}

export function downloadWordHtml(title, html) {
  const blob = new Blob(['\ufeff' + html], { type: 'application/msword' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${title || '分析报告'}.doc`
  link.click()
  URL.revokeObjectURL(link.href)
}

function buildChartDataTable(chart) {
  const data = chart.data
  if (!data) return null
  const labels = data.labels || []
  const values = data.values || []
  const metric = data.metric || '值'
  if (!labels.length || !values.length) return null

  // HTML table
  let html = `<table border="0" cellspacing="0" cellpadding="0" style="border-collapse:collapse;table-layout:fixed;width:100%;margin:6px 0;border:none;mso-table-lspace:0pt;mso-table-rspace:0pt;${HTML_TABLE_FONT}">`
  html += `<thead><tr><th style="${buildOfficeCellStyle({ bold: true, topBorder: '2px solid #000', bottomBorder: '1px solid #000' })}">类别</th><th style="${buildOfficeCellStyle({ bold: true, topBorder: '2px solid #000', bottomBorder: '1px solid #000' })}">${escapeHtml(metric)}</th></tr></thead><tbody>`
  for (let i = 0; i < labels.length; i++) {
    const bottomBorder = i === labels.length - 1 ? '2px solid #000' : 'none'
    html += `<tr><td style="${buildOfficeCellStyle({ bottomBorder })}">${escapeHtml(String(labels[i]))}</td><td style="${buildOfficeCellStyle({ bottomBorder })}">${escapeHtml(String(values[i] ?? ''))}</td></tr>`
  }
  html += '</tbody></table>'

  // Plain text
  let plain = `类别\t${metric}\n`
  for (let i = 0; i < labels.length; i++) {
    plain += `${labels[i]}\t${values[i] ?? ''}\n`
  }

  // RTF table
  const cellWidth = Math.floor(RTF_TABLE_WIDTH / 2)
  let rtf = '\\trowd\\trgaph0\\trleft0\\trautofit1'
  for (let i = 0; i < 2; i++) {
    rtf += `\\clvertalc${buildRtfCellBorder('t', RTF_LINE_TOP)}${buildRtfCellBorder('b', RTF_LINE_MIDDLE)}${buildRtfCellBorder('l', 0)}${buildRtfCellBorder('r', 0)}\\cellx${(i + 1) * cellWidth}`
  }
  rtf += `\\pard\\intbl\\qc\\sl300\\slmult1\\sa0\\sb0${RTF_FONT_SWITCH}\\cf1\\fs${RTF_TABLE_FONT_SIZE}\\b 类别\\b0\\cell\\pard\\intbl\\qc\\sl300\\slmult1\\sa0\\sb0${RTF_FONT_SWITCH}\\cf1\\fs${RTF_TABLE_FONT_SIZE}\\b ${escapeRtfText(metric)}\\b0\\cell\\row`
  for (let i = 0; i < labels.length; i++) {
    const bottomBorder = i === labels.length - 1 ? RTF_LINE_BOTTOM : 0
    rtf += '\\trowd\\trgaph0\\trleft0\\trautofit1'
    for (let j = 0; j < 2; j++) {
      rtf += `\\clvertalc${buildRtfCellBorder('t', 0)}${buildRtfCellBorder('b', bottomBorder)}${buildRtfCellBorder('l', 0)}${buildRtfCellBorder('r', 0)}\\cellx${(j + 1) * cellWidth}`
    }
    rtf += `\\pard\\intbl\\qc\\sl300\\slmult1\\sa0\\sb0${RTF_FONT_SWITCH}\\cf1\\fs${RTF_TABLE_FONT_SIZE} ${escapeRtfText(String(labels[i]))}\\cell\\pard\\intbl\\qc\\sl300\\slmult1\\sa0\\sb0${RTF_FONT_SWITCH}\\cf1\\fs${RTF_TABLE_FONT_SIZE} ${escapeRtfText(String(values[i] ?? ''))}\\cell\\row`
  }
  rtf += '\\pard\\sa40\\par'

  return { html, plain, rtf }
}

export function printHtml(html) {
  const printWindow = window.open('', '_blank')
  if (!printWindow) return
  printWindow.document.write(html)
  printWindow.document.close()
  setTimeout(() => { printWindow.print() }, 400)
}

function fallbackCopyText(text) {
  try {
    const textarea = document.createElement('textarea')
    textarea.value = String(text || '')
    textarea.setAttribute('readonly', 'readonly')
    textarea.style.position = 'fixed'
    textarea.style.top = '-9999px'
    textarea.style.left = '-9999px'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    textarea.setSelectionRange(0, textarea.value.length)
    const copied = document.execCommand('copy')
    document.body.removeChild(textarea)
    return copied
  } catch {
    return false
  }
}
