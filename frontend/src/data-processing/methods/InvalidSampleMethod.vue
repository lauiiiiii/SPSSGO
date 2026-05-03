<template>
  <div>
    <div class="dp-tip-banner">
      无效样本处理用于对整行样本进行识别与管理，帮助排除重复、无效个案，使整体分析数据更符合研究预期。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：两项或以上的定量或定类变量。输出：对满足条件的样本进行删除，或生成标记变量进行标记。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>无效样本识别规则</span>
    </div>
    <div class="dp-check-group">
      <label>
        <input type="checkbox" v-model="options.invalidSameDigit" />
        相同数据出现
        <input class="dp-input dp-input-xs" v-model.number="options.invalidSameDigitPct" style="width:56px" />
        % 及以上（按行识别）
      </label>
      <label>
        <input type="checkbox" v-model="options.invalidMissing" />
        缺失比例出现
        <input class="dp-input dp-input-xs" v-model.number="options.invalidMissingPct" style="width:56px" />
        % 及以上（按行识别）
      </label>
    </div>

    <div class="dp-config-hint">
      一般在问卷回答中，若同一行在多个题目上都出现大量相同回答，可能说明样本存在乱填情况；若同一行缺失值过多，也通常会被视为无效样本。
    </div>

    <div class="dp-config-step" style="margin-top:16px">
      <span class="dp-step-num">2</span>
      <span>处理方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.invalidAction" value="delete" /> 删除无效样本</label>
      <label><input type="radio" v-model="options.invalidAction" value="mark" /> 标记无效样本（首列生成标记变量，1 有效 / 0 无效）</label>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：若进行“相同数据出现 XX% 及以上”的识别，对于定类变量，本质上识别的是相同编码出现的比例，因此通常不建议直接对定类变量使用这一规则。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
