<template>
  <div class="viz-workbench">
    <aside class="viz-chart-nav">
      <div class="mn-header">
        <input v-model="chartTypeQuery" class="mn-search" placeholder="搜索图形类型..." />
      </div>
      <div class="mn-list">
        <div class="mn-category">
          <div class="mn-cat-header" @click="chartGroupExpanded = !chartGroupExpanded">
            <svg class="mn-cat-arrow" :class="{ open: chartGroupExpanded }" viewBox="0 0 16 16" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>基础图形</span>
          </div>
          <div class="mn-items" v-show="chartGroupExpanded">
            <div class="viz-chart-type-grid">
              <button
                v-for="item in filteredChartTypes"
                :key="item.value"
                type="button"
                class="viz-chart-type"
                :class="{ active: chartType === item.value }"
                @click="chartType = item.value"
              >
                {{ item.label }}
              </button>
            </div>
            <div v-if="!filteredChartTypes.length" class="hp-empty" style="padding:16px 8px">
              未找到匹配的图形
            </div>
          </div>
        </div>
      </div>
    </aside>

    <VariablePanel
      :variables="variables"
      :total-rows="totalRows"
      :selected-vars="selectedVars"
      :used-vars="usedVars"
      @select="$emit('select-variable', $event)"
      @deselect="$emit('deselect-variable', $event)"
      @select-range="$emit('select-range', $event)"
      @drag-start="$emit('drag-start', $event)"
      @drag-end="$emit('drag-end')"
    />

    <main class="viz-canvas-panel">
      <div class="viz-canvas-head">
        <div>
          <div class="viz-title">可视化绘图</div>
          <div class="viz-subtitle">{{ hasData ? `当前数据 ${totalRows} 行，拖入变量生成图表` : '上传数据后开始绘图' }}</div>
        </div>
        <button v-if="!hasData" class="viz-primary-btn" type="button" @click="$emit('upload')">上传数据</button>
      </div>

      <div class="viz-canvas">
        <div v-if="!hasData" class="viz-empty">
          <div class="viz-empty-title">暂无数据</div>
          <div class="viz-empty-actions">
            <button class="viz-primary-btn" type="button" @click="$emit('upload')">上传数据文件</button>
            <button class="viz-secondary-btn" type="button" @click="$emit('go-mydata')">去我的数据选择</button>
          </div>
        </div>
        <div v-else-if="errorMessage" class="viz-empty viz-empty--error">
          <div class="viz-empty-title">{{ errorMessage }}</div>
          <div class="viz-empty-hint">调整变量或图形类型后会自动重新生成。</div>
        </div>
        <div v-else-if="loading" class="viz-empty">
          <span class="spinner-sm"></span>
          <div class="viz-empty-title">正在生成图表...</div>
        </div>
        <div v-else-if="chart" class="viz-chart-stage">
          <AnalysisChartItem
            :calc-box="calcBox"
            :calc-grouped-box="calcGroupedBox"
            :calc-category-bar="calcCategoryBar"
            :calc-category-pie="calcCategoryPie"
            :calc-correspondence-map="calcCorrespondenceMap"
            :calc-crosstab="calcCrosstab"
            :calc-factor-heatmap="calcFactorHeatmap"
            :calc-hist="calcHist"
            :calc-metric-comparison="calcMetricComparison"
            :calc-normality-hist="calcNormalityHist"
            :calc-probability-plot="calcProbabilityPlot"
            :calc-scatter-plot="calcScatterPlot"
            :chart="chart"
            :chart-index="0"
            :data-visible="!!chartDataVisible['0_0']"
            :fmt-bin="fmtBin"
            :section-index="0"
            :set-chart-ref="setChartRef"
            @hide-tip="hideTip"
            @move-tip="moveTip"
            @show-hist-tip="showHistTip"
            @show-box-tip="showBoxTip"
            @show-category-tip="showCategoryTip"
            @show-crosstab-tip="showCrosstabTip"
            @show-probability-tip="showProbabilityTip"
            @show-metric-tip="showMetricTip"
            @show-scatter-tip="showScatterTip"
            @download-chart="downloadChart"
            @copy-chart="copyChart"
            @toggle-chart-data="toggleChartData"
          />
          <div v-if="warnings.length" class="viz-warning-list">
            <span v-for="warning in warnings" :key="warning">{{ warning }}</span>
          </div>
        </div>
        <div v-else class="viz-empty">
          <div class="viz-empty-title">拖入变量生成图表</div>
          <div class="viz-empty-hint">也可以在右侧变量槽中手动选择变量。</div>
        </div>
      </div>
    </main>

    <aside class="viz-config-panel">
      <div class="viz-config-section">
        <div class="viz-config-title">变量</div>
        <label v-if="needsX" class="viz-field">
          <span>{{ xLabel }}</span>
          <select v-model="slotValues.x">
            <option value="">请选择</option>
            <option v-for="variable in xCandidates" :key="variable.name" :value="variable.name">{{ variable.name }}</option>
          </select>
        </label>
        <label v-if="needsY" class="viz-field">
          <span>变量Y</span>
          <select v-model="slotValues.y">
            <option value="">请选择</option>
            <option v-for="variable in numericVariables" :key="variable.name" :value="variable.name">{{ variable.name }}</option>
          </select>
        </label>
        <label v-if="needsGroup" class="viz-field">
          <span>分组变量</span>
          <select v-model="slotValues.group">
            <option value="">请选择</option>
            <option v-for="variable in categoryVariables" :key="variable.name" :value="variable.name">{{ variable.name }}</option>
          </select>
        </label>
        <div class="viz-drop-zone" @dragover.prevent @drop.prevent="onDropVariables">
          将变量拖到这里
        </div>
      </div>

      <div class="viz-config-section">
        <div class="viz-config-title">参数</div>
        <label class="viz-field">
          <span>标题</span>
          <input v-model="options.title" placeholder="默认自动生成" />
        </label>
        <label v-if="chartType === 'histogram'" class="viz-field">
          <span>分箱数</span>
          <input v-model.number="options.bins" type="number" min="3" max="60" placeholder="自动" />
        </label>
        <label v-if="supportsSort" class="viz-field">
          <span>排序</span>
          <select v-model="options.sort">
            <option value="count_desc">按数值降序</option>
            <option value="original">原始顺序</option>
          </select>
        </label>
        <label class="viz-check">
          <input v-model="options.show_labels" type="checkbox" />
          <span>显示数值</span>
        </label>
        <button class="viz-primary-btn viz-full-btn" type="button" :disabled="!canPreview || loading" @click="loadPreview">生成图表</button>
      </div>
    </aside>

    <AnalysisChartTooltip :tip="tip" />
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import * as api from '../../api.js'
import { useAnalysisCharts } from '../../composables/analysis/useAnalysisCharts.js'
import AnalysisChartItem from '../analysis/AnalysisChartItem.vue'
import AnalysisChartTooltip from '../analysis/AnalysisChartTooltip.vue'
import VariablePanel from '../variable/VariablePanel.vue'

