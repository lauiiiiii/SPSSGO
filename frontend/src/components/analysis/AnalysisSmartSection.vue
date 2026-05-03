<template>
  <div class="ap-sec ap-sec--smart">
    <div class="ap-sec-label">
      <span class="ap-sec-label-dot ap-dot--green"></span>
      {{ section.title }}
      <button v-if="allowAiRequest" class="ap-sec-ai-btn" @click="$emit('request-ai')" :disabled="aiLoading">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3l2 1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        {{ aiLoading ? '解读中...' : 'AI智能解读 >' }}
      </button>
    </div>
    <div class="ap-sec-body">{{ section.content }}</div>
    <div v-if="aiResult" class="ap-sec-ai-box">
      <div class="ap-sec-ai-head">AI 深度解读</div>
      <div class="ap-sec-ai-text">{{ aiResult }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  aiLoading: { type: Boolean, default: false },
  aiResult: { type: String, default: '' },
  allowAiRequest: { type: Boolean, default: true },
  section: { type: Object, required: true },
})

defineEmits(['request-ai'])
</script>
