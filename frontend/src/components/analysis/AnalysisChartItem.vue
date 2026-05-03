<template>
  <div class="ap-chart-item">
    <div class="ap-chart-caption">{{ chart.title }}</div>
    <div class="ap-chart-wrap" :ref="el => setChartRef(sectionIndex, chartIndex, el)">
      <template v-if="chart.chartType === 'histogram'">
        <template v-for="histogramData in [calcHist(chart.data)]" :key="0">
          <svg class="ap-chart-svg" :viewBox="`0 0 ${histogramData.W} ${histogramData.H}`" :width="histogramData.W" :height="histogramData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="histogramData.ml" :y="histogramData.mt" :width="histogramData.pw" :height="histogramData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in histogramData.yTicks" :key="'yg'+tickIndex"
              :x1="histogramData.ml" :y1="tick.y" :x2="histogramData.ml+histogramData.pw" :y2="tick.y"
              stroke="#efefef" stroke-width="1"/>
            <rect v-for="(bar, barIndex) in histogramData.bars" :key="barIndex"
              :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h"
              fill="#5b8ff9" rx="1" style="cursor:pointer"
              @mouseenter="$emit('show-hist-tip', $event, chart.data, barIndex)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <line :x1="histogramData.ml" :y1="histogramData.mt+histogramData.ph" :x2="histogramData.ml+histogramData.pw" :y2="histogramData.mt+histogramData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="histogramData.ml" :y1="histogramData.mt" :x2="histogramData.ml" :y2="histogramData.mt+histogramData.ph" stroke="#bbb" stroke-width="1"/>
            <text v-for="(tick, tickIndex) in histogramData.xTicks" :key="'xl'+tickIndex"
              :x="tick.x" :y="histogramData.mt+histogramData.ph+16" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            <text v-for="(tick, tickIndex) in histogramData.yTicks" :key="'yl'+tickIndex"
              :x="histogramData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            <text :x="13" :y="histogramData.mt+histogramData.ph/2" text-anchor="middle" font-size="11" fill="#aaa"
              :transform="`rotate(-90,13,${histogramData.mt+histogramData.ph/2})`">频数</text>
          </svg>
        </template>
      </template>
      <template v-else-if="chart.chartType === 'boxplot'">
        <template v-for="boxplotData in [calcBox(chart.data)]" :key="0">
          <svg class="ap-chart-svg ap-chart-svg--box" :viewBox="`0 0 ${boxplotData.W} ${boxplotData.H}`" :width="boxplotData.W" :height="boxplotData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="boxplotData.ml" :y="boxplotData.mt" :width="boxplotData.W-boxplotData.ml-20" :height="boxplotData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in boxplotData.yTicks" :key="'yg'+tickIndex"
              :x1="boxplotData.ml" :y1="tick.y" :x2="boxplotData.cx+boxplotData.bw+20" :y2="tick.y"
              stroke="#efefef" stroke-width="1"/>
            <line :x1="boxplotData.ml" :y1="boxplotData.mt" :x2="boxplotData.ml" :y2="boxplotData.mt+boxplotData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="boxplotData.cx" :y1="boxplotData.yWH" :x2="boxplotData.cx" :y2="boxplotData.yQ3" stroke="#5b8ff9" stroke-width="1.5"/>
            <line :x1="boxplotData.cx" :y1="boxplotData.yQ1" :x2="boxplotData.cx" :y2="boxplotData.yWL" stroke="#5b8ff9" stroke-width="1.5"/>
            <line :x1="boxplotData.cx-boxplotData.bw*0.6" :y1="boxplotData.yWH" :x2="boxplotData.cx+boxplotData.bw*0.6" :y2="boxplotData.yWH" stroke="#5b8ff9" stroke-width="1.5"/>
            <line :x1="boxplotData.cx-boxplotData.bw*0.6" :y1="boxplotData.yWL" :x2="boxplotData.cx+boxplotData.bw*0.6" :y2="boxplotData.yWL" stroke="#5b8ff9" stroke-width="1.5"/>
            <rect :x="boxplotData.cx-boxplotData.bw-6" :y="Math.min(boxplotData.yWH, ...(boxplotData.outlierPts.map(o=>o.y)))-10"
              :width="boxplotData.bw*2+12"
              :height="Math.max(boxplotData.yWL, ...(boxplotData.outlierPts.map(o=>o.y)))-Math.min(boxplotData.yWH, ...(boxplotData.outlierPts.map(o=>o.y)))+20"
              fill="transparent" style="cursor:pointer"
              @mouseenter="$emit('show-box-tip', $event, chart)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <rect :x="boxplotData.cx-boxplotData.bw" :y="boxplotData.yQ3" :width="boxplotData.bw*2" :height="boxplotData.yQ1-boxplotData.yQ3"
              fill="white" stroke="#5b8ff9" stroke-width="1.5" pointer-events="none"/>
            <line :x1="boxplotData.cx-boxplotData.bw" :y1="boxplotData.yMed" :x2="boxplotData.cx+boxplotData.bw" :y2="boxplotData.yMed"
              stroke="#5b8ff9" stroke-width="2" pointer-events="none"/>
            <circle v-for="(outlier, outlierIndex) in boxplotData.outlierPts" :key="outlierIndex"
              :cx="boxplotData.cx" :cy="outlier.y" r="4" fill="#52c41a" stroke="white" stroke-width="1.2" pointer-events="none"/>
            <text v-for="(tick, tickIndex) in boxplotData.yTicks" :key="'yl'+tickIndex"
              :x="boxplotData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
          </svg>
        </template>
      </template>
    </div>
    <div class="ap-chart-actions">
      <button class="ap-chart-act-btn" @click="$emit('download-chart', sectionIndex, chartIndex, chart.title)" title="保存图片">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v8m0 0l-3-3m3 3l3-3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 12h10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
        保存
      </button>
      <button class="ap-chart-act-btn" @click="$emit('copy-chart', sectionIndex, chartIndex)" title="复制图片">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
        复制
      </button>
      <button class="ap-chart-act-btn" :class="{ 'is-active': dataVisible }"
        @click="$emit('toggle-chart-data', sectionIndex, chartIndex)" title="查看数据">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="2.5" width="13" height="11" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M1.5 6h13M6 6v8" stroke="currentColor" stroke-width="1.2"/></svg>
        数据
      </button>
    </div>
    <div v-if="dataVisible && chart.chartType === 'histogram'" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>分段起始值</th><th>分段终止值</th><th>频数</th></tr></thead>
        <tbody>
          <tr v-for="(_, binIndex) in chart.data.counts" :key="binIndex">
            <td>{{ fmtBin(chart.data.binEdges[binIndex]) }}</td>
            <td>{{ fmtBin(chart.data.binEdges[binIndex+1]) }}</td>
            <td>{{ chart.data.counts[binIndex] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="dataVisible && chart.chartType === 'boxplot'" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>指标</th><th>值</th></tr></thead>
        <tbody>
          <tr><td>最小值</td><td>{{ chart.data.whiskerLow }}</td></tr>
          <tr><td>25%分位数</td><td>{{ chart.data.q1 }}</td></tr>
          <tr><td>中位数</td><td>{{ chart.data.median }}</td></tr>
          <tr><td>75%分位数</td><td>{{ chart.data.q3 }}</td></tr>
          <tr><td>最大值</td><td>{{ chart.data.whiskerHigh }}</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  calcBox: { type: Function, required: true },
  calcHist: { type: Function, required: true },
  chart: { type: Object, required: true },
  chartIndex: { type: Number, required: true },
  dataVisible: { type: Boolean, default: false },
  fmtBin: { type: Function, required: true },
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
