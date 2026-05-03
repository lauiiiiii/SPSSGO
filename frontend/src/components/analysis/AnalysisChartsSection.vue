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
        :calc-hist="calcHist"
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
  calcHist: { type: Function, required: true },
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
  'show-hist-tip',
  'toggle-chart-data',
])
</script>
