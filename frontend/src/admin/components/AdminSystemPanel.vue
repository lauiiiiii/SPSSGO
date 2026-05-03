<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Runtime</div>
        <h2>系统信息</h2>
      </div>
      <button class="admin-ghost-btn" type="button" @click="$emit('refresh')">刷新</button>
    </div>

    <div v-if="loading" class="admin-state">系统信息加载中...</div>
    <div v-else-if="error" class="admin-state is-error">{{ error }}</div>
    <div v-else class="admin-block">
      <div class="admin-kv-list admin-kv-list--dense">
        <div class="admin-kv-row"><span>Python 版本</span><strong>{{ systemInfo.python_version || '—' }}</strong></div>
        <div class="admin-kv-row"><span>操作系统</span><strong>{{ systemInfo.system || '—' }}</strong></div>
        <div class="admin-kv-row"><span>AI 供应商</span><strong>{{ providerLabel(systemInfo.ai_provider) }}</strong></div>
        <div class="admin-kv-row"><span>AI 模型</span><strong>{{ systemInfo.ai_model || '—' }}</strong></div>
        <div class="admin-kv-row"><span>AI 接口</span><strong class="admin-text-ellipsis">{{ systemInfo.ai_base_url || '—' }}</strong></div>
        <div class="admin-kv-row"><span>AI Key</span><strong>{{ systemInfo.ai_has_api_key ? '已配置' : '未配置' }}</strong></div>
        <div class="admin-kv-row"><span>任务后端</span><strong>{{ systemInfo.job_backend || '—' }}</strong></div>
        <div class="admin-kv-row"><span>最大上传</span><strong>{{ systemInfo.max_upload_mb || 0 }} MB</strong></div>
        <div class="admin-kv-row"><span>最大执行时间</span><strong>{{ systemInfo.max_exec_seconds || 0 }} 秒</strong></div>
        <div class="admin-kv-row"><span>会话过期</span><strong>{{ systemInfo.session_expire_hours || 0 }} 小时</strong></div>
        <div class="admin-kv-row"><span>最大并发任务</span><strong>{{ systemInfo.max_concurrent_tasks || 0 }}</strong></div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  systemInfo: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['refresh'])

function providerLabel(provider) {
  if (provider === 'deepseek') return 'DeepSeek'
  if (provider === 'doubao') return '豆包 / 火山方舟'
  if (provider === 'qwen') return '通义千问'
  if (provider === 'kimi') return 'Kimi / Moonshot'
  if (provider === 'openai') return 'OpenAI'
  if (provider === 'gemini') return 'Google Gemini'
  if (provider === 'claude') return 'Anthropic Claude'
  if (provider === 'grok') return 'xAI Grok'
  if (provider === 'mistral') return 'Mistral'
  if (provider === 'cohere') return 'Cohere'
  if (provider === 'custom') return '自定义'
  return provider || '—'
}
</script>
