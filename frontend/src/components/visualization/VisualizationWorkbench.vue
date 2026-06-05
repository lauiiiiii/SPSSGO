<template>
  <div class="viz-workbench">
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
      <div v-if="historyItems.length > 0" class="viz-canvas-head">
        <div class="viz-canvas-head-main">
          <div class="viz-history-strip" :class="{ expanded: historyExpanded }">
            <div class="viz-history-chip-wrap" :class="{ expanded: historyExpanded }">
              <div
                v-for="(item, idx) in historyItems"
                :key="item.id || idx"
                class="viz-history-chip-item"
                @mouseenter="hoveredHistoryIdx = idx"
                @mouseleave="onLeaveHistoryChip(idx)"
              >
                <button
                  class="viz-history-chip"
                  :class="{ active: idx === activeHistoryIndex }"
                  :title="item.name || '可视化记录'"
                  type="button"
                  @click="selectHistory(idx)"
                  @contextmenu.prevent="openHistoryMenu(idx, $event)"
                >
                  <span class="viz-history-serial">N{{ historyItems.length - idx }}</span>
                  <span class="viz-history-text">{{ item.name }}</span>
                </button>
                <button
                  class="viz-history-delete"
                  type="button"
                  title="删除记录"
                  @click.stop="deleteHistoryAt(idx)"
                >×</button>
              </div>
            </div>
            <button
              v-if="historyItems.length > 8"
              class="viz-history-expand"
              type="button"
              :title="historyExpanded ? '收起记录' : '展开记录'"
              @click="historyExpanded = !historyExpanded"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  :d="historyExpanded ? 'M4 10l4-4 4 4' : 'M4 6l4 4 4-4'"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </button>
          </div>
        </div>
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
            :key="chartRenderKey"
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
        <div class="viz-config-title-row">
          <div class="viz-config-title">变量</div>
          <button v-if="assignedSlotChips.length" class="viz-reset-slots" type="button" @click="clearAllSlots">重新设置</button>
        </div>
        <div class="viz-drop-zone" @dragover.prevent @drop.prevent="onDropVariables">
          <template v-if="assignedSlotChips.length">
            <span v-for="chip in assignedSlotChips" :key="chip.key" class="viz-slot-chip">
              {{ chip.name }}
              <button type="button" title="移除变量" @mousedown.prevent.stop @click.prevent.stop="clearSlot(chip.key)">×</button>
            </span>
          </template>
          <span v-else>将变量拖到这里，或从左侧选择变量</span>
        </div>
      </div>

      <div class="viz-config-section">
        <div class="viz-config-title">智能图表推荐</div>
        <div class="viz-chart-preview-grid viz-chart-preview-grid--recommended">
          <button
            v-for="item in recommendedChartTypes"
            :key="item.value"
            type="button"
            class="viz-chart-preview"
            :class="{ active: chartType === item.value }"
            @click="selectChartType(item.value)"
          >
            <span class="viz-mini-chart" :class="`viz-mini-chart--${item.value}`">
              <i></i><i></i><i></i><i></i>
            </span>
            <span>{{ item.label }}</span>
          </button>
        </div>
        <div v-if="!recommendedChartTypes.length" class="viz-config-empty">
          先选择变量，系统会按变量类型推荐图表。
        </div>
      </div>

      <div class="viz-config-section">
        <div class="viz-config-title">全部图表类型</div>
        <div class="viz-chart-preview-grid">
          <button
            v-for="item in chartTypes"
            :key="item.value"
            type="button"
            class="viz-chart-preview"
            :class="{ active: chartType === item.value }"
            :disabled="!chartTypeUsable(item.value)"
            @click="selectChartType(item.value)"
          >
            <span class="viz-mini-chart" :class="`viz-mini-chart--${item.value}`">
              <i></i><i></i><i></i><i></i>
            </span>
            <span>{{ item.label }}</span>
          </button>
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
        <button class="viz-secondary-btn viz-full-btn" type="button" :disabled="(!chart && !canPreview) || loading || saving" @click="saveCurrentVisualization">
          {{ saving ? '保存中...' : '保存记录' }}
        </button>
      </div>
    </aside>

    <div v-if="historyMenuIdx >= 0" class="viz-history-menu" :style="historyMenuStyle">
      <button type="button" @click="renameHistory">重命名</button>
      <button type="button" class="danger" @click="deleteHistory">删除</button>
    </div>

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
  activeResult: { type: Object, default: null },
  activeHistoryIndex: { type: Number, default: -1 },
  hasData: { type: Boolean, default: false },
  historyItems: { type: Array, default: () => [] },
  selectedVars: { type: Array, default: () => [] },
  sessionId: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits(['delete-history', 'deselect-variable', 'drag-end', 'drag-start', 'go-mydata', 'history-saved', 'rename-history', 'select-history', 'select-range', 'select-variable', 'upload'])

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
const slotValues = reactive({ x: '', y: '', group: '' })
const options = reactive({ title: '', bins: '', sort: 'count_desc', show_labels: true })
const chart = ref(null)
const warnings = ref([])
const errorMessage = ref('')
const loading = ref(false)
const saving = ref(false)
const chartRenderKey = ref(0)
const hoveredHistoryIdx = ref(-1)
const historyExpanded = ref(false)
const historyMenuIdx = ref(-1)
const historyMenuStyle = reactive({ left: '0px', top: '0px' })

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
const needsX = computed(() => categoryTypes.has(chartType.value) || numericTypes.has(chartType.value) || xyTypes.has(chartType.value))
const needsY = computed(() => xyTypes.has(chartType.value) || groupedTypes.has(chartType.value))
const needsGroup = computed(() => groupedTypes.has(chartType.value))
const xLabel = computed(() => categoryTypes.has(chartType.value) ? '分类变量' : '变量X')
const xCandidates = computed(() => (categoryTypes.has(chartType.value) ? categoryVariables.value : numericVariables.value))
const supportsSort = computed(() => categoryTypes.has(chartType.value) || chartType.value === 'grouped_bar')
const assignedSlotChips = computed(() => [
  { key: 'group', name: slotValues.group },
  { key: 'x', name: slotValues.x },
  { key: 'y', name: slotValues.y },
].filter(item => item.name))
const selectedVariableTypes = computed(() => {
  const values = [slotValues.x, slotValues.y, slotValues.group]
    .map(variableByName)
    .filter(Boolean)
  return {
    hasCategory: values.some(variable => variable.type !== 'numeric'),
    numericCount: values.filter(variable => variable.type === 'numeric').length,
  }
})
const recommendedChartTypes = computed(() => {
  const { hasCategory, numericCount } = selectedVariableTypes.value
  if (hasCategory && numericCount) return chartTypes.filter(item => ['grouped_bar', 'grouped_boxplot'].includes(item.value))
  if (numericCount >= 2) return chartTypes.filter(item => ['scatter', 'line'].includes(item.value))
  if (numericCount === 1) return chartTypes.filter(item => ['histogram', 'boxplot'].includes(item.value))
  if (hasCategory) return chartTypes.filter(item => ['bar', 'horizontal_bar', 'pie', 'donut'].includes(item.value))
  return []
})
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

