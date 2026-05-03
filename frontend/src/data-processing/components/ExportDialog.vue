<template>
  <div class="dp-dialog-overlay" @click.self="$emit('close')">
    <div class="dp-export-dialog">
      <div class="dp-dialog-head">
        <span>导出数据</span>
        <button class="dp-dialog-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="dp-export-body">
        <div class="dp-export-title">选择数据格式</div>
        <div class="dp-export-grid">
          <button
            v-for="format in formats"
            :key="format.key"
            class="dp-export-chip"
            @click="$emit('export-format', format.key)"
          >
            <b>{{ format.label }}</b>
            <span>{{ format.ext }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  formats: { type: Array, default: () => [] },
})

defineEmits(['close', 'export-format'])
</script>
