<template>
  <div>
    <div class="dp-tip-banner">
      样本量足够大时，为了减少极端值对研究结果的影响，可以对连续变量进行缩尾或截尾处理。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：一项或以上定量变量。输出：对极端值进行缩尾（替换）或截尾（置空 / 删除所在行）处理。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>处理方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.winsorizeMode" value="winsorize" /> 缩尾（用分位数替换极端值）</label>
      <label><input type="radio" v-model="options.winsorizeMode" value="trim" /> 截尾</label>
    </div>

    <div v-if="options.winsorizeMode === 'trim'" class="dp-radio-group dp-radio-indent">
      <label><input type="radio" v-model="options.winsorizeTrimAction" value="null" /> 仅将极端值置空</label>
      <label><input type="radio" v-model="options.winsorizeTrimAction" value="row_delete" /> 删除极端值所在整行样本</label>
    </div>

    <div class="dp-config-hint">
      <template v-if="options.winsorizeMode === 'winsorize'">
        例如设置 5% ~ 95%，则低于 5% 分位数的值将被替换为 5% 分位数，高于 95% 分位数的值将被替换为 95% 分位数。
      </template>
      <template v-else-if="options.winsorizeTrimAction === 'null'">
        截尾后，超出指定百分位范围的极端值会被置为空值。
      </template>
      <template v-else>
        截尾后，只要某行在任一选中变量中出现极端值，该整行样本都会被删除。
      </template>
    </div>

    <div class="dp-config-step" style="margin-top:16px">
      <span class="dp-step-num">2</span>
      <span>百分位范围</span>
    </div>
    <div class="dp-inline-form">
      <span>处理不在</span>
      <input class="dp-input dp-input-sm" v-model.number="options.winsorizePercent" style="width:64px" />
      <span>% ~ {{ 100 - Number(options.winsorizePercent || 0) }}% 范围内的数据</span>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：缩尾/截尾处理不支持对存在空值的变量进行处理，需要提前处理空值。多列处理中各列独立识别极端值。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