watch(() => props.activeResult, (result) => {
  const savedChart = extractSavedChart(result)
  if (!savedChart) {
    if (result) {
      chart.value = null
      warnings.value = []
      errorMessage.value = '这条绘图记录缺少图表数据，请删除后重新保存。'
    }
    return
  }
  chart.value = savedChart
  warnings.value = result?.description ? String(result.description).split('\n').filter(Boolean) : []
  errorMessage.value = ''
  chartRenderKey.value += 1
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
  slotValues.x = ''
  slotValues.y = ''
  slotValues.group = ''
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

function chartTypeUsable(type) {
  const { hasCategory, numericCount } = selectedVariableTypes.value
  if (groupedTypes.has(type)) return hasCategory && numericCount >= 1
  if (xyTypes.has(type)) return numericCount >= 2
  if (numericTypes.has(type)) return numericCount >= 1
  if (categoryTypes.has(type)) return hasCategory
  return false
}

function selectChartType(type) {
  if (!chartTypeUsable(type) && props.hasData) return
  chartType.value = type
}

function resetSlotsForType() {
  chart.value = null
  warnings.value = []
  errorMessage.value = ''
  chartRenderKey.value += 1
  if (categoryTypes.has(chartType.value) && slotValues.x && variableByName(slotValues.x)?.type === 'numeric') slotValues.x = ''
  if ((numericTypes.has(chartType.value) || xyTypes.has(chartType.value)) && slotValues.x && variableByName(slotValues.x)?.type !== 'numeric') slotValues.x = ''
}

function clearSlot(key) {
  const removedName = slotValues[key]
  slotValues[key] = ''
  chart.value = null
  warnings.value = []
  errorMessage.value = ''
  chartRenderKey.value += 1
  if (removedName) emit('deselect-variable', removedName)
}

function clearAllSlots() {
  const removedNames = Array.from(new Set([slotValues.x, slotValues.y, slotValues.group].filter(Boolean)))
  slotValues.x = ''
  slotValues.y = ''
  slotValues.group = ''
  chart.value = null
  warnings.value = []
  errorMessage.value = ''
  chartRenderKey.value += 1
  removedNames.forEach(name => emit('deselect-variable', name))
}

function onDropVariables(event) {
  const names = String(event.dataTransfer?.getData('text/plain') || '')
    .split(',')
    .map(name => name.trim())
    .filter(Boolean)
  if (names.length) assignVariables(names)
}

function selectHistory(idx) {
  historyMenuIdx.value = -1
  historyExpanded.value = false
  emit('select-history', idx)
}

function onLeaveHistoryChip(idx) {
  if (historyMenuIdx.value !== idx) hoveredHistoryIdx.value = -1
}

function openHistoryMenu(idx, event) {
  historyMenuIdx.value = idx
  hoveredHistoryIdx.value = idx
  historyMenuStyle.left = `${event.clientX}px`
  historyMenuStyle.top = `${event.clientY}px`
}

function toggleHistoryMenu(idx, event) {
  if (historyMenuIdx.value === idx) {
    historyMenuIdx.value = -1
    return
  }
  const rect = event.currentTarget.getBoundingClientRect()
  historyMenuIdx.value = idx
  hoveredHistoryIdx.value = idx
  historyMenuStyle.left = `${rect.left}px`
  historyMenuStyle.top = `${rect.bottom + 6}px`
}

function renameHistory() {
  if (historyMenuIdx.value < 0) return
  emit('rename-history', historyMenuIdx.value)
  historyMenuIdx.value = -1
}

function deleteHistory() {
  if (historyMenuIdx.value < 0) return
  emit('delete-history', historyMenuIdx.value)
  historyMenuIdx.value = -1
}

function deleteHistoryAt(idx) {
  historyMenuIdx.value = -1
  emit('delete-history', idx)
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
    chartRenderKey.value += 1
  } catch (error) {
    chart.value = null
    warnings.value = []
    errorMessage.value = error.message || '图表生成失败'
    chartRenderKey.value += 1
  } finally {
    loading.value = false
  }
}

function extractSavedChart(result) {
  const chartSection = (result?.sections || []).find(section => section?.type === 'charts' && Array.isArray(section.charts))
  return chartSection?.charts?.[0] || null
}

async function saveCurrentVisualization() {
  if (!chart.value && canPreview.value) {
    await loadPreview()
  }
  if (!chart.value || saving.value) return
  saving.value = true
  try {
    await api.saveVisualization(props.sessionId, {
      chart: chart.value,
      title: chart.value.title || options.title || '可视化图表',
      warnings: warnings.value,
      config: {
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
      },
    })
    emit('history-saved')
  } catch (error) {
    alert('保存记录失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}
</script>
