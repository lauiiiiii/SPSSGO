<template>
  <div class="ap-sec ap-sec--refs">
    <div class="ap-sec-label">
      <span class="ap-sec-label-dot ap-dot--gray"></span>
      {{ section.title }}
    </div>
    <ul class="ap-sec-refs-list">
      <li v-for="(item, itemIndex) in section.items" :key="itemIndex">{{ item }}</li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  section: { type: Object, required: true },
})
</script>
