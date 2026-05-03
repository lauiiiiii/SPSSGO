<template>
  <teleport to="body">
    <div
      v-if="visible"
      class="hs-hover-menu"
      :style="menuStyle"
      @click.stop
    >
      <button class="hs-chip-action-btn" @click.stop="$emit('rename')">重命名</button>
      <button class="hs-chip-action-btn hs-chip-action-btn--danger" @click.stop="$emit('delete')">删除</button>
    </div>
  </teleport>
</template>

<script setup>
defineProps({
  menuStyle: { type: Object, default: () => ({}) },
  visible: { type: Boolean, default: false },
})

defineEmits(['rename', 'delete'])
</script>
