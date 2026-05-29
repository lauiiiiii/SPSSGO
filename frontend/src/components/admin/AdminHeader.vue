<template>
  <header class="admin-header">
    <div class="admin-header__brand">
      <img class="admin-header__logo" src="/logo.png" alt="SPSSGO" />
      <div>
        <div class="admin-header__eyebrow">SPSSGO</div>
        <h1 class="admin-header__title">管理控制台</h1>
      </div>
    </div>
    <div class="admin-header__actions">
      <a class="admin-header__link" href="/workspace">前往工作台</a>
      <div class="admin-header__user">
        <span class="admin-header__name">{{ username }}</span>
        <span class="admin-header__role">管理员</span>
      </div>
      <button class="admin-ghost-btn" type="button" @click="$emit('logout')">退出登录</button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  username: { type: String, default: '' },
})

defineEmits(['logout'])
</script>
