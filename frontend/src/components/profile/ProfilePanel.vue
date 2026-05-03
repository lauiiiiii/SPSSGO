<template>
  <div class="profile-panel">
    <div class="pf-container">
      <div class="pf-sidebar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="pf-sidebar-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <component :is="tab.icon" />
          {{ tab.label }}
        </button>
      </div>
      <div class="pf-content">
        <ProfileInfoSection
          v-if="activeTab === 'info'"
          :avatar-char="avatarChar"
          :created-at="createdAt"
          :editing-name="editingName"
          :edit-name="editName"
          :last-login="lastLogin"
          :name-loading="nameLoading"
          :name-msg="nameMsg"
          :name-ok="nameOk"
          :username="username"
          @cancel-edit="cancelEditingName"
          @save-name="saveName"
          @start-edit="startEditingName"
          @update:edit-name="editName = $event"
        />

        <ProfilePasswordSection
          v-if="activeTab === 'password'"
          :pw-form="pwForm"
          :pw-loading="pwLoading"
          :pw-msg="pwMsg"
          :pw-ok="pwOk"
          @change-password="changePassword"
        />

        <ProfileAboutSection
          v-if="activeTab === 'about'"
          @copy="copyText"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, ref } from 'vue'
import ProfileAboutSection from './ProfileAboutSection.vue'
import ProfileInfoSection from './ProfileInfoSection.vue'
import ProfilePasswordSection from './ProfilePasswordSection.vue'
import { useProfileAccount } from '../../composables/shared/useProfileAccount.js'

const activeTab = ref('info')

const IconUser = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', innerHTML: '<circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.2"/><path d="M2 14c0-3.3 2.7-5 6-5s6 1.7 6 5" stroke="currentColor" stroke-width="1.2"/>' }) } }
const IconLock = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', innerHTML: '<rect x="3" y="7" width="10" height="7" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M5 7V5a3 3 0 016 0v2" stroke="currentColor" stroke-width="1.2"/>' }) } }
const IconInfo = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', innerHTML: '<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2"/><path d="M8 7v4M8 5.5v0" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>' }) } }

const tabs = [
  { key: 'info', label: '基本信息', icon: IconUser },
  { key: 'password', label: '修改密码', icon: IconLock },
  { key: 'about', label: '关于系统', icon: IconInfo },
]

const {
  avatarChar,
  cancelEditingName,
  changePassword,
  copyText,
  createdAt,
  editingName,
  editName,
  lastLogin,
  nameLoading,
  nameMsg,
  nameOk,
  pwForm,
  pwLoading,
  pwMsg,
  pwOk,
  saveName,
  startEditingName,
  username,
} = useProfileAccount()
</script>
