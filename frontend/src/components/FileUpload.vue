<template>
  <div>
    <UploadDropCard
      accept=".xlsx,.xls,.csv,.sav,.zsav,.dta,.sas7bdat,.xpt,.tsv,.txt,.json,.parquet"
      :drag-enabled="true"
      :file="dataFile"
      icon="&#128202;"
      title="上传数据文件"
      hint="点击或拖拽上传数据文件（Excel / CSV / SPSS / Stata / SAS 等）"
      @select="$emit('upload-data', $event)"
      @clear="$emit('clear-data')"
    />

    <UploadDropCard
      accept=".docx,.doc"
      :file="questFile"
      :padded="true"
      icon="&#128221;"
      title="上传问卷（可选）"
      hint="点击上传 Word 问卷文件，AI 可以读取题目内容辅助分析"
      @select="$emit('upload-quest', $event)"
      @clear="$emit('clear-quest')"
    />

    <div class="card" v-if="dataSummary" style="display: flex; align-items: center; gap: 12px; padding: 20px 30px">
      <span style="font-size: 20px">&#9989;</span>
      <span style="font-size: 15px; color: #2d3748">
        数据已解析：<b>{{ dataSummary.total_rows }}</b> 行 &times; <b>{{ dataSummary.total_cols }}</b> 列
      </span>
    </div>

    <div class="btn-group" v-if="dataSummary">
      <button class="btn btn-primary" @click="$emit('next')">下一步：填写研究信息 &rarr;</button>
    </div>
  </div>
</template>

<script setup>
import UploadDropCard from './upload/UploadDropCard.vue'

defineProps({
  dataFile: Object,
  questFile: Object,
  dataSummary: Object,
})

defineEmits(['upload-data', 'upload-quest', 'clear-data', 'clear-quest', 'next'])
</script>
