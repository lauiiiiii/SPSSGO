import { computed, onMounted, ref, watch } from 'vue'
import * as api from '../../api.js'

export function useDatasetVersions(props, { emit, loadPreview, notifySuccess }) {
  const versionDialogVisible = ref(false)
  const versionLoading = ref(false)
  const datasetVersions = ref([])
  const currentVersionId = ref(null)
  const versionSwitchingId = ref(null)

  const currentVersionNo = computed(() => {
    const current = datasetVersions.value.find(item => item.id === currentVersionId.value)
    return current?.version_no || ''
  })

  async function loadVersions() {
    if (!props.sessionId || !props.hasData) {
      datasetVersions.value = []
      currentVersionId.value = null
      return
    }
    versionLoading.value = true
    try {
      const data = await api.getDatasetVersions(props.sessionId)
      datasetVersions.value = data.versions || []
      currentVersionId.value = data.current_dataset_version_id || null
    } catch (_) {
      datasetVersions.value = []
      currentVersionId.value = null
    }
    versionLoading.value = false
  }

  async function openVersionDialog() {
    versionDialogVisible.value = true
    await loadVersions()
  }

  async function switchDatasetVersion(version) {
    if (!props.sessionId || !version || version.is_current) return
    versionSwitchingId.value = version.id
    try {
      const data = await api.activateDatasetVersion(props.sessionId, version.id)
      notifySuccess(data.message || '数据版本已切换')
      await loadVersions()
      emit('variables-updated')
      await loadPreview()
    } catch (e) {
      alert('切换版本失败: ' + e.message)
    }
    versionSwitchingId.value = null
  }

  onMounted(loadVersions)
  watch(() => props.sessionId, loadVersions)
  watch(() => props.hasData, (hasData) => {
    if (hasData) {
      loadVersions()
    } else {
      datasetVersions.value = []
      currentVersionId.value = null
    }
  })

  return {
    currentVersionNo,
    datasetVersions,
    formatVersionTime,
    loadVersions,
    openVersionDialog,
    switchDatasetVersion,
    versionDialogVisible,
    versionLoading,
    versionSwitchingId,
  }
}

function formatVersionTime(value) {
  if (!value) return '刚刚'
  try {
    return new Date(Number(value) * 1000).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (_) {
    return '刚刚'
  }
}
