<template>
  <div v-if="executing" class="ap-results ap-results--overlay">
    <div class="ap-executing">
      <span class="ap-executing-spinner" aria-hidden="true"></span>
      <span class="ap-executing-text">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  executing: { type: Boolean, default: false },
  method: { type: Object, default: null },
})

const label = computed(() => (
  props.method?.label ? `${props.method.label} 算法分析中...` : '算法分析中...'
))
</script>
