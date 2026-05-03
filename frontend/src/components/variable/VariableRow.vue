<template>
  <div
    class="vp-item"
    :class="{ selected, dragging }"
    draggable="true"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
    @dragstart="$emit('drag-start', $event, variable)"
    @dragend="$emit('drag-end')"
    @click="$emit('toggle', $event, variable)"
  >
    <span class="vp-var-name" :title="variableTitle">{{ variable.display_name || variable.name }}</span>
    <span class="vp-var-tag" :class="'t-' + variable.type">
      {{ variable.type === 'numeric' ? '定量' : variable.type === 'categorical' ? '定类' : '字符' }}
    </span>
    <button
      class="vp-more-btn"
      :class="{ visible: hovered || menuOpen }"
      type="button"
      title="变量操作"
      @click.stop="$emit('open-menu', variable, $event)"
    >
      <span></span><span></span><span></span>
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  variable: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  dragging: { type: Boolean, default: false },
  menuOpen: { type: Boolean, default: false },
})

defineEmits(['toggle', 'drag-start', 'drag-end', 'open-menu'])

const hovered = ref(false)

const variableTitle = computed(() => {
  const v = props.variable
  if (!v || !v.name) return ''
  if (v.display_name && v.display_name !== v.name) {
    return `${v.display_name}\n原始变量名: ${v.name}`
  }
  return v.name
})
</script>
