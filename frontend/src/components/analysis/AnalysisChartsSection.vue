<template>
  <div class="ap-sec ap-sec--charts">
    <div class="ap-sec-head">
      <span class="ap-sec-head-title">{{ section.title }}</span>
    </div>
    <div class="ap-charts-grid">
      <AnalysisChartItem
        v-for="(chart, chartIndex) in section.charts"
        :key="chartIndex"
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
        :chart="chart"
        :chart-index="chartIndex"
        :data-visible="!!chartDataVisible[sectionIndex+'_'+chartIndex]"
        :fmt-bin="fmtBin"
        :section-index="sectionIndex"
        :set-chart-ref="setChartRef"
        @hide-tip="$emit('hide-tip')"
        @move-tip="$emit('move-tip', $event)"
        @show-hist-tip="(eventArg, dataArg, indexArg) => $emit('show-hist-tip', eventArg, dataArg, indexArg)"
        @show-box-tip="(eventArg, chartArg) => $emit('show-box-tip', eventArg, chartArg)"
        @show-category-tip="(eventArg, chartArg, dataPointArg) => $emit('show-category-tip', eventArg, chartArg, dataPointArg)"
        @show-crosstab-tip="(eventArg, chartArg, dataPointArg) => $emit('show-crosstab-tip', eventArg, chartArg, dataPointArg)"
        @show-probability-tip="(eventArg, chartArg, dataPointArg) => $emit('show-probability-tip', eventArg, chartArg, dataPointArg)"
        @show-metric-tip="(eventArg, chartArg, dataPointArg) => $emit('show-metric-tip', eventArg, chartArg, dataPointArg)"
        @download-chart="(sectionArg, chartArg, titleArg) => $emit('download-chart', sectionArg, chartArg, titleArg)"
        @copy-chart="(sectionArg, chartArg) => $emit('copy-chart', sectionArg, chartArg)"
        @toggle-chart-data="(sectionArg, chartArg) => $emit('toggle-chart-data', sectionArg, chartArg)"
      />
    </div>
    <div v-if="section.description" class="ap-chart-desc">
      <span class="ap-chart-desc-icon">图表说明：</span>{{ section.description }}
    </div>
  </div>
</template>

<script setup>
import AnalysisChartItem from './AnalysisChartItem.vue'

defineProps({
  calcBox: { type: Function, required: true },
  calcGroupedBox: { type: Function, required: true },
  calcCategoryBar: { type: Function, required: true },
  calcCategoryPie: { type: Function, required: true },
  calcCorrespondenceMap: { type: Function, required: true },
  calcCrosstab: { type: Function, required: true },
  calcFactorHeatmap: { type: Function, required: true },
  calcHist: { type: Function, required: true },
  calcMetricComparison: { type: Function, required: true },
  calcNormalityHist: { type: Function, required: true },
  calcProbabilityPlot: { type: Function, required: true },
  chartDataVisible: { type: Object, required: true },
  fmtBin: { type: Function, required: true },
  section: { type: Object, required: true },
  sectionIndex: { type: Number, required: true },
  setChartRef: { type: Function, required: true },
})

defineEmits([
  'copy-chart',
  'download-chart',
  'hide-tip',
  'move-tip',
  'show-box-tip',
  'show-category-tip',
  'show-crosstab-tip',
  'show-hist-tip',
  'show-metric-tip',
  'show-probability-tip',
  'toggle-chart-data',
])
</script>
