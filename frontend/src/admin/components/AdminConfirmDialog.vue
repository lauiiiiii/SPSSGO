<template>
  <div class="admin-dialog-backdrop" @click.self="$emit('cancel')">
    <div class="admin-dialog admin-dialog--compact">
      <div class="admin-dialog__head">
        <h3>{{ title }}</h3>
        <button class="admin-icon-btn" type="button" @click="$emit('cancel')">×</button>
      </div>
      <div class="admin-dialog__body">
        <p class="admin-dialog__text">{{ message }}</p>
      </div>
      <div class="admin-dialog__footer">
        <button class="admin-ghost-btn" type="button" @click="$emit('cancel')">取消</button>
        <button :class="['admin-primary-btn', danger ? 'is-danger' : '']" type="button" @click="$emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '确认' },
  danger: { type: Boolean, default: false },
})

defineEmits(['cancel', 'confirm'])
</script>
