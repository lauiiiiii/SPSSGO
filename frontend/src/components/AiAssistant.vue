<template>
  <!-- Chat panel -->
  <div v-if="open" class="ai-panel">
    <div class="ai-panel-header">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="color:#2563eb">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="ai-panel-title">AI 数据分析助手</span>
      <button class="ai-panel-close" @click="open = false">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </button>
    </div>

    <div class="ai-messages" ref="msgListRef">
      <div class="ai-msg ai">
        你好！我是 AI 分析助手，可以帮你：
        <br/>• 推荐适合的分析方法
        <br/>• 建议应该选哪些变量
        <br/>• 解读分析结果的含义
        <br/>• 回答统计方法相关问题
      </div>
      <div v-for="(m, i) in messages" :key="i" class="ai-msg" :class="m.role">
        {{ m.content }}
      </div>
      <div v-if="thinking" class="ai-msg ai" style="opacity:.6">
        <span class="spinner-sm" style="display:inline-block;vertical-align:middle;margin-right:6px"></span>
        思考中...
      </div>
    </div>

    <div class="ai-input-bar">
      <input
        class="ai-input"
        v-model="input"
        placeholder="问我任何数据分析问题..."
        @keydown.enter.prevent="send"
      />
      <button class="ai-send" :disabled="!input.trim() || thinking" @click="send">
        <svg width="14" height="14" viewBox="0 0 18 18" fill="none"><path d="M9 14V4M4 8l5-5 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { aiAssist } from '../api.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  context: { type: String, default: '' },
})

const open = ref(false)
const input = ref('')
const messages = ref([])
const thinking = ref(false)
const msgListRef = ref(null)

watch(() => props.visible, (v) => { open.value = v })

function scrollToBottom() {
  nextTick(() => {
    if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  })
}

async function send() {
  const text = input.value.trim()
  if (!text || thinking.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  thinking.value = true
  scrollToBottom()

  try {
    const contextPrompt = props.context
      ? `[当前数据分析上下文]\n${props.context}\n\n[用户问题]\n${text}`
      : text

    const data = await aiAssist(contextPrompt)
    messages.value.push({ role: 'ai', content: data.reply || '抱歉，我暂时无法回答。' })
  } catch {
    messages.value.push({ role: 'ai', content: '网络连接失败，请检查后端服务是否运行。' })
  }

  thinking.value = false
  scrollToBottom()
}

defineExpose({ open })
</script>
