import { ref } from 'vue'
import * as api from '../../api.js'

export function useAiInterpretation(sessionId) {
  const aiLoading = ref(false)
  const aiResult = ref('')

  function resetAiInterpretation() {
    aiLoading.value = false
    aiResult.value = ''
  }

  async function requestAiInterpret(result) {
    if (aiLoading.value) return
    aiLoading.value = true
    aiResult.value = ''
    try {
      const data = await api.aiInterpret(result.name || '', result.sections || [], {
        sessionId: sessionId.value,
        datasetVersionId: result.dataset_version_id || null,
      })
      aiResult.value = data.interpretation || '未获取到解读内容'
    } catch (error) {
      aiResult.value = `解读失败：${error.message}`
    }
    aiLoading.value = false
  }

  return {
    aiLoading,
    aiResult,
    requestAiInterpret,
    resetAiInterpretation,
  }
}
