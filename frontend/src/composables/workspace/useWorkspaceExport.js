import * as api from '../../api.js'

export function useWorkspaceExport({
  handleTrackedJobProgress,
  sessionId,
}) {
  async function downloadWord() {
    if (!sessionId.value) return

    try {
      const buffer = await api.downloadWordBuffer(sessionId.value, {
        onProgress: handleTrackedJobProgress,
      })
      const blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = '分析结果.docx'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('导出失败: ' + e.message)
    }
  }

  return {
    downloadWord,
  }
}
