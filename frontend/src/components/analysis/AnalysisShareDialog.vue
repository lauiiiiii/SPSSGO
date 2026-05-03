<!-- 这里只放分析报告分享弹窗，别把工作台状态和报告渲染逻辑塞进来。 -->
<template>
  <div class="ap-share-mask" @click.self="$emit('close')">
    <div class="ap-share-dialog">
      <div class="ap-share-head">
        <div>
          <div class="ap-share-title">分享分析结果</div>
          <div class="ap-share-subtitle">生成一段分享文案，直接发给别人就行。</div>
        </div>
        <button type="button" class="ap-share-close" @click="$emit('close')">&times;</button>
      </div>

      <div class="ap-share-body">
        <div class="ap-share-form-item">
          <div class="ap-share-form-row">
            <div class="ap-share-field-label ap-share-field-label--inline">有效期</div>
            <div class="ap-share-row-main">
              <div class="ap-share-expiry-tabs">
                <button
                  v-for="item in expiryOptions"
                  :key="item.value"
                  type="button"
                  class="ap-share-expiry-tab"
                  :class="{ active: expiryDays === item.value }"
                  :disabled="loading"
                  @click="$emit('update:expiryDays', item.value)"
                >
                  {{ item.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="ap-share-form-item">
          <div class="ap-share-form-row">
            <div class="ap-share-field-label ap-share-field-label--inline">查阅口令</div>
            <div class="ap-share-row-main">
              <div class="ap-share-code-row">
                <input
                  class="ap-share-input"
                  :value="password"
                  :disabled="loading"
                  type="text"
                  maxlength="64"
                  placeholder="不填则任何人拿到链接都可访问"
                  @input="$emit('update:password', $event.target.value)"
                />
                <button
                  type="button"
                  class="ap-share-mini-btn"
                  :disabled="loading"
                  @click="$emit('fill-random-password')"
                >
                  随机生成
                </button>
              </div>
            </div>
          </div>
          <div class="ap-share-field-hint ap-share-field-hint--offset">设置后，访问者打开链接前要先输入查阅口令。</div>
        </div>

        <div class="ap-share-field-label">分享文案</div>
        <div class="ap-share-linkbox" :class="{ 'is-loading': loading, 'is-error': error }">
          <span v-if="loading">正在生成分享链接...</span>
          <span v-else-if="error">{{ error }}</span>
          <span v-else-if="shareText">{{ shareText }}</span>
          <span v-else>请先设置有效期，查阅口令可选，然后生成分享链接。</span>
        </div>
        <div class="ap-share-field-hint">删除这个报告、重新生成链接或链接到期后，原链接会自动失效。</div>
      </div>

      <div class="ap-share-actions">
        <button type="button" class="ap-share-btn ap-share-btn--ghost" @click="$emit('close')">取消</button>
        <button
          type="button"
          class="ap-share-btn ap-share-btn--primary"
          :disabled="loading"
          @click="$emit('generate')"
        >
          {{ shareUrl ? '重新生成链接' : '生成分享链接' }}
        </button>
        <button
          v-if="shareText"
          type="button"
          class="ap-share-btn ap-share-btn--ghost"
          :disabled="loading || !shareText"
          @click="$emit('copy')"
        >
          {{ copied ? '已复制文案' : '复制分享文案' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const expiryOptions = [
  { value: 1, label: '1天' },
  { value: 3, label: '3天' },
  { value: 7, label: '7天' },
  { value: 30, label: '30天' },
]

defineProps({
  copied: { type: Boolean, default: false },
  expiryDays: { type: Number, default: 7 },
  error: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  password: { type: String, default: '' },
  shareText: { type: String, default: '' },
  shareUrl: { type: String, default: '' },
})

defineEmits(['close', 'copy', 'fill-random-password', 'generate', 'update:expiryDays', 'update:password'])
</script>
