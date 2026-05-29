<template>
  <article :class="['admin-stat-card', tone ? `is-${tone}` : '']">
    <div class="admin-stat-card__label">{{ label }}</div>
    <div class="admin-stat-card__value">{{ value }}</div>
    <div v-if="hint" class="admin-stat-card__hint">{{ hint }}</div>
  </article>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number], default: '0' },
  hint: { type: String, default: '' },
  tone: { type: String, default: '' },
})
</script>
