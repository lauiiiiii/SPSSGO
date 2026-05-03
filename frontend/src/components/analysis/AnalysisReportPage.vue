<template>
  <div class="ap-report-page">
    <AnalysisReportToolbar
      :report-meta-tags="reportMetaTags"
      :report-title="reportTitle"
      :show-copy-all="showCopyAll"
      :show-edit-config="showEditConfig"
      :show-export-actions="showExportActions"
      :show-share="showShare"
      @edit-config="$emit('edit-config')"
      @export-pdf="$emit('export-pdf')"
      @export-word="$emit('export-word')"
      @share="$emit('share')"
      @copy-all="$emit('copy-all')"
    />
    <div class="ap-report-body">
      <div v-for="(result, resultIndex) in displayResults" :key="resultIndex" class="ap-report-card-wrap">
        <div class="ap-report-result-title">
          <span class="ap-report-result-bar"></span>
          {{ result.name }}
        </div>
        <template v-if="result.sections?.length">
          <template v-for="(section, sectionIndex) in result.sections" :key="sectionIndex">
            <AnalysisTableSection
              v-if="section.type === 'table'"
              :cell-class="cellClass"
              :section="section"
              @copy-table="(sectionArg, eventArg) => $emit('copy-table', sectionArg, eventArg)"
            />

            <AnalysisAdviceSection v-else-if="section.type === 'advice'" :section="section" />

            <AnalysisSmartSection
              v-else-if="section.type === 'smart_analysis'"
              :ai-loading="aiLoading"
              :ai-result="aiResult"
              :allow-ai-request="allowAiRequest"
              :section="section"
              @request-ai="$emit('request-ai', results[resultIndex])"
            />

            <AnalysisReferencesSection v-else-if="section.type === 'references'" :section="section" />

            <AnalysisChartsSection
              v-else-if="section.type === 'charts'"
              :calc-box="calcBox"
              :calc-hist="calcHist"
              :chart-data-visible="chartDataVisible"
              :fmt-bin="fmtBin"
              :section="section"
              :section-index="sectionIndex"
              :set-chart-ref="setChartRef"
              @hide-tip="$emit('hide-tip')"
              @move-tip="$emit('move-tip', $event)"
              @show-hist-tip="(eventArg, dataArg, indexArg) => $emit('show-hist-tip', eventArg, dataArg, indexArg)"
              @show-box-tip="(eventArg, chartArg) => $emit('show-box-tip', eventArg, chartArg)"
              @download-chart="(sectionArg, chartArg, titleArg) => $emit('download-chart', sectionArg, chartArg, titleArg)"
              @copy-chart="(sectionArg, chartArg) => $emit('copy-chart', sectionArg, chartArg)"
              @toggle-chart-data="(sectionArg, chartArg) => $emit('toggle-chart-data', sectionArg, chartArg)"
            />
          </template>
        </template>

        <template v-else>
          <AnalysisTableSection
            :cell-class="cellClass"
            :copyable="false"
            :section="result"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import AnalysisAdviceSection from './AnalysisAdviceSection.vue'
import AnalysisChartsSection from './AnalysisChartsSection.vue'
import AnalysisReferencesSection from './AnalysisReferencesSection.vue'
import AnalysisReportToolbar from './AnalysisReportToolbar.vue'
import AnalysisSmartSection from './AnalysisSmartSection.vue'
import AnalysisTableSection from './AnalysisTableSection.vue'

defineProps({
  aiLoading: { type: Boolean, default: false },
  aiResult: { type: String, default: '' },
  allowAiRequest: { type: Boolean, default: true },
  calcBox: { type: Function, required: true },
  calcHist: { type: Function, required: true },
  cellClass: { type: Function, required: true },
  chartDataVisible: { type: Object, required: true },
  displayResults: { type: Array, default: () => [] },
  fmtBin: { type: Function, required: true },
  reportMetaTags: { type: Array, default: () => [] },
  reportTitle: { type: String, default: '分析报告' },
  results: { type: Array, default: () => [] },
  setChartRef: { type: Function, required: true },
  showCopyAll: { type: Boolean, default: true },
  showEditConfig: { type: Boolean, default: true },
  showExportActions: { type: Boolean, default: true },
  showShare: { type: Boolean, default: false },
})

defineEmits([
  'copy-all',
  'copy-chart',
  'copy-table',
  'download-chart',
  'edit-config',
  'export-pdf',
  'export-word',
  'hide-tip',
  'move-tip',
  'request-ai',
  'share',
  'show-box-tip',
  'show-hist-tip',
  'toggle-chart-data',
])
</script>
