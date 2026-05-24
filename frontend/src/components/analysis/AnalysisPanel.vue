<template>
  <section class="analysis-panel">
    <!-- No data uploaded yet -->
    <AnalysisUploadPrompt v-if="!hasData" @upload="$emit('upload')" />

    <!-- No method selected and no results to show -->
    <AnalysisMethodPlaceholder v-else-if="!method && !(results && results.length)" />

    <!-- Method selected OR has results from history -->
    <div v-else class="ap-scroll-body">
      <!-- 有结果且未选择「返回配置」时：独立报告页（类 SPSSPRO） -->
      <AnalysisReportPage
        v-if="results.length && !executing && !editingConfig"
        :ai-loading="aiLoading"
        :ai-result="aiResult"
        :allow-ai-request="true"
        :calc-box="calcBox"
        :calc-category-bar="calcCategoryBar"
        :calc-category-pie="calcCategoryPie"
        :calc-correspondence-map="calcCorrespondenceMap"
        :calc-crosstab="calcCrosstab"
        :calc-factor-heatmap="calcFactorHeatmap"
        :calc-hist="calcHist"
        :calc-metric-comparison="calcMetricComparison"
        :calc-normality-hist="calcNormalityHist"
        :calc-probability-plot="calcProbabilityPlot"
        :cell-class="cellClass"
        :chart-data-visible="chartDataVisible"
        :display-results="displayResults"
        :fmt-bin="fmtBin"
        :report-meta-tags="reportMetaTags"
        :report-title="reportTitle"
        :results="results"
        :set-chart-ref="setChartRef"
        :show-share="true"
        @edit-config="editConfig"
        @export-pdf="exportPDF"
        @export-word="exportWord"
        @share="openShareDialog"
        @copy-all="copyAllResults"
        @copy-table="copyTable"
        @request-ai="requestAiInterpret"
        @hide-tip="hideTip"
        @move-tip="moveTip"
        @show-hist-tip="showHistTip"
        @show-box-tip="showBoxTip"
        @show-category-tip="showCategoryTip"
        @show-crosstab-tip="showCrosstabTip"
        @show-probability-tip="showProbabilityTip"
        @download-chart="downloadChart"
        @show-metric-tip="showMetricTip"
        @copy-chart="copyChart"
        @toggle-chart-data="toggleChartData"
      />

      <!-- 配置区：有方法且（无结果、执行中、或用户点击返回配置） -->
      <AnalysisConfigPanel
        v-else-if="method"
        :active-second-order-factor-name="activeSecondOrderFactorName"
        :active-second-order-key="activeSecondOrderKey"
        :active-second-order-members="activeSecondOrderMembers"
        :active-factor-items="activeFactorItems"
        :active-factor-key="activeFactorKey"
        :active-factor-slot="activeFactorSlot"
        :active-factor-title="activeFactorTitle"
        :can-execute="canExecute"
        :display-slots="displaySlots"
        :drag-preview-count="dragPreviewCount"
        :drag-over-slot="dragOverSlot"
        :dynamic-factor-count="dynamicFactorCount"
        :dynamic-group-add-text="dynamicGroupAddText"
        :dynamic-group-item-name="dynamicGroupItemName"
        :dynamic-group-tip="dynamicGroupTip"
        :editing-config="editingConfig"
        :executing="executing"
        :factor-menu-key="factorMenuKey"
        :first-order-factor-choices="firstOrderFactorChoices"
        :get-factor-short-label="getFactorShortLabel"
        :get-var-type="getVarType"
        :get-var-type-class="getVarTypeClass"
        :is-cfa-method="isCfaMethod"
        :is-one-sample-equivalence-method="isOneSampleEquivalenceMethod"
        :is-one-way-anova-method="isOneWayAnovaMethod"
        :is-paired-equivalence-method="isPairedEquivalenceMethod"
        :is-summary-one-way-anova-method="isSummaryOneWayAnovaMethod"
        :is-summary-t-method="isSummaryTMethod"
        :is-two-sample-equivalence-method="isTwoSampleEquivalenceMethod"
        :max-dynamic-factors="maxDynamicFactors"
        :max-second-order-models="maxSecondOrderModels"
        :method="method"
        :option-values="optionValues"
        :rename-focus-token="renameFocusToken"
        :results="results"
        :second-order-models="secondOrderModels"
        :second-order-factor-choices="secondOrderFactorChoices"
        :slot-values="slotValues"
        :variables="variables"
        @show-report="showReport"
        @add-second-order-model="addSecondOrderModel"
        @add-factor="addFactorSlot"
        @add-summary-one-way-group="addSummaryOneWayGroup"
        @select-factor="selectFactor"
        @toggle-factor-menu="toggleFactorMenu"
        @rename-factor="renameFactor"
        @rename-factor-inline="renameFactorInline"
        @delete-factor="deleteFactor"
        @delete-second-order-model="deleteSecondOrderModel"
        @remove-summary-one-way-group="removeSummaryOneWayGroup"
        @close-factor-menu="factorMenuKey = null"
        @drag-over="onDragOver"
        @drag-leave="onDragLeave"
        @drop-slot="onDrop"
        @remove-var="removeVar"
        @option-change="setOptionValue"
        @rename-second-order-factor="setSecondOrderFactorName"
        @reset="handleReset"
        @select-second-order-model="selectSecondOrderModel"
        @execute="$emit('execute')"
        @toggle-second-order-member="toggleSecondOrderMember"
        @update-summary-one-way-group="updateSummaryOneWayGroup"
      />

      <!-- Executing indicator -->
      <AnalysisExecutingOverlay :executing="executing" :method="method" />
    </div>
    <AnalysisShareDialog
      v-if="shareDialogVisible"
      :copied="copiedShareUrl"
      :expiry-days="shareExpiryDays"
      :error="shareError"
      :loading="shareLoading"
      :password="sharePassword"
      :share-text="shareText"
      :share-url="shareUrl"
      @close="closeShareDialog"
      @copy="copyShareUrl"
      @fill-random-password="fillRandomSharePassword"
      @generate="generateShareLink"
      @update:expiry-days="shareExpiryDays = $event"
      @update:password="sharePassword = $event"
    />
    <!-- chart tooltip -->
    <AnalysisChartTooltip :tip="tip" />
  </section>
