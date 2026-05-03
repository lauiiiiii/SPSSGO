<template>
  <div>
    <div class="dp-tip-banner">
      当分类任务中因变量各类别样本数量差异过大时，会明显影响模型训练。样本均衡通过过采样、欠采样或组合采样，使各类别样本数量更接近。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：至少 1 个无空值变量，并选择 1 个定类目标变量。输出：增加样本量较少的类别样本，或减少样本量较多的类别样本。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>选择目标变量</span>
    </div>
    <div class="dp-form-row">
      <label>目标变量（分类变量）</label>
      <select class="dp-select" v-model="options.balanceTarget">
        <option value="">请选择</option>
        <option v-for="v in catVars" :key="v.name" :value="v.name">{{ v.name }}</option>
      </select>
    </div>

    <div class="dp-config-step" style="margin-top:16px">
      <span class="dp-step-num">2</span>
      <span>均衡方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.balanceMethod" value="oversample" /> 过采样（增加少数类样本）</label>
      <label><input type="radio" v-model="options.balanceMethod" value="undersample" /> 欠采样（减少多数类样本）</label>
      <label><input type="radio" v-model="options.balanceMethod" value="mixed" /> 组合采样（同时调整多数类与少数类）</label>
    </div>

    <div class="dp-config-hint">
      <template v-if="options.balanceMethod === 'oversample'">
        过采样会增加样本量较少的类别，使其尽量与样本量最多的类别接近。
      </template>
      <template v-else-if="options.balanceMethod === 'undersample'">
        欠采样会减少样本量较多的类别，使其尽量与样本量最少的类别接近。
      </template>
      <template v-else>
        组合采样会同时减少多数类样本，并增加少数类样本，使各类别样本数量向中间水平靠拢。
      </template>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：样本均衡不支持对存在空值的变量进行处理，需要提前处理空值。
    </div>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Object, required: true },
  catVars: { type: Array, default: () => [] },
})
</script>
