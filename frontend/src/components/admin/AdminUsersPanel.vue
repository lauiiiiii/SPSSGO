<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Accounts</div>
        <h2>账户管理</h2>
      </div>
      <button class="admin-primary-btn" type="button" @click="$emit('create')">新建账户</button>
    </div>

    <div class="admin-toolbar">
      <div class="admin-toolbar__filters">
        <input :value="filters.keyword" class="admin-search" type="text" placeholder="搜索用户名" @input="$emit('update:filters', { ...filters, keyword: $event.target.value })" />
        <select :value="filters.role" @change="$emit('update:filters', { ...filters, role: $event.target.value })">
          <option value="">全部角色</option>
          <option value="user">普通用户</option>
          <option value="admin">管理员</option>
        </select>
        <select :value="filters.is_active" @change="$emit('update:filters', { ...filters, is_active: $event.target.value })">
          <option value="">全部状态</option>
          <option value="1">启用中</option>
          <option value="0">已停用</option>
        </select>
      </div>
      <button class="admin-ghost-btn" type="button" @click="$emit('refresh')">刷新</button>
    </div>

    <div v-if="error" class="admin-state is-error">{{ error }}</div>
    <div v-else-if="loading" class="admin-state">账户列表加载中...</div>
    <div v-else class="admin-table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>角色</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>会话令牌</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="admin-user-cell">
                <strong>{{ user.username }}</strong>
                <span class="admin-user-id">#{{ user.id }}</span>
              </div>
            </td>
            <td><span :class="['admin-badge', user.role === 'admin' ? 'is-admin' : 'is-user']">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span></td>
            <td><span :class="['admin-badge', user.is_active ? 'is-active' : 'is-inactive']">{{ user.is_active ? '启用中' : '已停用' }}</span></td>
            <td>{{ formatTime(user.last_login_at) }}</td>
            <td>{{ user.active_refresh_tokens || 0 }}</td>
            <td>{{ formatTime(user.created_at) }}</td>
            <td>
              <div class="admin-row-actions">
                <button class="admin-action-btn" type="button" title="编辑账户" @click="$emit('edit', user)">编辑</button>
                <button class="admin-action-btn" type="button" title="重置密码" @click="$emit('reset-password', user)">重置</button>
                <button
                  :class="['admin-action-btn', user.is_active ? 'is-danger' : 'is-success']"
                  :title="user.is_active ? '停用账号' : '启用账号'"
                  type="button"
                  @click="$emit('toggle-active', user)"
                >
                  {{ user.is_active ? '停用' : '启用' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!users.length">
            <td colspan="7" class="admin-empty-cell">暂无账户数据</td>
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
defineProps({
  users: { type: Array, default: () => [] },
  filters: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  size: { type: Number, default: 12 },
})

defineEmits(['create', 'edit', 'reset-password', 'toggle-active', 'refresh', 'change-page', 'update:filters'])

function formatTime(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('zh-CN')
}
</script>