const props = defineProps({
  dataFileName: { type: String, default: '' },
  hasData: { type: Boolean, default: false },
  selectedVars: { type: Array, default: () => [] },
  sessionId: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variables: { type: Array, default: () => [] },
})

defineEmits(['deselect-variable', 'drag-end', 'drag-start', 'go-mydata', 'select-range', 'select-variable', 'upload'])

const chartTypes = [
  { value: 'bar', label: '柱状图' },
  { value: 'horizontal_bar', label: '条形图' },
  { value: 'pie', label: '饼图' },
  { value: 'donut', label: '环形图' },
  { value: 'histogram', label: '直方图' },
  { value: 'boxplot', label: '箱线图' },
  { value: 'scatter', label: '散点图' },
  { value: 'line', label: '折线图' },
  { value: 'grouped_bar', label: '分组柱状图' },
  { value: 'grouped_boxplot', label: '分组箱线图' },
]

const categoryTypes = new Set(['bar', 'horizontal_bar', 'pie', 'donut'])
const numericTypes = new Set(['histogram', 'boxplot'])
const xyTypes = new Set(['scatter', 'line'])
const groupedTypes = new Set(['grouped_bar', 'grouped_boxplot'])

const chartType = ref('bar')
const chartTypeQuery = ref('')
const chartGroupExpanded = ref(true)
const slotValues = reactive({ x: '', y: '', group: '' })
const options = reactive({ title: '', bins: '', sort: 'count_desc', show_labels: true })
const chart = ref(null)
const warnings = ref([])
const errorMessage = ref('')
const loading = ref(false)

const {
  calcBox,
  calcGroupedBox,
  calcCategoryBar,
  calcCategoryPie,
  calcCorrespondenceMap,
  calcCrosstab,
  calcFactorHeatmap,
  calcHist,
  calcMetricComparison,
  calcNormalityHist,
  calcProbabilityPlot,
  calcScatterPlot,
  chartDataVisible,
  copyChart,
  downloadChart,
  fmtBin,
  hideTip,
  moveTip,
  setChartRef,
  showBoxTip,
  showCategoryTip,
  showCrosstabTip,
  showHistTip,
  showMetricTip,
  showProbabilityTip,
  showScatterTip,
  tip,
  toggleChartData,
} = useAnalysisCharts()

