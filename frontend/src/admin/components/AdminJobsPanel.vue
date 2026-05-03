<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Operations</div>
        <h2>作业监控</h2>
      </div>
      <button class="admin-ghost-btn" type="button" @click="$emit('refresh')">刷新</button>
    </div>

    <div class="admin-stat-grid admin-stat-grid--3">
      <AdminStatCard label="24 小时新建作业" :value="operationsSummary.jobs_last_24h || 0" />
      <AdminStatCard label="24 小时 Sandbox 失败" :value="operationsSummary.sandbox_failures_last_24h || 0" tone="danger" />
      <AdminStatCard label="运行中 Sandbox" :value="operationsSummary.sandbox_status_counts?.running || 0" tone="warn" />
    </div>

    <div class="admin-dual-grid">
      <section class="admin-block">
        <div class="admin-block__title">队列负载</div>
        <div v-if="!queueChips.length" class="admin-state">暂无队列数据</div>
        <div v-else class="admin-chip-grid">
          <div v-for="chip in queueChips" :key="chip.key" class="admin-chip">
            <span>{{ queueLabel(chip.key) }}</span>
            <strong>{{ chip.count }}</strong>
          </div>
        </div>
      </section>
      <section class="admin-block">
        <div class="admin-block__title">Sandbox 模式</div>
        <div v-if="!sandboxModeChips.length" class="admin-state">暂无模式数据</div>
        <div v-else class="admin-chip-grid">
          <div v-for="chip in sandboxModeChips" :key="chip.key" class="admin-chip">
            <span>{{ sandboxModeLabel(chip.key) }}</span>
            <strong>{{ chip.count }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="admin-subsection">
      <div class="admin-subsection__head">
        <h3>最近作业</h3>
        <div class="admin-toolbar__filters">
          <select :value="jobFilters.status" @change="$emit('update:job-filters', { ...jobFilters, status: $event.target.value })">
            <option value="">全部状态</option>
            <option v-for="status in jobStatuses" :key="status" :value="status">{{ jobStatusLabel(status) }}</option>
          </select>
          <select :value="jobFilters.queue" @change="$emit('update:job-filters', { ...jobFilters, queue: $event.target.value })">
            <option value="">全部队列</option>
            <option v-for="queue in queues" :key="queue" :value="queue">{{ queueLabel(queue) }}</option>
          </select>
          <select :value="jobFilters.job_type" @change="$emit('update:job-filters', { ...jobFilters, job_type: $event.target.value })">
            <option value="">全部作业类型</option>
            <option v-for="type in jobTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
        </div>
      </div>

      <div v-if="jobsError" class="admin-state is-error">{{ jobsError }}</div>
      <div v-else-if="jobsLoading" class="admin-state">作业列表加载中...</div>
      <div v-else class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>作业 ID</th>
              <th>类型</th>
              <th>队列</th>
              <th>状态</th>
              <th>所属用户</th>
              <th>创建时间</th>
              <th>错误</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in jobs" :key="job.id">
              <td class="admin-mono">{{ job.id }}</td>
              <td>{{ jobTypeLabel(job.job_type) }}</td>
              <td>{{ queueLabel(job.queue_name) }}</td>
              <td><span :class="['admin-badge', `is-status-${job.status}`]">{{ jobStatusLabel(job.status) }}</span></td>
              <td>{{ job.owner_username || '—' }}</td>
              <td>{{ formatTime(job.created_at) }}</td>
              <td class="admin-table__truncate" :title="job.error_message || ''">{{ shortText(job.error_message) }}</td>
            </tr>
            <tr v-if="!jobs.length">
              <td colspan="7" class="admin-empty-cell">暂无作业数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="jobTotal > jobSize" class="admin-pagination">
        <button class="admin-ghost-btn" type="button" :disabled="jobPage <= 1" @click="$emit('change-job-page', jobPage - 1)">上一页</button>
        <span>第 {{ jobPage }} / {{ Math.ceil(jobTotal / jobSize) }} 页</span>
        <button class="admin-ghost-btn" type="button" :disabled="jobPage >= Math.ceil(jobTotal / jobSize)" @click="$emit('change-job-page', jobPage + 1)">下一页</button>
      </div>
    </div>

    <div class="admin-subsection">
      <div class="admin-subsection__head">
        <h3>Sandbox 审计</h3>
        <div class="admin-toolbar__filters">
          <select :value="sandboxFilters.status" @change="$emit('update:sandbox-filters', { ...sandboxFilters, status: $event.target.value })">
            <option value="">全部状态</option>
            <option v-for="status in sandboxStatuses" :key="status" :value="status">{{ jobStatusLabel(status) }}</option>
          </select>
          <select :value="sandboxFilters.executor_mode" @change="$emit('update:sandbox-filters', { ...sandboxFilters, executor_mode: $event.target.value })">
            <option value="">全部模式</option>
            <option value="docker">Docker</option>
            <option value="local">本地</option>
            <option value="unknown">未知</option>
          </select>
        </div>
      </div>

      <div v-if="sandboxError" class="admin-state is-error">{{ sandboxError }}</div>
      <div v-else-if="sandboxLoading" class="admin-state">Sandbox 审计加载中...</div>
      <div v-else class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>执行 ID</th>
              <th>作业类型</th>
              <th>模式</th>
              <th>状态</th>
              <th>所属用户</th>
              <th>创建时间</th>
              <th>退出码</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sandboxExecutions" :key="item.execution_id">
              <td class="admin-mono">{{ item.execution_id }}</td>
              <td>{{ jobTypeLabel(item.job_type) }}</td>
              <td>{{ sandboxModeLabel(item.executor_mode) }}</td>
              <td><span :class="['admin-badge', `is-status-${item.status}`]">{{ jobStatusLabel(item.status) }}</span></td>
              <td>{{ item.owner_username || '—' }}</td>
              <td>{{ formatTime(item.created_at) }}</td>
              <td>{{ item.exit_code ?? '—' }}</td>
            </tr>
            <tr v-if="!sandboxExecutions.length">
              <td colspan="7" class="admin-empty-cell">暂无 sandbox 审计数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="sandboxTotal > sandboxSize" class="admin-pagination">
        <button class="admin-ghost-btn" type="button" :disabled="sandboxPage <= 1" @click="$emit('change-sandbox-page', sandboxPage - 1)">上一页</button>
        <span>第 {{ sandboxPage }} / {{ Math.ceil(sandboxTotal / sandboxSize) }} 页</span>
        <button class="admin-ghost-btn" type="button" :disabled="sandboxPage >= Math.ceil(sandboxTotal / sandboxSize)" @click="$emit('change-sandbox-page', sandboxPage + 1)">下一页</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import AdminStatCard from './AdminStatCard.vue'

defineProps({
  operationsSummary: { type: Object, default: () => ({}) },
  queueChips: { type: Array, default: () => [] },
  sandboxModeChips: { type: Array, default: () => [] },
  jobFilters: { type: Object, required: true },
  jobs: { type: Array, default: () => [] },
  jobsLoading: { type: Boolean, default: false },
  jobsError: { type: String, default: '' },
  jobPage: { type: Number, default: 1 },
  jobSize: { type: Number, default: 12 },
  jobTotal: { type: Number, default: 0 },
  sandboxFilters: { type: Object, required: true },
  sandboxExecutions: { type: Array, default: () => [] },
  sandboxLoading: { type: Boolean, default: false },
  sandboxError: { type: String, default: '' },
  sandboxPage: { type: Number, default: 1 },
  sandboxSize: { type: Number, default: 12 },
  sandboxTotal: { type: Number, default: 0 },
})

defineEmits([
  'refresh',
  'update:job-filters',
  'update:sandbox-filters',
  'change-job-page',
  'change-sandbox-page',
])

const jobStatuses = ['pending', 'queued', 'running', 'retrying', 'succeeded', 'failed', 'canceled']
const sandboxStatuses = ['pending', 'queued', 'running', 'retrying', 'succeeded', 'failed', 'canceled']
const queues = ['ingest', 'process', 'analysis', 'report', 'ai', 'sandbox']
const jobTypes = [
  { value: 'upload_ingest', label: '上传解析' },
  { value: 'process_data', label: '数据处理' },
  { value: 'execute_method', label: '单方法分析' },
  { value: 'execute_plan', label: '整套分析' },
  { value: 'generate_report', label: '报告生成' },
  { value: 'ai_plan', label: 'AI 规划' },
  { value: 'ai_interpret', label: 'AI 解读' },
]

function queueLabel(value) {
  return {
    ingest: '解析队列',
    process: '处理队列',
    analysis: '分析队列',
    report: '报告队列',
    ai: 'AI 队列',
    sandbox: 'Sandbox 队列',
  }[value] || value || '—'
}

function sandboxModeLabel(value) {
  if (value === 'docker') return 'Docker'
  if (value === 'local') return '本地'
  return value || '未知'
}

function jobTypeLabel(value) {
  return (jobTypes.find(item => item.value === value) || {}).label || value || '—'
}

function jobStatusLabel(value) {
  return {
    pending: '待处理',
    queued: '排队中',
    running: '运行中',
    retrying: '重试中',
    succeeded: '已完成',
    failed: '失败',
    canceled: '已取消',
  }[value] || value || '—'
}

function formatTime(ts) {
  if (!ts) return '—'
  return new Date(ts * 1000).toLocaleString('zh-CN')
}

function shortText(text) {
  const value = String(text || '').trim()
  if (!value) return '—'
  return value.length > 48 ? `${value.slice(0, 48)}...` : value
}
</script>
