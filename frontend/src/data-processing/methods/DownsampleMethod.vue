<template>
  <div>
    <div class="dp-tip-banner">
      数据降采样会按固定规则减少样本数量，同时尽量保留原始数据的关键趋势和模式，常用于时序信号或高频数据压缩。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：1 个及以上定量变量。输出：减少样本后的变量。若最后一组样本数量不足降采样因子 N，则该组会被直接剔除。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>降采样方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.downsampleMode" value="direct" /> 直接采样（固定间隔采样）</label>
      <label><input type="radio" v-model="options.downsampleMode" value="dilution" /> 稀释采样</label>
    </div>

    <div class="dp-form-row" style="margin-top: 14px;">
      <label>降采样因子 N</label>
      <input class="dp-input" type="number" v-model.number="options.downsampleFactor" min="1" step="1" placeholder="10" />
    </div>

    <div v-if="options.downsampleMode === 'direct'" class="dp-form-row">
      <label>采样位置</label>
      <input class="dp-input" type="number" v-model.number="options.downsamplePosition" min="1" step="1" :max="Math.max(options.downsampleFactor || 1, 1)" placeholder="1" />
    </div>

    <div v-else class="dp-form-row">
      <label>稀释方法</label>
      <select class="dp-select" v-model="options.downsampleAggregate">
        <option value="mean">平均值</option>
        <option value="median">中位数</option>
        <option value="min">最小值</option>
        <option value="max">最大值</option>
        <option value="sum">求和</option>
      </select>
    </div>

    <div class="dp-config-hint">
      <template v-if="options.downsampleMode === 'direct'">
        直接采样会把数据按每 N 个样本分成一组，并取每组中指定位置的值作为结果。
      </template>
      <template v-else>
        稀释采样会把数据按每 N 个样本分组，再对每组计算平均值、中位数、最小值、最大值或求和。
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
