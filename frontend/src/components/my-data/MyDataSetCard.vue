<template>
  <div
    class="md-card md-card--file"
    :class="{ 'md-card--active': dataSet.isCurrent }"
    draggable="true"
    @click="!dataSet.isCurrent && $emit('switch', dataSet.sessionId)"
    @contextmenu.prevent="$emit('open-menu', $event, dataSet, inFolder)"
    @dragstart="$emit('drag-start', $event, dataSet.sessionId)"
  >
    <label
      v-if="selectable"
      class="md-card-select"
      :class="{ 'md-card-select--checked': selected }"
      @click.stop
    >
      <input
        type="checkbox"
        :checked="selected"
        @change="$emit('select', dataSet.sessionId)"
      />
    </label>
    <button class="md-card-more md-tooltip" @click.stop="$emit('open-menu-button', $event, dataSet, inFolder)" aria-label="更多操作" data-tooltip="更多操作">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="4" cy="8" r="1.1" fill="currentColor"/>
        <circle cx="8" cy="8" r="1.1" fill="currentColor"/>
        <circle cx="12" cy="8" r="1.1" fill="currentColor"/>
      </svg>
    </button>
    <div class="md-card-icon md-card-icon--green">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="currentColor" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="currentColor" stroke-width="1" opacity=".35"/></svg>
    </div>
    <template v-if="renaming">
      <input
        :value="modelValue"
        class="md-inline-input md-card-input"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.enter="$emit('confirm-rename', dataSet)"
        @keydown.escape="$emit('cancel-rename')"
        @blur="$emit('confirm-rename', dataSet)"
        @click.stop
      />
    </template>
    <template v-else>
      <div class="md-card-label">{{ dataSet.topic || dataSet.fileName }}</div>
      <div class="md-card-meta">
        <span>{{ datasetMeta }}</span>
        <span>{{ formatDate(dataSet.createdAt) }}</span>
      </div>
    </template>
    <span v-if="dataSet.currentVersionNo" class="md-card-version">v{{ dataSet.currentVersionNo }}</span>
    <span v-if="dataSet.isCurrent" class="md-card-badge">当前</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dataSet: { type: Object, required: true },
  formatDate: { type: Function, required: true },
  inFolder: { type: Boolean, default: false },
  modelValue: { type: String, default: '' },
  renaming: { type: Boolean, default: false },
  selectable: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
})

const datasetMeta = computed(() => {
  const parts = []
  if (props.dataSet.rowCount || props.dataSet.columnCount) {
    parts.push(`${props.dataSet.rowCount || 0} 行 / ${props.dataSet.columnCount || 0} 列`)
  }
  if (props.dataSet.fileSize) parts.push(props.dataSet.fileSize)
  if (props.dataSet.versionCount) parts.push(`${props.dataSet.versionCount} 个版本`)
  if (props.dataSet.resultCount) parts.push(`${props.dataSet.resultCount} 条分析`)
  return parts.join(' · ') || '数据集'
})

defineEmits([
  'cancel-rename',
  'confirm-rename',
  'drag-start',
  'open-menu',
  'open-menu-button',
  'select',
  'switch',
  'update:modelValue',
])
</script>
