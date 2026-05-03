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
      <div v-if="dragOverSlot === slotKey" class="ap-drop-insert-preview"></div>
    </template>
    <template v-else>
      <div v-if="dragOverSlot === slotKey" class="ap-drop-insert-preview"></div>
      <div class="ap-drop-empty" :class="{ 'with-preview': dragOverSlot === slotKey }">
        {{ emptyText }}
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  dragOverSlot: { type: String, default: null },
  emptyText: { type: String, default: '将待分析变量拖入到此区域' },
  getVarType: { type: Function, required: true },
  getVarTypeClass: { type: Function, required: true },
  slot: { type: Object, required: true },
  slotKey: { type: String, required: true },
  values: { type: Array, default: () => [] },
  zoneClass: { type: String, default: '' },
})

const emit = defineEmits(['drag-leave', 'drag-over', 'drop-slot', 'remove-var', 'zone-click'])

function handleDragLeave(event) {
  const nextTarget = event.relatedTarget
  if (nextTarget && event.currentTarget?.contains?.(nextTarget)) return
  emit('drag-leave')
}
</script>
