<template>
  <teleport to="body">
    <div
      v-if="visible && variable"
      class="vp-context-menu"
      :style="menuStyle"
      @click.stop
    >
      <button class="vp-context-item" type="button" @click="$emit('change-type', conversionTarget)">
        <span class="vp-context-icon">↔</span>
        {{ conversionLabel }}
      </button>
      <button class="vp-context-item" type="button" @click="$emit('rename')">
        <span class="vp-context-icon">✎</span>
        重命名
      </button>
      <button class="vp-context-item" type="button" @click="$emit('batch-rename')">
        <span class="vp-context-icon">▦</span>
        批量命名
      </button>
      <button class="vp-context-item vp-context-item--danger" type="button" @click="$emit('delete')">
        <span class="vp-context-icon">⌫</span>
        删除
      </button>
    </div>
  </teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  variable: { type: Object, default: null },
  position: { type: Object, default: () => ({ top: 0, left: 0 }) },
})

const emit = defineEmits(['close', 'change-type', 'rename', 'batch-rename', 'delete'])

const menuStyle = computed(() => ({
  top: `${props.position.top || 0}px`,
  left: `${props.position.left || 0}px`,
}))

const conversionTarget = computed(() => (
  props.variable?.type === 'categorical' ? 'numeric' : 'categorical'
))

const conversionLabel = computed(() => (
  conversionTarget.value === 'numeric' ? '转化为定量' : '转化为定类'
))

function closeFromOutside(e) {
  const target = e.target
  if (target?.closest?.('.vp-context-menu') || target?.closest?.('.vp-more-btn')) return
  emit('close')
}

onMounted(() => {
  document.addEventListener('click', closeFromOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeFromOutside)
})
</script>
