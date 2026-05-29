<template>
  <div class="admin-dialog-backdrop" @click.self="$emit('close')">
    <div class="admin-dialog admin-dialog--compact">
      <div class="admin-dialog__head">
        <h3>重置密码</h3>
        <button class="admin-icon-btn" type="button" @click="$emit('close')">×</button>
      </div>
      <div class="admin-dialog__body admin-form-grid">
        <label class="admin-field admin-field--wide">
          <span>新密码</span>
          <input :value="modelValue" type="password" maxlength="255" @input="$emit('update:modelValue', $event.target.value)" />
        </label>
      </div>
      <div class="admin-dialog__footer">
        <button class="admin-ghost-btn" type="button" @click="$emit('close')">取消</button>
        <button class="admin-primary-btn" type="button" @click="$emit('submit')">确认重置</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
})

defineEmits(['close', 'submit', 'update:modelValue'])
</script>
