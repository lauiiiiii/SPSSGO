<template>
  <DataProcessingPanelFolder v-bind="$props" @variables-updated="$emit('variables-updated')" @go-analysis="$emit('go-analysis', $event)" />
</template>

<script setup>
import DataProcessingPanelFolder from '../data-processing/DataProcessingPanel.vue'

defineProps({
  sessionId: { type: String, default: '' },
  dataFileName: { type: String, default: '' },
  variables: { type: Array, default: () => [] },
  totalRows: { type: Number, default: 0 },
  hasData: { type: Boolean, default: false },
})

defineEmits(['variables-updated', 'go-analysis'])
</script>
