<template>
  <div>
    <div class="card">
      <h2>研究信息</h2>
      <div class="form-group">
        <label>研究主题</label>
        <input v-model="form.research_topic" placeholder="如：自我效能感、社会支持对大学生就业焦虑的影响" />
      </div>
      <div class="form-group">
        <label>变量说明</label>
        <textarea
          v-model="form.variable_desc"
          placeholder="如：社会支持是第6-15题，自我效能感16-25题，就业焦虑26-45题；q1=性别(1男2女)，q2=年级(1-4)"
        ></textarea>
        <div class="hint">告诉 AI 哪些列是什么变量，编码含义是什么</div>
      </div>
      <div class="form-group">
        <label>研究假设</label>
        <textarea
          v-model="form.hypotheses"
          placeholder="如：H1: 就业焦虑在性别、年级上存在显著差异&#10;H2: 自我效能感与就业焦虑呈显著负相关&#10;H3: 社会支持与就业焦虑呈显著负相关"
        ></textarea>
      </div>
      <div class="form-group">
        <label>需要的分析（可选）</label>
        <textarea
          v-model="form.analysis_request"
          placeholder="如：描述统计、独立样本t检验、方差分析、皮尔逊相关、多元回归&#10;不填则由 AI 根据假设自动决定"
        ></textarea>
        <div class="hint">不填的话 AI 会根据研究假设自动选择分析方法</div>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-outline" @click="$emit('back')">&#8592; 上一步</button>
      <button class="btn btn-primary" :disabled="loading" @click="$emit('submit')">
        {{ loading ? '正在生成分析计划...' : '生成分析计划 →' }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  form: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})
defineEmits(['back', 'submit'])
</script>
