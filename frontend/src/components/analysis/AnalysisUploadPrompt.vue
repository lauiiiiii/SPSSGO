<template>
  <div class="ap-upload-prompt">
    <div class="ap-upload-empty-title">暂无数据</div>
    <div class="ap-upload-actions">
      <button class="viz-primary-btn" type="button" @click="$emit('upload')">上传数据文件</button>
      <button class="viz-secondary-btn" type="button" @click="$emit('go-mydata')">去我的数据选择</button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['upload', 'go-mydata'])
</script>
