import { ref } from 'vue'
import * as api from '../../api.js'

export function useDatasetExport(props) {
  const exportDialogVisible = ref(false)
  const exportFormats = [
    { key: 'xlsx', label: 'Excel', ext: '.xlsx' },
    { key: 'csv', label: 'CSV', ext: '.csv' },
    { key: 'sav', label: 'SPSS', ext: '.sav' },
    { key: 'dta', label: 'Stata', ext: '.dta' },
    { key: 'xpt', label: 'SAS', ext: '.xpt' },
    { key: 'tsv', label: 'TSV', ext: '.tsv' },
    { key: 'txt', label: 'TXT', ext: '.txt' },
    { key: 'json', label: 'JSON', ext: '.json' },
    { key: 'parquet', label: 'Parquet', ext: '.parquet' },
  ]

  function exportCurrent() {
    exportDialogVisible.value = true
  }

  async function handleExportFormat(format) {
    if (!props.sessionId) return
    try {
      const buf = await api.exportDataFileBuffer(props.sessionId, format)
      const blob = new Blob([buf])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const baseName = (props.dataFileName || 'data').replace(/\.[^.]+$/, '')
      a.download = `${baseName}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      exportDialogVisible.value = false
    } catch (e) {
      alert('导出失败: ' + e.message)
    }
  }

  return {
    exportCurrent,
    exportDialogVisible,
    exportFormats,
    handleExportFormat,
  }
}
