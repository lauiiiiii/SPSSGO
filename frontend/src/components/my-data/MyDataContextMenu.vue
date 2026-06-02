<template>
  <div v-if="contextMenu.visible" class="md-ctx-menu" :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }">
    <template v-if="contextMenu.type === 'ds'">
      <div class="md-ctx-item" @click="$emit('start-rename-ds')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M11.5 1.5l3 3L5 14H2v-3L11.5 1.5z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        重命名
      </div>
      <div class="md-ctx-sep"></div>
      <div class="md-ctx-item" @click="$emit('go-processing', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 2h5v5H2zM9 2h5v5H9zM2 9h5v5H2zM9 9h5v5H9z" stroke="currentColor" stroke-width="1.1"/></svg>
        数据处理
      </div>
      <div class="md-ctx-item" @click="$emit('go-analysis', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 14V6l3-4h6l3 4v8H2z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><path d="M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
        数据分析
      </div>
      <div class="md-ctx-item" @click="$emit('go-visualization', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 12.5h12M3.5 12.5V7.5M7 12.5V4.5M10.5 12.5V9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M2 14h12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        可视化绘图
      </div>
      <div class="md-ctx-sep"></div>
      <div class="md-ctx-item" @click="$emit('export-dataset', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 2v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        导出当前版本
      </div>
      <div class="md-ctx-item" @click="$emit('copy-dataset', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
        复制当前版本
      </div>
      <div v-if="folders.length" class="md-ctx-sep"></div>
      <div v-for="folder in folders" :key="folder.id" class="md-ctx-item" @click="$emit('move-ds-to-folder', folder.id)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        移入「{{ folder.name }}」
      </div>
      <div v-if="contextMenu.inFolder" class="md-ctx-item" @click="$emit('move-ds-to-folder', '')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M10 2H6L4 4H1v10h14V4h-3L10 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M5 9h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        移出文件夹
      </div>
      <div class="md-ctx-sep"></div>
      <div class="md-ctx-item md-ctx-item--danger" @click="$emit('delete-dataset', contextMenu.target.sessionId)">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M5 4V2h6v2M6 7v5M10 7v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M3 4l1 10h8l1-10" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        删除
      </div>
    </template>
    <template v-if="contextMenu.type === 'folder'">
      <div class="md-ctx-item" @click="$emit('start-rename-folder')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M11.5 1.5l3 3L5 14H2v-3L11.5 1.5z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        重命名
      </div>
      <div class="md-ctx-sep"></div>
      <div class="md-ctx-item md-ctx-item--danger" @click="$emit('delete-folder')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M5 4V2h6v2M6 7v5M10 7v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M3 4l1 10h8l1-10" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        删除文件夹
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  contextMenu: { type: Object, required: true },
  folders: { type: Array, default: () => [] },
})

defineEmits([
  'copy-dataset',
  'delete-dataset',
  'delete-folder',
  'export-dataset',
  'go-analysis',
  'go-processing',
  'go-visualization',
  'move-ds-to-folder',
  'start-rename-ds',
  'start-rename-folder',
])
</script>
