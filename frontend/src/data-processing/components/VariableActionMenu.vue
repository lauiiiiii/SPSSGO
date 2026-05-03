<template>
  <div
    class="dp-var-menu"
    :style="{ left: `${menu.x}px`, top: `${menu.y}px` }"
    @click.stop
  >
    <button class="dp-var-menu-item" @click="$emit('toggle-type')">
      <span class="dp-var-menu-icon">⇆</span>
      {{ menu.target?.type === 'numeric' ? '转化为定类' : '转化为定量' }}
    </button>
    <button class="dp-var-menu-item" @click="$emit('rename')">
      <span class="dp-var-menu-icon">✎</span>
      重命名
    </button>
    <button class="dp-var-menu-item" @click="$emit('delete')">
      <span class="dp-var-menu-icon">🗑</span>
      删除
    </button>
  </div>
</template>

<script setup>
defineProps({
  menu: { type: Object, required: true },
})

defineEmits(['toggle-type', 'rename', 'delete'])
</script>
