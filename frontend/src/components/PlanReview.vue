<template>
  <div>
    <div class="card">
      <h2>AI 分析计划</h2>
      <p style="color: #718096; font-size: 13px; margin-bottom: 12px">
        请审核以下分析计划，可以直接编辑修改，确认后点击执行。
      </p>
      <textarea class="plan-edit" :value="plan" @input="$emit('update:plan', $event.target.value)"></textarea>
    </div>
    <div class="btn-group">
      <button class="btn btn-outline" @click="$emit('back')">&#8592; 返回修改</button>
      <button class="btn btn-primary" :disabled="loading" @click="$emit('regenerate')">重新生成计划</button>
      <button class="btn btn-success" :disabled="loading" @click="$emit('execute')">
        {{ loading ? '正在执行分析...' : '确认并执行分析 →' }}
      </button>
    </div>
    <div class="loading-overlay" v-if="loading">
      <div class="spinner"></div>
      <p>{{ loadingMsg }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  plan: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  loadingMsg: { type: String, default: '' },
})
defineEmits(['update:plan', 'back', 'regenerate', 'execute'])
</script>
