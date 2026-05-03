<template>
  <div class="pf-section">
    <h3 class="pf-section-title">修改密码</h3>
    <div class="pf-card">
      <div class="pf-form-group">
        <label class="pf-label">当前密码</label>
        <input class="pf-input" type="password" v-model="pwForm.oldPwd" placeholder="请输入当前密码" />
      </div>
      <div class="pf-form-group">
        <label class="pf-label">新密码</label>
        <input class="pf-input" type="password" v-model="pwForm.newPwd" placeholder="请输入新密码（至少6位）" />
      </div>
      <div class="pf-form-group">
        <label class="pf-label">确认新密码</label>
        <input class="pf-input" type="password" v-model="pwForm.confirmPwd" placeholder="请再次输入新密码" />
      </div>
      <div v-if="pwMsg" class="pf-msg" :class="pwOk ? 'pf-msg--ok' : 'pf-msg--err'">{{ pwMsg }}</div>
      <button class="pf-submit" :disabled="pwLoading" @click="$emit('change-password')">
        {{ pwLoading ? '提交中...' : '修改密码' }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pwForm: { type: Object, required: true },
  pwLoading: { type: Boolean, default: false },
  pwMsg: { type: String, default: '' },
  pwOk: { type: Boolean, default: false },
})

defineEmits(['change-password'])
</script>
