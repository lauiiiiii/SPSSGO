<template>
  <section class="admin-panel">
    <div class="admin-panel__head">
      <div>
        <div class="admin-panel__eyebrow">Overview</div>
        <h2>全局概览</h2>
      </div>
      <button class="admin-ghost-btn" type="button" @click="$emit('refresh')">刷新</button>
    </div>

    <div v-if="loading" class="admin-state">概览加载中...</div>
    <div v-else-if="error" class="admin-state is-error">{{ error }}</div>
    <template v-else>
      <div class="admin-stat-grid admin-stat-grid--4">
        <AdminStatCard label="总会话数" :value="dashboard.total_sessions || 0" hint="历史累计" />
        <AdminStatCard label="已完成分析" :value="dashboard.done_sessions || 0" tone="success" hint="已进入完成态" />
        <AdminStatCard label="进行中会话" :value="dashboard.active_sessions || 0" tone="warn" hint="当前执行态" />
        <AdminStatCard label="分析结果总数" :value="dashboard.total_results || 0" hint="结果表累计" />
      </div>

      <div class="admin-dual-grid">
        <section class="admin-block">
          <div class="admin-block__title">存储占用</div>
          <div class="admin-kv-list">
            <div class="admin-kv-row"><span>上传文件</span><strong>{{ dashboard.storage?.uploads_mb || 0 }} MB</strong></div>
            <div class="admin-kv-row"><span>输出报告</span><strong>{{ dashboard.storage?.outputs_mb || 0 }} MB</strong></div>
          </div>
        </section>
        <section class="admin-block">
          <div class="admin-block__title">近 7 日会话趋势</div>
          <div v-if="!dashboard.daily_sessions?.length" class="admin-state">暂无趋势数据</div>
          <div v-else class="admin-trend">
            <div v-for="item in dashboard.daily_sessions" :key="item.date" class="admin-trend__item">
              <div class="admin-trend__bar-wrap">
                <div class="admin-trend__bar" :style="{ height: `${trendHeight(item.count)}px` }"></div>
              </div>
              <span class="admin-trend__count">{{ item.count }}</span>
              <span class="admin-trend__label">{{ item.date?.slice(5) }}</span>
            </div>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup>
import AdminStatCard from './AdminStatCard.vue'

const props = defineProps({
  dashboard: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['refresh'])

function trendHeight(count) {
  const max = Math.max(...((props.dashboard.daily_sessions || []).map(item => item.count)), 1)
  return Math.max(8, Math.round((count / max) * 92))
}
</script>
