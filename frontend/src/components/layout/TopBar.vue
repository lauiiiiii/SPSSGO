<template>
  <header class="topbar">
    <div class="topbar-brand">
      <img class="topbar-logo-img" src="/logo.png" alt="SPSSGO" />
    </div>
    <nav class="topbar-nav">
      <button class="topbar-tab" :class="{ active: activeTab === 'mydata' }" @click="$emit('tab-change', 'mydata')">我的数据</button>
      <button class="topbar-tab" :class="{ active: activeTab === 'processing' }" @click="$emit('tab-change', 'processing')">数据处理</button>
      <button class="topbar-tab" :class="{ active: activeTab === 'analysis' }" @click="$emit('tab-change', 'analysis')">数据分析</button>
      <button class="topbar-tab disabled">可视化绘图</button>
      <button class="topbar-tab disabled">文本分析</button>
    </nav>
    <div class="topbar-actions">
      <button class="topbar-btn" @click="$emit('toggle-tasks')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 4h10M3 8h10M3 12h6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
        任务
        <span v-if="activeJobCount" class="topbar-badge">{{ activeJobCount }}</span>
      </button>
      <button class="topbar-btn primary" @click="$emit('toggle-ai')">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 1L1 5l7 3.5L15 5 8 1zM1 11l7 3.5L15 11M1 8l7 3.5L15 8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        AI 助手
      </button>
      <div class="tb-user-wrap" @mouseenter="showMenu = true" @mouseleave="showMenu = false">
        <div class="tb-user-avatar">{{ avatarChar }}</div>
        <span class="tb-user-name">{{ username }}</span>
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <transition name="tb-menu-fade">
          <div v-if="showMenu" class="tb-user-menu">
            <div class="tb-menu-header">
              <div class="tb-menu-avatar">{{ avatarChar }}</div>
              <div class="tb-menu-info">
                <div class="tb-menu-name">{{ username }}</div>
              </div>
            </div>
            <div class="tb-menu-divider"></div>
            <button class="tb-menu-item" @click="showMenu = false; $emit('tab-change', 'profile')">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.2"/><path d="M2 14c0-3.3 2.7-5 6-5s6 1.7 6 5" stroke="currentColor" stroke-width="1.2"/></svg>
              个人中心
            </button>
            <button class="tb-menu-item" @click="showMenu = false">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2l1.5 3h3.5l-2.8 2 1 3.5L8 8.5 4.8 10.5l1-3.5L3 5h3.5L8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
              建议反馈
            </button>
            <div class="tb-menu-divider"></div>
            <button class="tb-menu-item tb-menu-item--danger" @click="handleLogout">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M11 11l3-3-3-3M6 8h8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              退出登录
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { logout, getUsername } from '../../api.js'

defineProps({
  hasResults: { type: Boolean, default: false },
  activeTab: { type: String, default: 'analysis' },
  activeJobCount: { type: Number, default: 0 },
})
defineEmits(['upload', 'export', 'toggle-ai', 'toggle-tasks', 'tab-change'])

const username = computed(() => getUsername())
const avatarChar = computed(() => (username.value || 'U')[0].toUpperCase())
const showMenu = ref(false)

function handleLogout() {
  showMenu.value = false
  if (confirm('确认退出登录？')) logout()
}
</script>

<style scoped>
.topbar-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
}
</style>
