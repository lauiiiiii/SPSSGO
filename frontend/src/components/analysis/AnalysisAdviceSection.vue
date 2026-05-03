<template>
  <div class="ap-sec ap-sec--advice">
    <div class="ap-sec-label">
      <span class="ap-sec-label-dot ap-dot--blue"></span>
      {{ section.title }}
    </div>
    <div class="ap-sec-body">{{ section.content }}</div>
  </div>
</template>

<script setup>
defineProps({
  section: { type: Object, required: true },
})
</script>
