import { computed } from 'vue'
import { downloadWordBuffer } from '../../api.js'
import {
  buildAllResultsCopyPayload,
  buildReportExportHtml,
  buildTableSectionCopyPayload,
  downloadWordHtml,
  printHtml,
  writeRichClipboard,
} from '../../utils/reportExport.js'
import { buildReportMetaTags } from '../../utils/reportMeta.js'
import { buildVariableMetaMap, createResultDisplayFormatter } from '../../utils/resultDisplay.js'

export function useAnalysisReport(props) {
  const variableMetaMap = computed(() => buildVariableMetaMap(props.variables))
  const resultDisplayFormatter = computed(() => createResultDisplayFormatter(variableMetaMap.value))
  const displayResults = computed(() => (props.results || []).map(resultDisplayFormatter.value.normalizeResult))
  const reportTitle = computed(() => displayResults.value?.[0]?.name || props.method?.label || '分析报告')
  const reportMetaTags = computed(() => {
    return buildReportMetaTags({
      currentDatasetVersionId: props.currentDatasetVersionId,
      currentDatasetVersionNo: props.currentDatasetVersionNo,
      result: props.results?.[0],
    })
  })

  function getVarType(name) {
    const variable = variableMetaMap.value[name]
    if (!variable) return ''
    return variable.type === 'numeric' ? '定量' : variable.type === 'categorical' ? '定类' : '字符'
  }

  function getVarTypeClass(name) {
    const variable = variableMetaMap.value[name]
    if (!variable) return ''
    return 't-' + variable.type
  }

  const cellClass = cell => ({
    'tlt-cell--danger': cell === '需要检查',
    'tlt-cell--success': cell === '较好',
  })

  async function copyTable(sec, evt) {
    const payload = buildTableSectionCopyPayload(sec)
    await writeRichClipboard(payload)
    const button = evt?.target?.closest?.('.ap-sec-copy')
    if (!button) return
    const textEl = button.querySelector('.ap-sec-copy-txt')
    if (!textEl) return
    textEl.textContent = '已复制'
    setTimeout(() => { textEl.textContent = '复制' }, 1500)
  }

  async function copyAllResults() {
    const payload = buildAllResultsCopyPayload(displayResults.value)
    await writeRichClipboard(payload)
  }

  function buildExportHTML() {
    return buildReportExportHtml(reportTitle.value, displayResults.value)
  }

  function isDocxBuffer(buffer) {
    const bytes = new Uint8Array(buffer || new ArrayBuffer(0))
    if (bytes.length < 4) return false
    // docx 本质上是 zip 包，头一般是 PK\x03\x04。
    return bytes[0] === 0x50 && bytes[1] === 0x4b && (bytes[2] === 0x03 || bytes[2] === 0x05 || bytes[2] === 0x07) && (bytes[3] === 0x04 || bytes[3] === 0x06 || bytes[3] === 0x08)
  }

  async function exportWord() {
    try {
      if (props.sessionId) {
        const buffer = await downloadWordBuffer(props.sessionId)
        if (!isDocxBuffer(buffer)) {
          throw new Error('后端返回的不是标准 Word 文档')
        }
        const blob = new Blob([buffer], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${reportTitle.value || '分析报告'}.docx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        return
      }
      downloadWordHtml(reportTitle.value, buildExportHTML())
    } catch (error) {
      alert(`导出 Word 失败：${error?.message || '请稍后重试'}`)
    }
  }

  function exportPDF() {
    printHtml(buildExportHTML())
  }

  return {
    cellClass,
    copyAllResults,
    copyTable,
    displayResults,
    exportPDF,
    exportWord,
    getVarType,
    getVarTypeClass,
    reportMetaTags,
    reportTitle,
  }
}