</template>

<script setup>
import { toRef } from 'vue'
import AnalysisChartTooltip from './AnalysisChartTooltip.vue'
import AnalysisConfigPanel from './AnalysisConfigPanel.vue'
import AnalysisExecutingOverlay from './AnalysisExecutingOverlay.vue'
import AnalysisMethodPlaceholder from './AnalysisMethodPlaceholder.vue'
import AnalysisReportPage from './AnalysisReportPage.vue'
import AnalysisShareDialog from './AnalysisShareDialog.vue'
import AnalysisUploadPrompt from './AnalysisUploadPrompt.vue'
import { useAnalysisConfig } from '../../composables/analysis/useAnalysisConfig.js'
import { useAnalysisCharts } from '../../composables/analysis/useAnalysisCharts.js'
import { useAiInterpretation } from '../../composables/analysis/useAiInterpretation.js'
import { useAnalysisReport } from '../../composables/analysis/useAnalysisReport.js'
import { useAnalysisShare } from '../../composables/analysis/useAnalysisShare.js'
import { useAnalysisViewState } from '../../composables/analysis/useAnalysisViewState.js'

const props = defineProps({
  hasData: { type: Boolean, default: false },
  method: { type: Object, default: null },
  methodKey: { type: String, default: '' },
  executing: { type: Boolean, default: false },
  results: { type: Array, default: () => [] },
  variables: { type: Array, default: () => [] },
  dragPreviewCount: { type: Number, default: 0 },
  sessionId: { type: String, default: '' },
  currentDatasetVersionId: { type: Number, default: null },
  currentDatasetVersionNo: { type: Number, default: null },
})

