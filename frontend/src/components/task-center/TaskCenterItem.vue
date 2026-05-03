<template>
  <article class="tc-item" :class="`is-${job.status}`">
    <div class="tc-item-top">
      <div class="tc-item-title">{{ jobLabel(job) }}</div>
      <span class="tc-status" :class="`is-${job.status}`">{{ statusLabel(job.status) }}</span>
    </div>
    <div class="tc-message">{{ progressMessage(job) }}</div>
    <div v-if="progressPercent(job) > 0 && progressPercent(job) < 100" class="tc-progress">
      <div class="tc-progress-bar" :style="{ width: `${progressPercent(job)}%` }"></div>
    </div>
    <div v-if="job.error_message" class="tc-error">{{ job.error_message }}</div>
    <div class="tc-meta">
      <span>{{ queueLabel(job.queue) }}</span>
      <span>{{ formatJobTime(job.created_at) }}</span>
    </div>
    <div v-if="canCancelJob(job) || canRetryJob(job)" class="tc-actions">
      <button
        v-if="canCancelJob(job)"
        class="tc-action tc-action--danger"
        :disabled="job.action_pending"
        @click="$emit('cancel-job', job)"
      >
        {{ job.action_pending && job.action_type === 'cancel' ? '取消中...' : '取消任务' }}
      </button>
      <button
        v-if="canRetryJob(job)"
        class="tc-action"
        :disabled="job.action_pending"
        @click="$emit('retry-job', job)"
      >
        {{ job.action_pending && job.action_type === 'retry' ? '重试中...' : '重新执行' }}
      </button>
    </div>
  </article>
</template>

<script setup>
import {
  canCancelJob,
  canRetryJob,
  formatJobTime,
  jobLabel,
  progressMessage,
  progressPercent,
  queueLabel,
  statusLabel,
} from '../../utils/taskDisplay.js'

defineProps({
  job: { type: Object, required: true },
})

defineEmits(['cancel-job', 'retry-job'])
</script>
