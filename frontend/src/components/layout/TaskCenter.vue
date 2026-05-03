<template>
  <transition name="tc-fade">
    <aside v-if="open" class="tc-panel">
      <div class="tc-head">
        <div>
          <div class="tc-title">任务中心</div>
          <div class="tc-subtitle">当前会话的异步任务状态</div>
        </div>
        <div class="tc-head-actions">
          <button v-if="hasCompleted" class="tc-link" @click="$emit('clear-completed')">清除已完成</button>
          <button class="tc-close" @click="$emit('close')">&times;</button>
        </div>
      </div>

      <div v-if="sortedJobs.length" class="tc-list">
        <TaskCenterItem
          v-for="job in sortedJobs"
          :key="job.id"
          :job="job"
          @cancel-job="$emit('cancel-job', $event)"
          @retry-job="$emit('retry-job', $event)"
        />
      </div>

      <div v-else class="tc-empty">
        <div class="tc-empty-title">暂无任务</div>
        <div class="tc-empty-text">上传、处理、分析或导出后，任务会出现在这里。</div>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import TaskCenterItem from '../task-center/TaskCenterItem.vue'
import { sortTaskJobs, TERMINAL_JOB_STATUSES } from '../../utils/taskDisplay.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  jobs: { type: Array, default: () => [] },
})

defineEmits(['close', 'clear-completed', 'cancel-job', 'retry-job'])

const sortedJobs = computed(() => sortTaskJobs(props.jobs))
const hasCompleted = computed(() => sortedJobs.value.some(job => TERMINAL_JOB_STATUSES.has(job.status)))
</script>

<style scoped>
.tc-panel {
  position: fixed;
  top: 76px;
  right: 18px;
  z-index: 40;
  width: 336px;
  max-height: calc(100vh - 96px);
  overflow: auto;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(12px);
}

.tc-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.tc-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.tc-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.tc-head-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tc-link,
.tc-close {
  border: 0;
  background: transparent;
  color: #475569;
  cursor: pointer;
}

.tc-link {
  font-size: 12px;
}

.tc-close {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  font-size: 20px;
  line-height: 1;
}

.tc-close:hover {
  background: rgba(148, 163, 184, 0.14);
}

.tc-list {
  padding: 12px;
}

.tc-item {
  padding: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 14px;
  background: #fff;
}

.tc-item + .tc-item {
  margin-top: 10px;
}

.tc-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tc-item-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.tc-status {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.tc-status.is-queued,
.tc-status.is-pending,
.tc-status.is-retrying {
  background: #fff7ed;
  color: #c2410c;
}

.tc-status.is-running {
  background: #eff6ff;
  color: #2563eb;
}

.tc-status.is-succeeded {
  background: #ecfdf5;
  color: #059669;
}

.tc-status.is-failed,
.tc-status.is-canceled {
  background: #fef2f2;
  color: #dc2626;
}

.tc-message {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #334155;
}

.tc-progress {
  height: 6px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.tc-progress-bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6, #0ea5e9);
}

.tc-error {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  color: #dc2626;
}

.tc-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
  font-size: 12px;
  color: #94a3b8;
}

.tc-empty {
  padding: 28px 20px 32px;
  text-align: center;
}

.tc-empty-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.tc-empty-text {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: #64748b;
}

.tc-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.tc-action {
  min-width: 84px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.tc-action:hover:not(:disabled) {
  background: #dbeafe;
}

.tc-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tc-action--danger {
  border-color: rgba(220, 38, 38, 0.16);
  background: #fef2f2;
  color: #dc2626;
}

.tc-action--danger:hover:not(:disabled) {
  background: #fee2e2;
}

.tc-fade-enter-active,
.tc-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.tc-fade-enter-from,
.tc-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
