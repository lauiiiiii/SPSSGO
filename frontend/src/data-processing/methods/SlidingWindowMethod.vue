<template>
  <div>
    <div class="dp-tip-banner">
      时序数据滑窗转换用于把单序列数据转换为监督学习数据。简单来说，就是用前若干期数据 X1~XN 去预测当前期 Y。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：1 项定量变量。输出：根据步阶划分得到的自变量 X1~XN 和因变量 Y。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>步阶设置</span>
    </div>
    <div class="dp-form-row">
      <label>步阶</label>
      <input class="dp-input" type="number" v-model.number="options.windowSize" min="1" placeholder="7" />
    </div>

    <div class="dp-config-hint">
      例如步阶为 7，表示用前 7 个时点的数据作为 X1~X7，去预测当前时点的 Y。若是日度销量数据，步阶为 7 往往可对应一个周周期。
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：时序数据滑窗转换不支持对存在空值的变量进行处理。转换后前若干行会因为凑不够前序窗口而为空，在机器学习建模前不要直接对这些空行做数据填补；如需处理，建议进行整行删除。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
