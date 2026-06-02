<template>
  <div class="dp-topbar">
    <div class="dp-topbar-info">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="#2563eb" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="#2563eb" stroke-width="1" opacity=".35"/></svg>
      <span class="dp-topbar-name">{{ dataFileName }}</span>
      <span class="dp-topbar-meta">{{ totalRows }} 行 &middot; {{ variablesCount }} 个变量</span>
      <span v-if="currentVersionNo" class="dp-version-badge">v{{ currentVersionNo }}</span>
    </div>
    <div class="dp-topbar-actions">
      <div class="dp-view-tabs">
        <button :class="{ active: viewMode === 'code' }" @click="$emit('update:viewMode', 'code')">编码视图</button>
        <button :class="{ active: viewMode === 'label' }" @click="$emit('update:viewMode', 'label')">标签视图</button>
      </div>
      <button class="dp-topbar-btn" @click="$emit('open-version')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v6l3 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3"/></svg>
        版本
      </button>
      <button class="dp-topbar-btn" @click="$emit('go-analysis')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 14V6l3-4h6l3 4v8H2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
        数据分析
      </button>
      <button class="dp-topbar-btn" @click="$emit('go-visualization')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 12.5h12M3.5 12.5V7.5M7 12.5V4.5M10.5 12.5V9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M2 14h12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        可视化绘图
      </button>
      <button class="dp-topbar-btn" @click="$emit('export-current')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 11v3h12v-3M8 2v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        导出
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  dataFileName: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variablesCount: { type: Number, default: 0 },
  currentVersionNo: { type: [String, Number], default: '' },
  viewMode: { type: String, default: 'code' },
})

defineEmits(['update:viewMode', 'open-version', 'go-analysis', 'go-visualization', 'export-current'])
</script>
