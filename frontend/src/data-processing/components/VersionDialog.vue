<template>
  <div class="dp-version-drawer-shell" @click.self="$emit('close')">
    <aside class="dp-version-drawer">
      <div class="dp-version-drawer-head">
        <div>
          <h3>版本记录</h3>
          <p>当前版本 v{{ currentVersionNo || '-' }}</p>
        </div>
        <button class="dp-version-drawer-close" @click="$emit('close')">&times;</button>
      </div>

      <div class="dp-version-drawer-body">
        <div v-if="loading" class="dp-version-empty">正在加载版本记录...</div>
        <div v-else-if="!versions.length" class="dp-version-empty">当前还没有可切换的历史版本。</div>
        <div v-else class="dp-version-list">
          <div v-for="version in versions" :key="version.id" class="dp-version-item">
            <div class="dp-version-main">
              <div class="dp-version-title">
                <span>v{{ version.version_no }}</span>
                <span v-if="version.is_current" class="dp-version-current">当前版本</span>
              </div>
              <div class="dp-version-meta">
                <span>{{ formatTime(version.created_at) }}</span>
                <span v-if="version.source_job_id">来源任务 {{ version.source_job_id }}</span>
              </div>
            </div>
            <button
              class="dp-version-switch"
              :disabled="version.is_current || switchingId === version.id"
              @click="$emit('switch-version', version)"
            >
              {{ switchingId === version.id ? '切换中' : (version.is_current ? '使用中' : '切换') }}
            </button>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
defineProps({
  currentVersionNo: { type: [String, Number], default: '' },
  loading: { type: Boolean, default: false },
  versions: { type: Array, default: () => [] },
  switchingId: { type: [String, Number, null], default: null },
  formatTime: { type: Function, required: true },
})

defineEmits(['close', 'switch-version'])
</script>
