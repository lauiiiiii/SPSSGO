import * as api from '../../api.js'

const SESSION_KEY = 'spssgo_session_id'

export function useDataUpload({
  dataFileName,
  dragHover,
  handleTrackedJobProgress,
  hasData,
  loadAllDataSets,
  loadVariables,
  sessionId,
  showUploadModal,
}) {
  async function ensureSession() {
    if (!sessionId.value) {
      const saved = localStorage.getItem(SESSION_KEY)
      if (saved) {
        sessionId.value = saved
        return
      }
      const data = await api.createSession()
      sessionId.value = data.session_id
      localStorage.setItem(SESSION_KEY, data.session_id)
    }
  }

  function onDataFile(event) {
    const file = event.target.files[0]
    if (file) {
      showUploadModal.value = false
      uploadData(file)
    }
    event.target.value = ''
  }

  function onDropFile(event) {
    dragHover.value = false
    const file = event.dataTransfer?.files?.[0]
    if (file) {
      showUploadModal.value = false
      uploadData(file)
    }
  }

  async function uploadData(file) {
    if (!sessionId.value) {
      await ensureSession()
    } else if (hasData.value) {
      const newSession = await api.createSession()
      sessionId.value = newSession.session_id
    }
    localStorage.setItem(SESSION_KEY, sessionId.value)
    try {
      const data = await api.uploadFile(sessionId.value, file, { onProgress: handleTrackedJobProgress })
      if (data.job) handleTrackedJobProgress(data.job)
      hasData.value = true
      dataFileName.value = file.name
      await loadVariables()
      await loadAllDataSets()
    } catch (e) {
      alert('上传失败: ' + e.message)
    }
  }

  return {
    onDataFile,
    onDropFile,
  }
}
