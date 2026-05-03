<template>
  <div class="pf-section">
    <h3 class="pf-section-title">基本信息</h3>
    <div class="pf-card">
      <div class="pf-avatar-row">
        <div class="pf-avatar">{{ avatarChar }}</div>
        <div class="pf-avatar-info">
          <div class="pf-name">{{ username }}</div>
          <div class="pf-role">管理员</div>
        </div>
      </div>
      <div class="pf-form-group">
        <label class="pf-label">用户名</label>
        <div class="pf-inline-edit">
          <input class="pf-input" :value="editName" :disabled="!editingName" @input="$emit('update:edit-name', $event.target.value)" />
          <template v-if="!editingName">
            <button class="pf-edit-btn" @click="$emit('start-edit')">修改</button>
          </template>
          <template v-else>
            <button class="pf-edit-btn pf-edit-btn--ok" :disabled="nameLoading" @click="$emit('save-name')">保存</button>
            <button class="pf-edit-btn" @click="$emit('cancel-edit')">取消</button>
          </template>
        </div>
        <div v-if="nameMsg" class="pf-msg" :class="nameOk ? 'pf-msg--ok' : 'pf-msg--err'">{{ nameMsg }}</div>
      </div>
      <div class="pf-form-group">
        <label class="pf-label">账户创建时间</label>
        <input class="pf-input" :value="createdAt" disabled />
      </div>
      <div class="pf-form-group">
        <label class="pf-label">上次登录</label>
        <input class="pf-input" :value="lastLogin" disabled />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  avatarChar: { type: String, default: 'U' },
  createdAt: { type: String, default: '' },
  editingName: { type: Boolean, default: false },
  editName: { type: String, default: '' },
  lastLogin: { type: String, default: '' },
  nameLoading: { type: Boolean, default: false },
  nameMsg: { type: String, default: '' },
  nameOk: { type: Boolean, default: false },
  username: { type: String, default: '' },
})

defineEmits(['cancel-edit', 'save-name', 'start-edit', 'update:edit-name'])
</script>
