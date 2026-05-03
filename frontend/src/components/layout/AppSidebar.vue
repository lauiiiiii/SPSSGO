<template>
  <aside class="sidebar">
    <div class="sb-brand">
      <div class="sb-logo">数</div>
      <span class="sb-title">AI 数据分析</span>
    </div>

    <button class="sb-new" @click="$emit('new-session')">
      <span class="sb-new-icon">＋</span>
      新建分析
    </button>

    <div class="sb-label">历史分析</div>
    <div class="sb-history">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="sb-item"
        :class="{ active: s.id === currentId }"
        @click="$emit('switch-session', s.id)"
        @dblclick.stop="startRename(s)"
      >
        <span class="sb-item-dot" :class="'st-' + s.status"></span>

        <!-- Inline rename mode -->
        <input
          v-if="renamingId === s.id"
          ref="renameInputRef"
          class="sb-rename-input"
          v-model="renameText"
          @keydown.enter="finishRename(s)"
          @keydown.escape="cancelRename"
          @blur="finishRename(s)"
          @click.stop
        />

        <!-- Normal display -->
        <template v-else>
          <span class="sb-item-text">{{ s.research_topic || '未命名分析' }}</span>
          <span class="sb-item-time">{{ timeAgo(s.created_at) }}</span>
        </template>
      </div>
      <div v-if="!sessions.length" class="sb-empty">暂无历史分析</div>
    </div>

    <template v-if="currentId">
      <div class="sb-label" style="margin-top:4px">当前文件</div>
      <div class="sb-files">
        <div v-if="dataFile" class="sb-file" :class="{ active: activeFile === dataFile.name }" @click="$emit('select-file', { type:'data', name: dataFile.name })">
          <span class="sb-fi">📊</span>{{ dataFile.name }}
        </div>
        <div
          v-for="(q, i) in questFiles" :key="i"
          class="sb-file"
          :class="{ active: activeFile === q.name }"
          @click="$emit('select-file', { type:'quest', name: q.name, index: i })"
        >
          <span class="sb-fi">📝</span>{{ q.name }}
        </div>
        <button class="sb-upload" @click="$emit('trigger-quest')">＋ 上传问卷</button>
      </div>
    </template>

    <div class="sb-footer">数据分析助手</div>
  </aside>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  currentId: { type: String, default: '' },
  dataFile: Object,
  questFiles: { type: Array, default: () => [] },
  activeFile: { type: String, default: '' },
})
const emit = defineEmits(['new-session', 'switch-session', 'select-file', 'trigger-quest', 'rename'])

const renamingId = ref('')
const renameText = ref('')
const renameInputRef = ref(null)

function startRename(s) {
  renamingId.value = s.id
  renameText.value = s.research_topic || ''
  nextTick(() => {
    const inputs = renameInputRef.value
    if (inputs) {
      const el = Array.isArray(inputs) ? inputs[0] : inputs
      el?.focus()
      el?.select()
    }
  })
}

function finishRename(s) {
  if (!renamingId.value) return
  const newTitle = renameText.value.trim()
  renamingId.value = ''
  if (newTitle && newTitle !== (s.research_topic || '')) {
    emit('rename', s.id, newTitle)
  }
}

function cancelRename() {
  renamingId.value = ''
}

function timeAgo(ts) {
  if (!ts) return ''
  const diff = (Date.now() / 1000 - ts) | 0
  if (diff < 60) return '刚刚'
  if (diff < 3600) return ((diff / 60) | 0) + ' 分钟前'
  if (diff < 86400) return ((diff / 3600) | 0) + ' 小时前'
  if (diff < 604800) return ((diff / 86400) | 0) + ' 天前'
  return new Date(ts * 1000).toLocaleDateString()
}
</script>