const emit = defineEmits(['upload', 'execute', 'update:slotValues', 'update:optionValues', 'report-view', 'reset-variable-selection'])

const {
  activeSecondOrderFactorName,
  activeSecondOrderKey,
  activeSecondOrderMembers,
  activeFactorItems,
  activeFactorKey,
  activeFactorSlot,
  activeFactorTitle,
  addSecondOrderModel,
  addFactorSlot,
  addSummaryOneWayGroup,
  addVar,
  canExecute,
  deleteFactor,
  deleteSecondOrderModel,
  displaySlots,
  dragOverSlot,
  dynamicFactorCount,
  dynamicGroupAddText,
  dynamicGroupItemName,
  dynamicGroupTip,
  factorMenuKey,
  firstOrderFactorChoices,
  getFactorShortLabel,
  isCfaMethod,
  isOneSampleEquivalenceMethod,
  isOneWayAnovaMethod,
  isPairedEquivalenceMethod,
  isSummaryOneWayAnovaMethod,
  isSummaryTMethod,
  isTwoSampleEquivalenceMethod,
  maxDynamicFactors,
  maxSecondOrderModels,
  onDragLeave,
  onDragOver,
  onDrop,
  optionValues,
  removeSummaryOneWayGroup,
  removeVar,
  renameFactor,
  renameFactorInline,
  renameFocusToken,
  resetSlots,
  selectFactor,
  selectSecondOrderModel,
  setOptionValue,
  setSecondOrderFactorName,
  secondOrderModels,
  secondOrderFactorChoices,
  slotValues,
  toggleFactorMenu,
  toggleSecondOrderMember,
  updateSummaryOneWayGroup,
} = useAnalysisConfig(toRef(props, 'method'), toRef(props, 'methodKey'), emit)
const {
  calcBox,
  calcCategoryBar,
  calcCategoryPie,
  calcCorrespondenceMap,
  calcCrosstab,
  calcFactorHeatmap,
  calcHist,
  calcMetricComparison,
  calcNormalityHist,
  calcProbabilityPlot,
  chartDataVisible,
  copyChart,
  downloadChart,
  fmtBin,
  hideTip,
  moveTip,
  resetCharts,
  setChartRef,
  showBoxTip,
  showCategoryTip,
  showCrosstabTip,
  showHistTip,
  showMetricTip,
  showProbabilityTip,
  tip,
  toggleChartData,
} = useAnalysisCharts()
const {
  cellClass,
  copyAllResults,
  copyTable,
  displayResults,
  exportPDF,
  exportWord,
  getVarType,
  getVarTypeClass,
  reportMetaTags,
  reportTitle,
} = useAnalysisReport(props)

const {
  aiLoading,
  aiResult,
  requestAiInterpret,
  resetAiInterpretation,
} = useAiInterpretation(toRef(props, 'sessionId'))
const {
  closeShareDialog,
  copiedShareUrl,
  copyShareUrl,
  fillRandomSharePassword,
  generateShareLink,
  openShareDialog,
  shareDialogVisible,
  shareError,
  shareExpiryDays,
  shareLoading,
  sharePassword,
  shareText,
  shareUrl,
} = useAnalysisShare({
  aiResult,
  displayResults,
  reportMetaTags,
  reportTitle,
  results: toRef(props, 'results'),
  sessionId: toRef(props, 'sessionId'),
})
const {
  editConfig,
  editingConfig,
  showReport,
} = useAnalysisViewState(props, emit, { resetAiInterpretation, resetCharts })

function handleReset() {
  resetSlots()
  emit('reset-variable-selection')
}

defineExpose({ addVar, slotValues, optionValues, canExecute })
</script>
