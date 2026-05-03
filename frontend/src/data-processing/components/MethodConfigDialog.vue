<template>
  <div class="dp-dialog-overlay" @click.self="$emit('close')">
    <div class="dp-dialog" :class="'dp-dialog--' + activeMethod">
      <div class="dp-dialog-head">
        <span>{{ activeMethodLabel }}
          <span
            class="dp-dialog-help"
            :class="{ 'dp-dialog-help--tooltip': !!dialogHelpText }"
            :data-tooltip="dialogHelpText"
          >?</span>
        </span>
        <button class="dp-dialog-close" @click="$emit('close')">&times;</button>
      </div>

      <div class="dp-dialog-body">
        <VariableSelectorPane
          :variables="variables"
          :selected-vars="selectedVars"
          :active-method="activeMethod"
          :needs-multi-var="needsMultiVar"
          :min-vars="minVars"
          :is-variable-selectable="isVariableSelectable"
          @toggle-var="$emit('toggle-var', $event)"
          @remove-var="$emit('remove-var', $event)"
          @toggle-menu="(...args) => $emit('toggle-menu', ...args)"
        />

        <div class="dp-config">
          <div v-if="errorMsg" class="dp-dialog-inline-error">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8.5" stroke="#ef4444" stroke-width="1.5"/><path d="M10 6v5M10 13.6h.01" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round"/></svg>
            <span>{{ errorMsg }}</span>
          </div>
          <component
            :is="activeMethodComponent"
            v-if="activeMethodComponent"
            :options="options"
            :label-rows="methodRuntime.labelRows"
            :label-editable="labelEditable"
            :label-hint-text="labelHintText"
            :selected-count="selectedVars.length"
            :encode-source-values="methodRuntime.encodeSourceValues"
            :encode-meta="methodRuntime.encodeMeta"
            :encode-hint-text="encodeHintText"
            :method-actions="methodActions"
            :numeric-vars="numericVars"
            :cat-vars="catVars"
          />
        </div>
      </div>

      <div class="dp-dialog-foot">
        <button class="dp-btn dp-btn--cancel" @click="$emit('close')">取消</button>
        <button class="dp-btn dp-btn--ok" @click="$emit('execute')" :disabled="processing">
          {{ processing ? '处理中...' : '确认' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import VariableSelectorPane from './VariableSelectorPane.vue'

defineProps({
  activeMethod: { type: String, default: '' },
  activeMethodComponent: { default: null },
  activeMethodLabel: { type: String, default: '' },
  catVars: { type: Array, default: () => [] },
  dialogHelpText: { type: String, default: '' },
  encodeHintText: { type: String, default: '' },
  errorMsg: { type: String, default: '' },
  isVariableSelectable: { type: Function, required: true },
  labelEditable: { type: Boolean, default: false },
  labelHintText: { type: String, default: '' },
  methodActions: { type: Object, default: () => ({}) },
  methodRuntime: { type: Object, required: true },
  minVars: { type: Number, default: 0 },
  needsMultiVar: { type: Boolean, default: false },
  numericVars: { type: Array, default: () => [] },
  options: { type: Object, required: true },
  processing: { type: Boolean, default: false },
  selectedVars: { type: Array, default: () => [] },
  variables: { type: Array, default: () => [] },
})

defineEmits(['close', 'execute', 'remove-var', 'toggle-menu', 'toggle-var'])
</script>
