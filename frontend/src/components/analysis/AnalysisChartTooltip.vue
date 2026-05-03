<template>
  <div v-if="tip.show" class="ap-chart-tip" :style="{ left: tip.x + 'px', top: tip.y + 'px' }">
    <div v-for="(line, lineIndex) in tip.lines" :key="lineIndex" class="ap-chart-tip-line">
      <span v-if="line.dot" class="ap-chart-tip-dot" :style="{ background: line.dot }"></span>
      {{ line.text }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  tip: { type: Object, required: true },
})
</script>
