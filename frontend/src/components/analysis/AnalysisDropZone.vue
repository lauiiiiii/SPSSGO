<template>
  <div
    class="ap-drop-zone"
    :class="[zoneClass, { 'drag-over': dragOverSlot === slotKey, 'has-items': values.length }]"
    @dragover.prevent="$emit('drag-over', slotKey)"
    @dragleave="handleDragLeave"
    @drop.prevent="$emit('drop-slot', $event, slot)"
    @click="$emit('zone-click')"
  >
    <template v-if="values.length">
      <div
        v-for="variableName in values"
        :key="variableName"
        class="ap-var-row"
      >
        <span class="ap-var-row-name">{{ variableName }}</span>
        <span class="ap-var-row-tag" :class="getVarTypeClass(variableName)">{{ getVarType(variableName) }}</span>
        <button class="ap-var-row-x" @click="$emit('remove-var', slotKey, variableName)">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.2"/><path d="M5.5 5.5l5 5M10.5 5.5l-5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        </button>
      </div>
      <div
        v-for="index in insertPreviewCount"
        :key="`preview-${index}`"
        class="ap-drop-insert-preview"
      ></div>
    </template>
    <template v-else>
      <div
        v-for="index in insertPreviewCount"
        :key="`preview-${index}`"
        class="ap-drop-insert-preview"
      ></div>
      <div v-if="!insertPreviewCount" class="ap-drop-empty" :class="{ 'with-preview': dragOverSlot === slotKey }">
        {{ emptyText }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dragOverSlot: { type: String, default: null },
  dragPreviewCount: { type: Number, default: 0 },
  emptyText: { type: String, default: '将待分析变量拖入到此区域' },
  getVarType: { type: Function, required: true },
  getVarTypeClass: { type: Function, required: true },
  slot: { type: Object, required: true },
  slotKey: { type: String, required: true },
  values: { type: Array, default: () => [] },
  zoneClass: { type: String, default: '' },
})

const emit = defineEmits(['drag-leave', 'drag-over', 'drop-slot', 'remove-var', 'zone-click'])

const insertPreviewCount = computed(() => {
  if (props.dragOverSlot !== props.slotKey) return 0
  const requestedCount = Math.max(1, Number(props.dragPreviewCount) || 1)
  if (props.slot?.type === 'single') return 1
  const max = Number(props.slot?.max)
  if (!Number.isFinite(max)) return requestedCount
  return Math.max(0, Math.min(requestedCount, max - props.values.length))
})

function handleDragLeave(event) {
  const nextTarget = event.relatedTarget
  if (nextTarget && event.currentTarget?.contains?.(nextTarget)) return
  emit('drag-leave')
}
</script>
