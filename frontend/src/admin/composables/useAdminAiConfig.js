import { reactive, ref } from 'vue'
import { getAdminAiConfig, getAdminSystemInfo, saveAdminAiConfig } from '../api.js'

export function useAdminAiConfig() {
  const systemInfo = ref({})
  const systemLoading = ref(false)
  const systemError = ref('')

  const aiLoading = ref(false)
  const aiSaving = ref(false)
  const aiError = ref('')
  const aiSuccess = ref('')
  const aiConfig = reactive({
    provider: 'deepseek',
    base_url: '',
    model: '',
    api_key: '',
    has_api_key: false,
    api_key_masked: '',
    clear_api_key: false,
    provider_defaults: {},
  })

  async function loadSystemInfo() {
    systemLoading.value = true
    systemError.value = ''
    try {
      systemInfo.value = await getAdminSystemInfo()
    } catch (err) {
      systemError.value = err.message || '系统信息加载失败'
    } finally {
      systemLoading.value = false
    }
  }

  async function loadAiConfig() {
    aiLoading.value = true
    aiError.value = ''
    try {
      const data = await getAdminAiConfig()
      aiConfig.provider = data.provider || 'deepseek'
      aiConfig.base_url = data.base_url || ''
      aiConfig.model = data.model || ''
      aiConfig.api_key = ''
      aiConfig.has_api_key = !!data.has_api_key
      aiConfig.api_key_masked = data.api_key_masked || ''
      aiConfig.clear_api_key = false
      aiConfig.provider_defaults = data.provider_defaults || {}
    } catch (err) {
      aiError.value = err.message || 'AI 配置加载失败'
    } finally {
      aiLoading.value = false
    }
  }

  function applyProviderPreset() {
    const defaults = aiConfig.provider_defaults?.[aiConfig.provider]
    if (!defaults) return
    aiConfig.base_url = defaults.base_url || aiConfig.base_url
    aiConfig.model = defaults.model || aiConfig.model
  }

  async function saveAiConfig() {
    if (!aiConfig.base_url || !aiConfig.model) {
      throw new Error('请填写 Base URL 和模型名称')
    }
    aiSaving.value = true
    aiError.value = ''
    aiSuccess.value = ''
    try {
      const data = await saveAdminAiConfig({
        provider: aiConfig.provider,
        base_url: aiConfig.base_url,
        model: aiConfig.model,
        api_key: aiConfig.api_key,
        clear_api_key: aiConfig.clear_api_key,
      })
      aiConfig.api_key = ''
      aiConfig.has_api_key = !!data.has_api_key
      aiConfig.api_key_masked = data.api_key_masked || ''
      aiConfig.clear_api_key = false
      aiSuccess.value = 'AI 配置已保存'
      await loadSystemInfo()
    } catch (err) {
      aiError.value = err.message || 'AI 配置保存失败'
      throw err
    } finally {
      aiSaving.value = false
    }
  }

  return {
    systemInfo,
    systemLoading,
    systemError,
    aiConfig,
    aiLoading,
    aiSaving,
    aiError,
    aiSuccess,
    loadSystemInfo,
    loadAiConfig,
    applyProviderPreset,
    saveAiConfig,
  }
}
