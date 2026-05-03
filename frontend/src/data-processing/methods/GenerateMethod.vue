<template>
  <div class="dp-config-section">
    <div class="dp-config-title">新变量设置</div>
    <div class="dp-form-row">
      <label>新变量名称</label>
      <input class="dp-input" v-model="options.generateName" placeholder="new_var" />
    </div>
    <div class="dp-form-row">
      <label>计算公式</label>
      <input class="dp-input" v-model="options.generateExpr" placeholder="例：q1 + q2 * 0.5" />
    </div>
    <div class="dp-config-hint">可使用变量名和数学运算符（+ - * / **），以及函数：log, sqrt, abs, mean, sum</div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
