<template>
  <div class="dp-config-section dp-config-section--label">
    <div class="dp-config-title">管理标签</div>
    <div v-if="labelRows.length && labelEditable" class="dp-label-editor">
      <div class="dp-label-editor-head">
        <span>数值</span>
        <span></span>
        <span>标签</span>
      </div>
      <div class="dp-label-values">
        <div v-for="(row, i) in labelRows" :key="`${row.value}-${i}`" class="dp-label-row">
          <input class="dp-input dp-input-sm dp-label-value-input" :value="row.value" disabled />
          <span class="dp-label-equals">表示</span>
          <input class="dp-input dp-input-sm dp-label-text-input" v-model="options.labelMap[row.value]" />
        </div>
      </div>
    </div>
    <div v-else-if="labelRows.length" class="dp-label-editor dp-label-editor--readonly">
      <div class="dp-label-editor-head dp-label-editor-head--single">
        <span>数值</span>
      </div>
      <div class="dp-label-values">
        <div v-for="(row, i) in labelRows" :key="`${row.value}-${i}`" class="dp-label-row dp-label-row--single">
          <input class="dp-input dp-input-sm dp-label-value-input" :value="row.value" disabled />
        </div>
      </div>
    </div>
    <div v-else class="dp-label-empty">
      <div class="dp-config-hint">{{ labelHintText }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Object, required: true },
  labelRows: { type: Array, default: () => [] },
  labelEditable: { type: Boolean, default: false },
  labelHintText: { type: String, default: '' },
})
</script>