const usedVars = computed(() => new Set([slotValues.x, slotValues.y, slotValues.group].filter(Boolean)))
const numericVariables = computed(() => props.variables.filter(variable => variable.type === 'numeric'))
const categoryVariables = computed(() => props.variables.filter(variable => variable.type !== 'numeric'))
const filteredChartTypes = computed(() => {
  const query = chartTypeQuery.value.trim().toLowerCase()
  if (!query) return chartTypes
  return chartTypes.filter(item => item.label.toLowerCase().includes(query) || item.value.toLowerCase().includes(query))
})
const needsX = computed(() => categoryTypes.has(chartType.value) || numericTypes.has(chartType.value) || xyTypes.has(chartType.value))
const needsY = computed(() => xyTypes.has(chartType.value) || groupedTypes.has(chartType.value))
const needsGroup = computed(() => groupedTypes.has(chartType.value))
const xLabel = computed(() => categoryTypes.has(chartType.value) ? '分类变量' : '变量X')
const xCandidates = computed(() => (categoryTypes.has(chartType.value) ? categoryVariables.value : numericVariables.value))
const supportsSort = computed(() => categoryTypes.has(chartType.value) || chartType.value === 'grouped_bar')
const canPreview = computed(() => {
  if (!props.hasData || !props.sessionId) return false
  if (needsX.value && !slotValues.x) return false
  if (needsY.value && !slotValues.y) return false
  if (needsGroup.value && !slotValues.group) return false
  return true
})

watch(() => props.selectedVars, (names) => {
  if (Array.isArray(names) && names.length) assignVariables(names)
}, { deep: true })

watch(chartType, () => {
  resetSlotsForType()
  if (props.selectedVars.length) assignVariables(props.selectedVars)
})

watch([() => slotValues.x, () => slotValues.y, () => slotValues.group, () => options.bins, () => options.sort, () => options.show_labels], () => {
  if (canPreview.value) loadPreview()
})

watch(() => options.title, () => {
  if (canPreview.value) loadPreview()
})

function variableByName(name) {
  return props.variables.find(variable => variable.name === name)
}

function assignVariables(names) {
  const list = names.map(variableByName).filter(Boolean)
  const numeric = list.filter(variable => variable.type === 'numeric')
  const category = list.filter(variable => variable.type !== 'numeric')
  if (category.length && numeric.length) {
    chartType.value = groupedTypes.has(chartType.value) ? chartType.value : 'grouped_bar'
    slotValues.group = category[0].name
    slotValues.y = numeric[0].name
    return
  }
  if (numeric.length >= 2) {
    chartType.value = xyTypes.has(chartType.value) ? chartType.value : 'scatter'
    slotValues.x = numeric[0].name
    slotValues.y = numeric[1].name
    return
  }
  if (category.length) {
    chartType.value = categoryTypes.has(chartType.value) ? chartType.value : 'bar'
    slotValues.x = category[0].name
    return
  }
  if (numeric.length) {
    chartType.value = numericTypes.has(chartType.value) ? chartType.value : 'histogram'
    slotValues.x = numeric[0].name
  }
}

function resetSlotsForType() {
  chart.value = null
  warnings.value = []
  errorMessage.value = ''
  if (categoryTypes.has(chartType.value) && slotValues.x && variableByName(slotValues.x)?.type === 'numeric') slotValues.x = ''
  if ((numericTypes.has(chartType.value) || xyTypes.has(chartType.value)) && slotValues.x && variableByName(slotValues.x)?.type !== 'numeric') slotValues.x = ''
}

function onDropVariables(event) {
  const names = String(event.dataTransfer?.getData('text/plain') || '')
    .split(',')
    .map(name => name.trim())
    .filter(Boolean)
  if (names.length) assignVariables(names)
}

async function loadPreview() {
  if (!canPreview.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await api.previewVisualization(props.sessionId, {
      chart_type: chartType.value,
      variables: {
        x: slotValues.x || null,
        y: slotValues.y || null,
        group: slotValues.group || null,
      },
      options: {
        title: options.title || '',
        bins: options.bins || '',
        sort: options.sort,
        show_labels: options.show_labels,
      },
    })
    chart.value = result.chart
    warnings.value = result.warnings || []
  } catch (error) {
    chart.value = null
    warnings.value = []
    errorMessage.value = error.message || '图表生成失败'
  } finally {
    loading.value = false
  }
}
</script>
