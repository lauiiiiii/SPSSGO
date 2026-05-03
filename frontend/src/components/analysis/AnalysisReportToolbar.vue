<template>
  <header class="ap-report-toolbar">
    <div class="ap-report-title-block ap-report-title-block--stack">
      <span class="ap-report-title">{{ reportTitle }}</span>
      <div v-if="reportMetaTags.length" class="ap-report-meta">
        <span v-for="tag in reportMetaTags" :key="tag" class="ap-report-meta-chip">{{ tag }}</span>
      </div>
    </div>
    <div v-if="hasActions" class="ap-report-actions">
      <button v-if="showEditConfig" type="button" class="ap-rpt-link" @click="$emit('edit-config')">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M10 2L6 8l4 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        返回配置
      </button>
      <span v-if="showEditConfig && showExportActions" class="ap-rpt-sep"></span>
      <button v-if="showExportActions" type="button" class="ap-rpt-link" @click="$emit('export-pdf')">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 1h5l4 4v9a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2"/><path d="M9 1v4h4" stroke="currentColor" stroke-width="1.2"/></svg>
        导出PDF
      </button>
      <span v-if="showExportActions" class="ap-rpt-sep"></span>
      <button v-if="showExportActions" type="button" class="ap-rpt-link" @click="$emit('export-word')">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 1h5l4 4v9a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2"/><path d="M9 1v4h4" stroke="currentColor" stroke-width="1.2"/></svg>
        导出Word
      </button>
      <span v-if="showShare && (showEditConfig || showExportActions)" class="ap-rpt-sep"></span>
      <button v-if="showShare" type="button" class="ap-rpt-link" @click="$emit('share')">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M11 5a2 2 0 100-4 2 2 0 000 4zM4 10a2 2 0 100-4 2 2 0 000 4zM11 16a2 2 0 100-4 2 2 0 000 4z" stroke="currentColor" stroke-width="1.2"/><path d="M5.7 7.1l3.7-2.2M5.7 8.9l3.7 2.2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        分享
      </button>
      <span v-if="showCopyAll && (showEditConfig || showExportActions || showShare)" class="ap-rpt-sep"></span>
      <button v-if="showCopyAll" type="button" class="ap-rpt-link" @click="$emit('copy-all')">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
        复制全部
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  reportMetaTags: { type: Array, default: () => [] },
  reportTitle: { type: String, default: '分析报告' },
  showCopyAll: { type: Boolean, default: true },
  showEditConfig: { type: Boolean, default: true },
  showExportActions: { type: Boolean, default: true },
  showShare: { type: Boolean, default: false },
})

const hasActions = computed(() => (
  props.showEditConfig
  || props.showExportActions
  || props.showShare
  || props.showCopyAll
))

defineEmits(['copy-all', 'edit-config', 'export-pdf', 'export-word', 'share'])
</script>
