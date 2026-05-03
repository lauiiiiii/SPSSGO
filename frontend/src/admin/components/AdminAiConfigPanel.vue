<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Model Access</div>
        <h2>AI 配置</h2>
      </div>
      <button class="admin-primary-btn" type="button" :disabled="saving" @click="$emit('save')">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
    </div>

    <div v-if="error" class="admin-state is-error">{{ error }}</div>
    <div v-else-if="loading" class="admin-state">AI 配置加载中...</div>
    <div v-else class="admin-split-grid">
      <section class="admin-block">
        <div class="admin-block__title">全局模型配置</div>
        <div class="admin-form-grid">
          <label class="admin-field">
            <span>供应商</span>
            <select :value="config.provider" @change="updateField('provider', $event.target.value); $emit('apply-provider-preset')">
              <option value="deepseek">DeepSeek</option>
              <option value="doubao">豆包 / 火山方舟</option>
              <option value="qwen">通义千问</option>
              <option value="kimi">Kimi / Moonshot</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Google Gemini</option>
              <option value="claude">Anthropic Claude</option>
              <option value="grok">xAI Grok</option>
              <option value="mistral">Mistral</option>
              <option value="cohere">Cohere</option>
              <option value="custom">自定义 OpenAI 兼容接口</option>
            </select>
          </label>
          <label class="admin-field">
            <span>模型名</span>
            <input :value="config.model" type="text" placeholder="例如 deepseek-chat" @input="updateField('model', $event.target.value)" />
          </label>
          <label class="admin-field admin-field--wide">
            <span>Base URL</span>
            <input :value="config.base_url" type="text" placeholder="https://api.example.com/v1" @input="updateField('base_url', $event.target.value)" />
          </label>
          <label class="admin-field admin-field--wide">
            <span>API Key</span>
            <input :value="config.api_key" type="password" :placeholder="config.has_api_key ? `已保存：${config.api_key_masked}，留空不改` : '请输入 API Key'" @input="updateField('api_key', $event.target.value)" />
          </label>
          <label class="admin-check admin-field--wide">
            <input :checked="config.clear_api_key" type="checkbox" @change="updateField('clear_api_key', $event.target.checked)" />
            <span>清空已保存的 API Key</span>
          </label>
        </div>
      </section>

      <section class="admin-block">
        <div class="admin-block__title">当前运行态</div>
        <div class="admin-kv-list">
          <div class="admin-kv-row"><span>当前供应商</span><strong>{{ providerLabel(config.provider) }}</strong></div>
          <div class="admin-kv-row"><span>当前模型</span><strong>{{ config.model || '—' }}</strong></div>
          <div class="admin-kv-row"><span>Base URL</span><strong class="admin-text-ellipsis">{{ config.base_url || '—' }}</strong></div>
          <div class="admin-kv-row"><span>Key 状态</span><strong>{{ config.has_api_key ? config.api_key_masked : '未配置' }}</strong></div>
        </div>
        <p class="admin-hint">这套配置是全局生效的，所有用户共用。这里先写死成单配置，别往多 Key 池上拐。</p>
      </section>
    </div>

    <div v-if="success" class="admin-state is-success">{{ success }}</div>
  </section>
</template>

<script setup>
const props = defineProps({
  config: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
  success: { type: String, default: '' },
})

const emit = defineEmits(['save', 'update:config', 'apply-provider-preset'])

function updateField(key, value) {
  emit('update:config', { ...props.config, [key]: value })
}

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
