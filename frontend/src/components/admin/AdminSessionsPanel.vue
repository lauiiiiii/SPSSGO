<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Sessions</div>
        <h2>会话管理</h2>
      </div>
      <div class="admin-panel__actions">
        <button class="admin-ghost-btn" type="button" @click="$emit('refresh')">刷新</button>
        <button class="admin-primary-btn is-danger" type="button" @click="$emit('cleanup')">清理过期会话</button>
      </div>
    </div>

    <div v-if="error" class="admin-state is-error">{{ error }}</div>
    <div v-else-if="loading" class="admin-state">会话列表加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>会话 ID</th>
            <th>研究主题</th>
            <th>状态</th>
            <th>分析数</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in sessions" :key="session.id">
            <td class="admin-mono">{{ session.id }}</td>
            <td>{{ session.research_topic || '—' }}</td>
            <td><span :class="['admin-badge', `is-session-${session.status}`]">{{ statusLabel(session.status) }}</span></td>
            <td>{{ session.result_count || 0 }}</td>
            <td>{{ formatTime(session.created_at) }}</td>
            <td><button class="admin-icon-btn is-danger" type="button" title="删除会话" @click="$emit('delete', session)">删</button></td>
          </tr>
          <tr v-if="!sessions.length">
            <td colspan="6" class="admin-empty-cell">暂无会话数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > size" class="admin-pagination">
      <button class="admin-ghost-btn" type="button" :disabled="page <= 1" @click="$emit('change-page', page - 1)">上一页</button>
      <span>第 {{ page }} / {{ Math.ceil(total / size) }} 页</span>
      <button class="admin-ghost-btn" type="button" :disabled="page >= Math.ceil(total / size)" @click="$emit('change-page', page + 1)">下一页</button>
    </div>
  </section>
</template>

<script setup>
import { getSessionStatusLabel } from '@/constants/sessionStatus.js'

defineProps({
  sessions: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  size: { type: Number, default: 12 },
})

defineEmits(['refresh', 'cleanup', 'delete', 'change-page'])

function formatTime(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('zh-CN')
}

function statusLabel(status) {
  return getSessionStatusLabel(status)
}
</script>
