<template>
  <div>
    <div class="dp-tip-banner">
      数据标准化包括去量纲化和一致化。去量纲化用于消除不同指标的量纲差异，一致化用于统一正向、负向和特殊指标的作用方向。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：一项或以上定量变量。输出：新生成标准化后的变量。若指标中既有正向指标又有负向指标，通常建议分别使用正向指标处理和负向指标处理。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>标准化方式</span>
    </div>
    <select class="dp-select" v-model="options.stdMethod">
      <option value="minmax">Min-Max 标准化</option>
      <option value="zscore">Z-score 标准化</option>
      <option value="sum">归一化（总和归一化）</option>
      <option value="center">中心化</option>
      <option value="mean">均值化</option>
      <option value="interval">区间化</option>
      <option value="initial">初值化</option>
      <option value="min_value">最小值化</option>
      <option value="max_value">最大值化</option>
      <option value="positive">正向指标处理</option>
      <option value="negative">负向指标处理</option>
      <option value="middle">中间型指标处理</option>
      <option value="range">区间型指标处理</option>
    </select>

    <div class="dp-config-hint">
      <template v-if="options.stdMethod === 'minmax'">
        Min-Max 标准化将数据线性压缩到 [0,1] 区间，适合希望保留原始分布和范围信息的场景。
      </template>
      <template v-else-if="options.stdMethod === 'zscore'">
        Z-score 标准化将数据转换为均值约为 0、标准差约为 1 的形式，适用于回归、聚类等常见分析场景。
      </template>
      <template v-else-if="options.stdMethod === 'sum'">
        归一化采用总和归一化方法，转换后数据与整体总和形成相对比例关系。
      </template>
      <template v-else-if="options.stdMethod === 'center'">
        中心化将每个值减去均值，使数据围绕 0 分布，便于比较相对偏差。
      </template>
      <template v-else-if="options.stdMethod === 'mean'">
        均值化将每个值转换为其相对均值的比例，以减少量纲差异。
      </template>
      <template v-else-if="options.stdMethod === 'interval'">
        区间化会将数据线性映射到你指定的区间 [a,b] 内。
      </template>
      <template v-else-if="options.stdMethod === 'initial'">
        初值化将各值相对于序列中的第一个非零元素进行归一化。
      </template>
      <template v-else-if="options.stdMethod === 'min_value'">
        最小值化会用每个值除以当前列最小值。
      </template>
      <template v-else-if="options.stdMethod === 'max_value'">
        最大值化会用每个值除以当前列最大值。
      </template>
      <template v-else-if="options.stdMethod === 'positive'">
        正向指标处理适用于数值越大越好的指标，处理后结果落在 [0,1] 区间，原值越大越接近 1。
      </template>
      <template v-else-if="options.stdMethod === 'negative'">
        负向指标处理适用于数值越小越好的指标，处理后结果落在 [0,1] 区间，原值越小越接近 1。
      </template>
      <template v-else-if="options.stdMethod === 'middle'">
        中间型指标处理适用于存在理想值的情况，越接近理想值，处理结果越接近 1。
      </template>
      <template v-else>
        区间型指标处理适用于存在理想区间 [a,b] 的情况，落在区间内记为 1，偏离区间越远结果越小。
      </template>
    </div>

    <div v-if="options.stdMethod === 'interval'" class="dp-inline-form" style="margin-top: 14px;">
      <span>目标区间：</span>
      <input class="dp-input dp-input-sm" v-model.number="options.stdIntervalMin" placeholder="a" style="width:96px" />
      <span>~</span>
      <input class="dp-input dp-input-sm" v-model.number="options.stdIntervalMax" placeholder="b" style="width:96px" />
    </div>

    <div v-if="options.stdMethod === 'middle'" class="dp-form-row" style="margin-top: 14px;">
      <label>理想值</label>
      <input class="dp-input" v-model.number="options.stdBestValue" placeholder="请输入理想值" />
    </div>

    <div v-if="options.stdMethod === 'range'" class="dp-inline-form" style="margin-top: 14px;">
      <span>理想区间：</span>
      <input class="dp-input dp-input-sm" v-model.number="options.stdRangeMin" placeholder="a" style="width:96px" />
      <span>~</span>
      <input class="dp-input dp-input-sm" v-model.number="options.stdRangeMax" placeholder="b" style="width:96px" />
    </div>

    <div class="dp-config-step" style="margin-top: 16px;">
      <span class="dp-step-num">2</span>
      <span>输出格式</span>
    </div>
    <div class="dp-toggle-row">
      <span>生成新变量</span>
      <label class="dp-toggle">
        <input type="checkbox" v-model="options.stdNewVar" />
        <span class="dp-toggle-slider"></span>
      </label>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：数据标准化不支持对存在空值的变量进行处理，需要提前处理空值。若选择“生成新变量”，系统会保留原始变量并新增标准化结果列。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
