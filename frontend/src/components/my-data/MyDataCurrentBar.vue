<template>
  <div v-if="dataFileName" class="md-current-bar">
    <div class="md-current-bar-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="currentColor" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="currentColor" stroke-width="1" opacity=".4"/></svg>
    </div>
    <div class="md-current-bar-info">
      <div class="md-current-bar-title">
        <span class="md-current-bar-name">{{ dataFileName }}</span>
        <span v-if="currentVersionNo" class="md-current-bar-version">v{{ currentVersionNo }}</span>
      </div>
      <span class="md-current-bar-meta">{{ datasetMeta }}</span>
    </div>
    <div class="md-current-bar-actions">
      <button class="md-bar-btn md-bar-btn--teal" @click="$emit('go-processing', currentSessionId)">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M2 2h5v5H2zM9 2h5v5H9zM2 9h5v5H2zM9 9h5v5H9z" stroke="currentColor" stroke-width="1.1"/></svg>
        数据处理
      </button>
      <button class="md-bar-btn md-bar-btn--blue" @click="$emit('go-analysis', currentSessionId)">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M2 14V6l3-4h6l3 4v8H2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
        数据分析
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentSessionId: { type: String, default: '' },
  dataFileName: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variableCount: { type: Number, default: 0 },
  versionCount: { type: Number, default: 0 },
  resultCount: { type: Number, default: 0 },
  currentVersionNo: { type: [Number, String], default: null },
})

defineEmits(['go-analysis', 'go-processing'])

const datasetMeta = computed(() => {
  const parts = [`${props.totalRows} 行`, `${props.variableCount} 个变量`]
  if (props.versionCount) parts.push(`${props.versionCount} 个版本`)
  if (props.resultCount) parts.push(`${props.resultCount} 条分析`)
  return parts.join(' · ')
})
</script>
