<template>
  <div class="upload-overlay" @click.self="$emit('close')">
    <div class="upload-modal confirm-modal">
      <div class="upload-modal-head">
        <span>{{ dialog.title }}</span>
        <button class="upload-modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="confirm-modal-body">
        <p class="confirm-modal-text">{{ dialog.message }}</p>
      </div>
      <div class="confirm-modal-actions">
        <label v-if="dialog.type === 'history'" class="confirm-modal-check">
          <input
            :checked="dialog.suppressForHour"
            type="checkbox"
            @change="$emit('update-suppress', $event.target.checked)"
          />
          <span>1小时内不再提示</span>
        </label>
        <div class="confirm-modal-actions-right">
          <button class="md-page-btn md-page-btn--ghost" @click="$emit('close')">取消</button>
          <button class="confirm-modal-danger" @click="$emit('confirm')">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  dialog: { type: Object, required: true },
})

defineEmits(['close', 'confirm', 'update-suppress'])
</script>
