<template>
  <div class="card">
    <h2>{{ title }}</h2>
    <div
      class="upload-zone"
      :class="{ dragging: dragOver }"
      :style="zoneStyle"
      @click="fileInput?.click()"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop.prevent="onDrop"
    >
      <div class="icon">{{ icon }}</div>
      <p>{{ hint }}</p>
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        style="display: none"
        @change="onChange"
      />
    </div>
    <div v-if="file" style="margin-top: 12px">
      <span class="file-tag">
        {{ file.name }}
        <span class="remove" @click="$emit('clear')">&times;</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  accept: { type: String, default: '' },
  dragEnabled: { type: Boolean, default: false },
  file: { type: Object, default: null },
  hint: { type: String, default: '' },
  icon: { type: String, default: '' },
  padded: { type: Boolean, default: false },
  title: { type: String, required: true },
})

const emit = defineEmits(['clear', 'select'])

const dragOver = ref(false)
const fileInput = ref(null)

const zoneStyle = computed(() => (props.padded ? { padding: '30px' } : null))

function onChange(event) {
  const file = event.target.files[0]
  if (file) emit('select', file)
}

function onDragOver() {
  if (props.dragEnabled) dragOver.value = true
}

function onDragLeave() {
  if (props.dragEnabled) dragOver.value = false
}

function onDrop(event) {
  if (!props.dragEnabled) return
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) emit('select', file)
}
</script>
