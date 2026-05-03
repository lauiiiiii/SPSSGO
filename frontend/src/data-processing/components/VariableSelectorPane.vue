<template>
  <div class="dp-var-select">
    <div class="dp-var-title">选择变量</div>
    <div class="dp-var-list">
      <div
        v-for="variable in variables"
        :key="variable.name"
        class="dp-var-item"
        :class="{ selected: selectedVars.includes(variable.name), disabled: !isVariableSelectable(variable) }"
        @click="$emit('toggle-var', variable)"
      >
        <span class="dp-var-name">{{ variable.name }}</span>
        <span class="dp-var-tag" :class="getVarTagClass(variable)">
          {{ getVarTypeLabel(variable) }}
        </span>
        <button class="dp-var-more" @click.stop="$emit('toggle-menu', $event, variable)">
          <svg viewBox="0 0 5632 1024" aria-hidden="true">
            <path d="M512 512m-512 0a512 512 0 1 0 1024 0 512 512 0 1 0-1024 0Z"></path>
            <path d="M2816 512m-512 0a512 512 0 1 0 1024 0 512 512 0 1 0-1024 0Z"></path>
            <path d="M5120 512m-512 0a512 512 0 1 0 1024 0 512 512 0 1 0-1024 0Z"></path>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="needsMultiVar" class="dp-var-selected">
      <div class="dp-var-title">已选变量 <span v-if="minVars">(变量数&ge;{{ minVars }})</span></div>
      <div class="dp-var-selected-area">
        <div v-if="!selectedVars.length" class="dp-var-drop-hint">
          <span
            v-for="(segment, index) in selectionHintSegments"
            :key="`${activeMethod}-${index}`"
            :class="segment.className"
          >{{ segment.text }}</span>
        </div>
        <div v-for="name in selectedVars" :key="name" class="dp-var-chip">
          {{ name }}
          <button @click="$emit('remove-var', name)">&times;</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getSelectionHintSegments } from '../methodSelectionHints.js'
import { getVarTagClass, getVarTypeLabel } from '../variableDisplay.js'

const props = defineProps({
  variables: { type: Array, default: () => [] },
  selectedVars: { type: Array, default: () => [] },
  activeMethod: { type: String, default: '' },
  needsMultiVar: { type: Boolean, default: false },
  minVars: { type: Number, default: 0 },
  isVariableSelectable: { type: Function, required: true },
})

defineEmits(['toggle-var', 'remove-var', 'toggle-menu'])

const selectionHintSegments = computed(() => getSelectionHintSegments(props.activeMethod))
</script>
