<template>
  <div class="steps">
    <div
      v-for="s in items"
      :key="s.num"
      class="step-item"
      :class="{ active: current === s.num, done: current > s.num }"
      @click="$emit('go', s.num)"
    >
      {{ s.num }}. {{ s.label }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  current: { type: Number, required: true },
})
defineEmits(['go'])

const items = [
  { num: 1, label: '上传文件' },
  { num: 2, label: '填写研究信息' },
  { num: 3, label: '分析计划' },
  { num: 4, label: '分析结果' },
]
</script>
