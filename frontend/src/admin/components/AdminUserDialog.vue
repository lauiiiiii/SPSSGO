<template>
  <div class="admin-dialog-backdrop" @click.self="$emit('close')">
    <div class="admin-dialog">
      <div class="admin-dialog__head">
        <h3>{{ mode === 'create' ? '新建账户' : '编辑账户' }}</h3>
        <button class="admin-icon-btn" type="button" @click="$emit('close')">×</button>
      </div>
      <div class="admin-dialog__body admin-form-grid">
        <label class="admin-field">
          <span>用户名</span>
          <input :value="modelValue.username" type="text" maxlength="255" @input="updateField('username', $event.target.value)" />
        </label>
        <label class="admin-field">
          <span>角色</span>
          <select :value="modelValue.role" @change="updateField('role', $event.target.value)">
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
          </select>
        </label>
        <label v-if="mode === 'create'" class="admin-field admin-field--wide">
          <span>初始密码</span>
          <input :value="modelValue.password" type="password" maxlength="255" @input="updateField('password', $event.target.value)" />
        </label>
      </div>
      <div class="admin-dialog__footer">
        <button class="admin-ghost-btn" type="button" @click="$emit('close')">取消</button>
        <button class="admin-primary-btn" type="button" @click="$emit('submit')">{{ mode === 'create' ? '创建账户' : '保存修改' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  mode: { type: String, default: 'create' },
  modelValue: { type: Object, required: true },
})

const emit = defineEmits(['close', 'submit', 'update:modelValue'])

function updateField(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}
</script>
