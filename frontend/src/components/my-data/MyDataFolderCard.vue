<template>
  <div
    class="md-card md-card--folder"
    :class="{ 'md-card--drop-active': dropActive }"
    @click="$emit('toggle', folder.id)"
    @contextmenu.prevent="$emit('open-menu', $event, folder)"
    @dragover.prevent="$emit('card-drag-over', folder.id)"
    @dragleave="$emit('card-drag-leave', $event, folder.id)"
    @drop.prevent="$emit('drop-card', $event, folder.id)"
  >
    <div class="md-card-icon md-card-icon--yellow">
      <svg width="24" height="24" viewBox="0 0 16 16" fill="none">
        <path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" :fill="open ? '#fef3c7' : '#fef9c3'"/>
      </svg>
    </div>
    <template v-if="renaming">
      <input
        :value="modelValue"
        class="md-inline-input md-card-input"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.enter="$emit('confirm-rename')"
        @keydown.escape="$emit('cancel-rename')"
        @blur="$emit('confirm-rename')"
        @click.stop
      />
    </template>
    <template v-else>
      <div class="md-card-label">{{ folder.name }}</div>
      <div class="md-card-meta">{{ fileCount }} 个文件</div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  dropActive: { type: Boolean, default: false },
  fileCount: { type: Number, default: 0 },
  folder: { type: Object, required: true },
  modelValue: { type: String, default: '' },
  open: { type: Boolean, default: false },
  renaming: { type: Boolean, default: false },
})

defineEmits([
  'cancel-rename',
  'card-drag-leave',
  'card-drag-over',
  'confirm-rename',
  'drop-card',
  'open-menu',
  'toggle',
  'update:modelValue',
])
</script>
