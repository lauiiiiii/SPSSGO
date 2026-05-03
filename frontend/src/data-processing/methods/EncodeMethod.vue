<template>
  <div>
    <div class="dp-tip-banner">
      将变量数值再次进行编码，可进一步浓缩或整合原始数据。处理后可按分组替换原始数据，也可生成新变量并补充分组标签。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：一项定量变量或定类变量。输出：对该变量每个值进行重新编码。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>选择编码方式</span>
    </div>
    <div class="dp-radio-group dp-radio-group--inline">
      <label><input type="radio" v-model="options.encodeMode" value="new" /> 新编码</label>
      <label><input type="radio" v-model="options.encodeMode" value="range" /> 范围编码 <span class="dp-dialog-help" title="按数值范围分组编码">?</span></label>
      <label><input type="radio" v-model="options.encodeMode" value="auto" /> 自动分组</label>
    </div>

    <div class="dp-config-hint" style="margin-top: 8px;">
      <template v-if="options.encodeMode === 'new'">
        新编码适合逐值重编码。若原始数据为文本类型，系统通常会先按列顺序生成默认编码，您也可以在此手动指定新的编码和标签。
      </template>
      <template v-else-if="options.encodeMode === 'range'">
        范围编码适合连续数值变量。您可以按照数值区间重新分组，编码范围不允许重复。
      </template>
      <template v-else>
        自动分组适合快速将数值按均值或分位数切分成 2 组、3 组或 4 组。
      </template>
    </div>

    <div v-if="selectedCount && encodeSourceValues.length" class="dp-encode-panel">
      <template v-if="options.encodeMode === 'new'">
        <div class="dp-encode-head dp-encode-grid dp-encode-grid--new">
          <span>原始值</span>
          <span>编码</span>
          <span>标签（选填）</span>
        </div>
        <div
          v-for="(row, idx) in options.encodeRows"
          :key="`${idx}-${row.source}`"
          class="dp-encode-row dp-encode-grid dp-encode-grid--new"
        >
          <input class="dp-input dp-input-sm" :value="row.source" disabled />
          <input class="dp-input dp-input-sm" v-model="options.encodeRows[idx].code" placeholder="编码值" />
          <input class="dp-input dp-input-sm" v-model="options.encodeRows[idx].label" placeholder="标签" />
        </div>
        <div class="dp-config-hint">
          适用于反向题、文本转数字、选项合并等场景。例如 5 级量表正向编码为 5/4/3/2/1 时，可将反向题重新编码为 1/2/3/4/5。
        </div>
        <div class="dp-config-hint">
          不填写标签时只对原始值进行编码；定量变量填写标签后，将更适合作为定类变量使用。
        </div>
      </template>

      <template v-else-if="options.encodeMode === 'range'">
        <div class="dp-encode-head dp-encode-grid dp-encode-grid--range">
          <span>最小值</span>
          <span>最大值</span>
          <span>编码</span>
          <span>标签（选填）</span>
        </div>
        <div v-for="(row, idx) in options.encodeRanges" :key="idx" class="dp-encode-row dp-encode-grid dp-encode-grid--range">
          <input class="dp-input dp-input-sm" v-model="row.min" placeholder="最小值" />
          <input class="dp-input dp-input-sm" v-model="row.max" placeholder="最大值" />
          <input class="dp-input dp-input-sm" v-model="row.code" placeholder="编码值" />
          <div class="dp-encode-range-actions">
            <input class="dp-input dp-input-sm" v-model="row.label" placeholder="标签" />
            <button class="dp-link-btn" @click="methodActions.removeRange?.(idx)" :disabled="options.encodeRanges.length <= 1">删除</button>
          </div>
        </div>
        <button class="dp-link-btn" @click="methodActions.addRange?.()">+ 添加范围</button>
        <div class="dp-config-hint">
          例如原本为 5 级量表时，可将 1-2 编码为 1，3 编码为 2，4-5 编码为 3，以整合成三级结果。
        </div>
      </template>

      <template v-else>
        <div class="dp-form-row">
          <label>分组方式</label>
          <select class="dp-input" v-model="options.encodeAutoStrategy">
            <option value="mean_2">均值 2 组</option>
            <option value="median_2">二分位数 2 组</option>
            <option value="quantile_27_73">27% / 73% 分位数 3 组</option>
            <option value="quartile_4">四分位数 4 组</option>
          </select>
        </div>
        <div class="dp-config-hint">
          <template v-if="options.encodeAutoStrategy === 'mean_2'">
            将数值按平均值切分，低于平均值为一组，高于或等于平均值为一组。
          </template>
          <template v-else-if="options.encodeAutoStrategy === 'median_2'">
            将数值按从小到大排序后，以 50% 分位数切分成两组。
          </template>
          <template v-else-if="options.encodeAutoStrategy === 'quantile_27_73'">
            将数值按 27%、27%-73%、73%-100% 划分为三组，适合区分低、中、高水平。
          </template>
          <template v-else>
            将数值按 25%、50%、75% 分位点划分为四组。
          </template>
        </div>
        <div class="dp-config-hint">
          当前样本量 {{ encodeMeta.sampleSize || 0 }}。样本较少时建议优先使用 2 组或 3 组，避免分组过细带来偶然波动。
        </div>
      </template>
    </div>
    <div v-else class="dp-config-hint">{{ encodeHintText }}</div>

    <div class="dp-config-step" style="margin-top:16px">
      <span class="dp-step-num">2</span>
      <span>输出格式</span>
    </div>
    <div class="dp-toggle-row">
      <span>生成新变量</span>
      <label class="dp-toggle">
        <input type="checkbox" v-model="options.encodeNewVar" />
        <span class="dp-toggle-slider"></span>
      </label>
      <span class="dp-dialog-help" title="若关闭此选项，则数据处理结果将覆盖原数据">?</span>
    </div>
    <input v-if="options.encodeNewVar" class="dp-input" v-model="options.encodeNewVarName" placeholder="新变量名称" />

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：范围编码和自动分组依赖数值信息。对于定量变量，会直接按原始数值分组；对于分类变量，则会基于其已有编码值进行分组。
    </div>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Object, required: true },
  selectedCount: { type: Number, default: 0 },
  encodeSourceValues: { type: Array, default: () => [] },
  encodeMeta: { type: Object, required: true },
  encodeHintText: { type: String, default: '' },
  methodActions: { type: Object, default: () => ({}) },
})
</script>
