<template>
  <div class="dp-config-section">
    <div class="dp-config-title">加权设置</div>
    <div class="dp-form-row">
      <label>权重变量</label>
      <select class="dp-select" v-model="options.weightVar">
        <option value="">请选择</option>
        <option v-for="v in numericVars" :key="v.name" :value="v.name">{{ v.name }}</option>
      </select>
    </div>
    <div class="dp-config-hint">选择的权重变量将用于对所选变量进行加权计算</div>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Object, required: true },
  numericVars: { type: Array, default: () => [] },
})
</script>
