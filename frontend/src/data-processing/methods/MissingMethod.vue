<template>
  <div>
    <div class="dp-tip-banner">
      缺失值即空值。缺失值处理支持剔除标记和填充两大类方式，可按行列阈值剔除，也可使用统计量、规则、插值或模型方法进行填补。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：一项或以上定量或定类变量。输出：对缺失值进行剔除、标记或填补后的结果。多列填补时各列独立处理，互不影响。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>处理大类</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.missingAction" value="drop_mark" /> 剔除标记</label>
      <label><input type="radio" v-model="options.missingAction" value="fill" /> 填充</label>
    </div>

    <template v-if="options.missingAction === 'drop_mark'">
      <div class="dp-config-step" style="margin-top: 16px;">
        <span class="dp-step-num">2</span>
        <span>剔除标记规则</span>
      </div>
      <div class="dp-radio-group">
        <label><input type="radio" v-model="options.missingDropMode" value="row_ratio" /> 按行缺失比例剔除</label>
        <label><input type="radio" v-model="options.missingDropMode" value="row_count" /> 按行缺失个数剔除</label>
        <label><input type="radio" v-model="options.missingDropMode" value="col_ratio" /> 按列缺失比例剔除</label>
        <label><input type="radio" v-model="options.missingDropMode" value="col_count" /> 按列缺失个数剔除</label>
      </div>

      <div class="dp-form-row" style="margin-top: 14px;">
        <label>{{ thresholdLabel }}</label>
        <input
          v-if="needsRatioThreshold"
          class="dp-input"
          type="number"
          v-model.number="options.missingDropThreshold"
          min="0"
          max="100"
          step="1"
          placeholder="50"
        />
        <input
          v-else
          class="dp-input"
          type="number"
          v-model.number="options.missingDropThreshold"
          min="1"
          step="1"
          placeholder="1"
        />
      </div>

      <div class="dp-radio-group">
        <label><input type="radio" v-model="options.missingDropAction" value="delete" /> 直接剔除</label>
        <label><input type="radio" v-model="options.missingDropAction" value="mark" /> 生成标记变量</label>
      </div>

      <div class="dp-config-hint">
        达到设定阈值的整行或整列会被识别为需要剔除。若选择标记，系统会新增标记列，`1` 表示保留，`0` 表示命中剔除条件。
      </div>
    </template>

    <template v-else>
      <div class="dp-config-step" style="margin-top: 16px;">
        <span class="dp-step-num">2</span>
        <span>填充类型</span>
      </div>
      <select class="dp-select" v-model="options.missingFillCategory">
        <option value="stat">统计量填充</option>
        <option value="rule">规则填充</option>
        <option value="interpolate">插值填充</option>
        <option value="model">模型填充</option>
      </select>

      <div class="dp-config-step" style="margin-top: 16px;">
        <span class="dp-step-num">3</span>
        <span>填充方法</span>
      </div>

      <div v-if="options.missingFillCategory === 'stat'" class="dp-radio-group">
        <label><input type="radio" v-model="options.missingFill" value="mean" /> 均值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="median" /> 中位数填充</label>
        <label><input type="radio" v-model="options.missingFill" value="mode" /> 众数填充</label>
        <label><input type="radio" v-model="options.missingFill" value="plus_3sigma" /> 三倍标准差填充</label>
        <label><input type="radio" v-model="options.missingFill" value="minus_3sigma" /> 负三倍标准差填充</label>
      </div>

      <div v-else-if="options.missingFillCategory === 'rule'" class="dp-radio-group">
        <label><input type="radio" v-model="options.missingFill" value="ffill" /> 纵向用上方值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="bfill" /> 纵向用下方值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="drop_all_missing_row" /> 若某行全为缺失值则剔除该行</label>
        <label><input type="radio" v-model="options.missingFill" value="custom" /> 固定值 M 填充</label>
      </div>

      <div v-else-if="options.missingFillCategory === 'interpolate'" class="dp-radio-group">
        <label><input type="radio" v-model="options.missingFill" value="nearest" /> Nearest 最近点数值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="zero" /> Zero 零阶插值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="linear" /> Linear 线性插值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="quadratic" /> quadratic 二次插值填充</label>
        <label><input type="radio" v-model="options.missingFill" value="cubic" /> cubic 三次插值填充</label>
      </div>

      <div v-else class="dp-radio-group">
        <label><input type="radio" v-model="options.missingFill" value="least_squares" /> 最小二乘填充</label>
        <label><input type="radio" v-model="options.missingFill" value="bayesian" /> 贝叶斯填充</label>
        <label><input type="radio" v-model="options.missingFill" value="decision_tree" /> 决策树填充</label>
        <label><input type="radio" v-model="options.missingFill" value="knn" /> k 近邻填充</label>
      </div>

      <input
        v-if="options.missingFill === 'custom'"
        class="dp-input"
        v-model="options.missingCustomVal"
        placeholder="请输入固定值 M"
        style="margin-top: 14px;"
      />

      <div v-if="options.missingFill === 'knn'" class="dp-form-row" style="margin-top: 14px;">
        <label>k 值</label>
        <input class="dp-input" type="number" v-model.number="options.missingKnnK" min="1" step="1" placeholder="5" />
      </div>

      <div class="dp-config-hint">
        <template v-if="options.missingFillCategory === 'stat'">
          统计量填充会按列独立计算填充值。定类变量只建议使用众数填充；定量变量可使用均值、中位数、众数、正负三倍标准差。
        </template>
        <template v-else-if="options.missingFillCategory === 'rule'">
          规则填充适合有顺序的数据。前向和后向填充会沿列方向寻找最近的非缺失值；固定值 M 填充适合规则明确的业务场景。
        </template>
        <template v-else-if="options.missingFillCategory === 'interpolate'">
          插值填充适用于连续型或有序数据。为了保证插值有效，通常建议用于定量变量。
        </template>
        <template v-else>
          模型填充会基于现有数据建立预测模型，再对缺失值进行估计。适合更复杂的数据模式，但计算开销更高。
        </template>
      </div>
    </template>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：定类变量与定量变量的缺失值处理应分开看待。定类变量的统计填充通常只适合众数；定量变量才适合均值、中位数、三倍标准差等统计量填充。
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({ options: { type: Object, required: true } })

const needsRatioThreshold = computed(() => ['row_ratio', 'col_ratio'].includes(props.options.missingDropMode))
const thresholdLabel = computed(() => (needsRatioThreshold.value ? '阈值（%）' : '阈值（个数）'))

watch(() => props.options.missingFillCategory, (category) => {
  const defaultMap = {
    stat: 'mean',
    rule: 'ffill',
    interpolate: 'linear',
    model: 'knn',
  }
  props.options.missingFill = defaultMap[category] || 'mean'
}, { immediate: true })
</script>
