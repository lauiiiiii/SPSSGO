<template>
  <div v-if="result" class="md-result-expand">
    <div class="md-result-expand-head">
      <span class="md-result-expand-title">{{ result.name }}</span>
      <button class="md-result-expand-close" @click="$emit('close')">&times;</button>
    </div>
    <div class="md-result-expand-body">
      <template v-for="(r, ri) in results" :key="ri">
        <template v-if="r.sections?.length">
          <template v-for="(sec, si) in r.sections" :key="si">
            <div v-if="sec.type === 'table'" class="md-res-table-block">
              <div class="md-res-table-title">{{ sec.title }}</div>
              <div class="md-res-table-wrap">
                <table class="tlt">
                  <thead><tr><th v-for="(h, hi) in sec.headers" :key="hi">{{ h }}</th></tr></thead>
                  <tbody><tr v-for="(row, roi) in sec.rows" :key="roi"><td v-for="(cell, ci) in row" :key="ci">{{ cellText(cell) }}</td></tr></tbody>
                </table>
              </div>
              <p v-if="sec.note" class="md-res-note">{{ sec.note }}</p>
              <div v-if="sec.description" class="md-res-desc">{{ sec.description }}</div>
            </div>
            <div v-else-if="sec.type === 'advice'" class="md-res-advice">
              <strong>{{ sec.title }}</strong>
              <p>{{ sec.content }}</p>
            </div>
            <div v-else-if="sec.type === 'smart_analysis'" class="md-res-smart">
              <strong>{{ sec.title }}</strong>
              <p>{{ sec.content }}</p>
            </div>
            <div v-else-if="sec.type === 'references'" class="md-res-refs">
              <strong>{{ sec.title }}</strong>
              <ul><li v-for="(item, ii) in sec.items" :key="ii">{{ item }}</li></ul>
            </div>
            <AnalysisChartsSection
              v-else-if="sec.type === 'charts'"
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
              :chart-data-visible="chartDataVisible"
              :fmt-bin="fmtBin"
              :section="sec"
              :section-index="si"
              :set-chart-ref="setChartRef"
            />
          </template>
        </template>
        <template v-else>
          <div v-if="r.headers?.length" class="md-res-table-block">
            <div class="md-res-table-title">{{ r.name }}</div>
            <div class="md-res-table-wrap">
              <table class="tlt">
                <thead><tr><th v-for="(h, hi) in r.headers" :key="hi">{{ h }}</th></tr></thead>
                <tbody><tr v-for="(row, roi) in r.rows" :key="roi"><td v-for="(cell, ci) in row" :key="ci">{{ cellText(cell) }}</td></tr></tbody>
              </table>
            </div>
            <div v-if="r.description" class="md-res-desc">{{ r.description }}</div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import AnalysisChartsSection from '../analysis/AnalysisChartsSection.vue'
import {
  calcBoxplotLayout,
  calcGroupedBoxplotLayout,
  calcCategoryBarLayout,
  calcCategoryPieLayout,
  calcCorrespondenceMapLayout,
  calcCrosstabLayout,
  calcHistogramLayout,
  calcFactorHeatmapLayout,
  calcMetricComparisonLayout,
  calcNormalityHistogramLayout,
  calcProbabilityPlotLayout,
  calcScatterPlotLayout,
  formatBin,
} from '../../utils/analysisCharts.js'

defineProps({
  result: { type: Object, default: null },
  results: { type: Array, default: () => [] },
})

const chartDataVisible = reactive({})
const chartRefs = {}

function setChartRef(sectionIndex, chartIndex, el) {
  chartRefs[sectionIndex + '_' + chartIndex] = el
}

function fmtBin(value) {
  return formatBin(value)
}

function calcHist(data) {
  return calcHistogramLayout(data)
}

function calcBox(data) {
  return calcBoxplotLayout(data)
}

function calcGroupedBox(data) {
  return calcGroupedBoxplotLayout(data)
}

function calcCategoryBar(data, horizontal = false) {
  return calcCategoryBarLayout(data, horizontal)
}

function calcCategoryPie(data, donut = false) {
  return calcCategoryPieLayout(data, donut)
}

function calcMetricComparison(data, mode = 'line') {
  return calcMetricComparisonLayout(data, mode)
}

function calcFactorHeatmap(data) {
  return calcFactorHeatmapLayout(data)
}

function calcNormalityHist(data) {
  return calcNormalityHistogramLayout(data)
}

function calcProbabilityPlot(data) {
  return calcProbabilityPlotLayout(data)
}

function calcScatterPlot(data) {
  return calcScatterPlotLayout(data)
}

function calcCorrespondenceMap(data) {
  return calcCorrespondenceMapLayout(data)
}

function calcCrosstab(data, mode = 'stackedColumn') {
  return calcCrosstabLayout(data, mode)
}

function cellText(cell) {
  return cell && typeof cell === 'object' ? cell.text : cell
}

defineEmits(['close'])
</script>
