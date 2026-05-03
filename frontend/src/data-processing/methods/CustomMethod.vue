<template>
  <div class="dp-config-section">
    <div class="dp-config-title">自定义处理</div>
    <div class="dp-form-row">
      <label>处理描述</label>
      <textarea class="dp-textarea" v-model="options.customDesc" placeholder="描述你要对数据做的处理，例如：将 q1 到 q5 求平均生成新变量 avg_score" rows="4"></textarea>
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
