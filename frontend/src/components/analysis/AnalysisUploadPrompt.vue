<template>
  <div class="ap-upload-prompt">
    <div class="ap-upload-card" @click="$emit('upload')">
      <div class="ap-upload-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="currentColor" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="currentColor" stroke-width="1" opacity=".5"/></svg>
      </div>
      <div class="ap-upload-text">
        <div class="ap-upload-title">上传数据文件</div>
        <div class="ap-upload-hint">支持 Excel / CSV / SPSS / Stata / SAS / Parquet 等格式</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['upload'])
</script>
