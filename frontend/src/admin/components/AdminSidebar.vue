<template>
  <aside class="admin-sidebar">
    <button
      v-for="item in items"
      :key="item.key"
      :class="['admin-sidebar__item', { 'is-active': activeTab === item.key }]"
      type="button"
      @click="$emit('change', item.key)"
    >
      <span class="admin-sidebar__icon" v-html="item.icon"></span>
      <span class="admin-sidebar__label">{{ item.label }}</span>
    </button>
  </aside>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  activeTab: { type: String, default: '' },
})

defineEmits(['change'])
</script>
