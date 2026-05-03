<template>
  <div class="upload-overlay" @click.self="$emit('close')">
    <div class="upload-modal">
      <div class="upload-modal-head">
        <span>上传数据</span>
        <button class="upload-modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div
        class="upload-drop-zone"
        :class="{ 'upload-drop-zone--hover': dragHover }"
        @dragover.prevent="$emit('update:dragHover', true)"
        @dragleave="$emit('update:dragHover', false)"
        @drop.prevent="$emit('drop-file', $event)"
        @click="$emit('choose-file')"
      >
        <div class="upload-drop-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <path d="M12 16V4M8 8l4-4 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 16v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="upload-drop-btn">上传文件</div>
        <div class="upload-drop-hint">支持拖拽文件上传，或点击选择文件</div>
      </div>
      <div class="upload-formats">
        <div class="upload-formats-text">支持 xlsx / xls / csv / sav / dta / sas7bdat / xpt / tsv / txt / json / parquet</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  dragHover: { type: Boolean, default: false },
})

defineEmits(['choose-file', 'close', 'drop-file', 'update:dragHover'])
</script>
