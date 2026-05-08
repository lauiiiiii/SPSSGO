<template>
  <div class="ap-chart-item">
    <div class="ap-chart-caption">{{ displayTitle }}</div>
    <div v-if="supportsDataLabels" class="ap-chart-label-toolbar">
      <select
        v-if="supportsLabelMode"
        v-model="labelMode"
        class="ap-chart-label-select"
        title="切换标签显示内容"
      >
        <option value="count">数字</option>
        <option value="percent">百分比</option>
      </select>
    </div>
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
      <template v-else-if="isCategoryChart">
        <template v-if="categoryMode === 'bar'" v-for="categoryData in [calcCategoryBar(chart.data, false)]" :key="'bar'">
          <svg class="ap-chart-svg ap-chart-svg--category" :viewBox="`0 0 ${categoryData.W} ${categoryData.H}`" :width="categoryData.W" :height="categoryData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="categoryData.ml" :y="categoryData.mt" :width="categoryData.pw" :height="categoryData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in categoryData.yTicks" :key="'fyg'+tickIndex"
              :x1="categoryData.ml" :y1="tick.y" :x2="categoryData.ml+categoryData.pw" :y2="tick.y"
              stroke="#eef1f5" stroke-width="1"/>
            <rect v-for="(bar, barIndex) in categoryData.bars" :key="barIndex"
              class="ap-category-mark"
              :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" fill="#2389e8" rx="2"
              @mouseenter="$emit('show-category-tip', $event, chart, bar)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <text v-for="(bar, barIndex) in categoryData.bars" :key="'fv'+barIndex"
              v-show="showDataLabels"
              :x="bar.x + bar.w / 2" :y="Math.max(bar.y - 6, 12)" text-anchor="middle" font-size="11" fill="#333">{{ chartValueLabel(bar.count, bar.percent) }}</text>
            <line :x1="categoryData.ml" :y1="categoryData.mt+categoryData.ph" :x2="categoryData.ml+categoryData.pw" :y2="categoryData.mt+categoryData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="categoryData.ml" :y1="categoryData.mt" :x2="categoryData.ml" :y2="categoryData.mt+categoryData.ph" stroke="#bbb" stroke-width="1"/>
            <text v-for="(bar, barIndex) in categoryData.bars" :key="'fx'+barIndex"
              :x="bar.tickX" :y="categoryData.mt+categoryData.ph+18" text-anchor="middle" font-size="11" fill="#666">{{ categoryData.shortLabel(bar.label) }}</text>
            <text v-for="(tick, tickIndex) in categoryData.yTicks" :key="'fy'+tickIndex"
              :x="categoryData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            <text :x="15" :y="categoryData.mt+categoryData.ph/2" text-anchor="middle" font-size="11" fill="#777"
              :transform="`rotate(-90,15,${categoryData.mt+categoryData.ph/2})`">百分比(%)</text>
          </svg>
        </template>
        <template v-else-if="categoryMode === 'horizontalBar'" v-for="categoryData in [calcCategoryBar(chart.data, true)]" :key="'horizontalBar'">
          <svg class="ap-chart-svg ap-chart-svg--category" :viewBox="`0 0 ${categoryData.W} ${categoryData.H}`" :width="categoryData.W" :height="categoryData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="categoryData.ml" :y="categoryData.mt" :width="categoryData.pw" :height="categoryData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in categoryData.xTicks" :key="'fhg'+tickIndex"
              :x1="tick.x" :y1="categoryData.mt" :x2="tick.x" :y2="categoryData.mt+categoryData.ph"
              stroke="#eef1f5" stroke-width="1"/>
            <rect v-for="(bar, barIndex) in categoryData.bars" :key="barIndex"
              class="ap-category-mark"
              :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" fill="#2389e8" rx="2"
              @mouseenter="$emit('show-category-tip', $event, chart, bar)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <text v-for="(bar, barIndex) in categoryData.bars" :key="'fhv'+barIndex"
              v-show="showDataLabels"
              :x="bar.x + bar.w + 6" :y="bar.labelY + 4" text-anchor="start" font-size="11" fill="#333">{{ chartValueLabel(bar.count, bar.percent) }}</text>
            <line :x1="categoryData.ml" :y1="categoryData.mt+categoryData.ph" :x2="categoryData.ml+categoryData.pw" :y2="categoryData.mt+categoryData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="categoryData.ml" :y1="categoryData.mt" :x2="categoryData.ml" :y2="categoryData.mt+categoryData.ph" stroke="#bbb" stroke-width="1"/>
            <text v-for="(bar, barIndex) in categoryData.bars" :key="'fhy'+barIndex"
              :x="categoryData.ml-8" :y="bar.labelY+4" text-anchor="end" font-size="11" fill="#666">{{ bar.label }}</text>
            <text v-for="(tick, tickIndex) in categoryData.xTicks" :key="'fhx'+tickIndex"
              :x="tick.x" :y="categoryData.mt+categoryData.ph+18" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            <text :x="categoryData.ml+categoryData.pw/2" :y="categoryData.H-10" text-anchor="middle" font-size="11" fill="#777">百分比(%)</text>
          </svg>
        </template>
        <template v-else v-for="pieData in [calcCategoryPie(chart.data, categoryMode === 'donut')]" :key="categoryMode">
          <svg class="ap-chart-svg ap-chart-svg--category" :viewBox="`0 0 ${pieData.W} ${pieData.H}`" :width="pieData.W" :height="pieData.H"
            @mouseleave="$emit('hide-tip')">
            <path v-for="(slice, sliceIndex) in pieData.slices" :key="'slice'+sliceIndex"
              class="ap-category-mark"
              :d="slice.path" :fill="slice.color" stroke="#fff" stroke-width="1.5"
              @mouseenter="$emit('show-category-tip', $event, chart, slice)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <circle v-if="pieData.donut" :cx="pieData.cx" :cy="pieData.cy" :r="pieData.innerR" fill="#fff"/>
            <line v-for="(slice, sliceIndex) in pieData.slices" :key="'line'+sliceIndex"
              :x1="slice.lineStart.x" :y1="slice.lineStart.y" :x2="slice.lineEnd.x" :y2="slice.lineEnd.y"
              :stroke="slice.color" stroke-width="1"/>
            <text v-for="(slice, sliceIndex) in pieData.slices" :key="'label'+sliceIndex"
              :x="slice.labelX" :y="slice.labelY+4" :text-anchor="slice.labelAnchor" font-size="11" fill="#333">{{ slice.labelText }}</text>
          </svg>
        </template>
      </template>
      <template v-else-if="isCrosstabChart">
        <template v-for="crossData in [calcCrosstab(chart.data, crosstabMode)]" :key="crosstabMode">
          <svg class="ap-chart-svg ap-chart-svg--crosstab" :viewBox="`0 0 ${crossData.W} ${crossData.H}`" :width="crossData.W" :height="crossData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="crossData.ml" :y="crossData.mt" :width="crossData.pw" :height="crossData.ph" fill="white"/>
            <template v-if="crossData.horizontal">
              <line v-for="(tick, tickIndex) in crossData.xTicks" :key="'cxg'+tickIndex"
                :x1="tick.x" :y1="crossData.mt" :x2="tick.x" :y2="crossData.mt+crossData.ph" stroke="#eef1f5" stroke-width="1"/>
              <rect v-for="(mark, markIndex) in crossData.marks" :key="'cm'+markIndex"
                class="ap-crosstab-mark"
                :x="mark.x" :y="mark.y" :width="mark.w" :height="mark.h" :fill="mark.color"
                @mouseenter="$emit('show-crosstab-tip', $event, chart, mark)"
                @mousemove="$emit('move-tip', $event)"
                @mouseleave="$emit('hide-tip')"/>
              <text
                v-for="(mark, markIndex) in crosstabLabels(crossData)"
                :key="'chv'+markIndex"
                :x="crossData.stacked ? mark.labelX : mark.x + mark.w + 5"
                :y="mark.labelY+4"
                :text-anchor="crossData.stacked ? 'middle' : 'start'"
                font-size="10"
                fill="#111"
              >{{ crosstabMarkLabel(mark) }}</text>
              <text v-for="(label, labelIndex) in crossData.groupLabels" :key="'cyl'+labelIndex"
                :x="crossData.ml-8" :y="crossData.mt + (labelIndex + .5) * (crossData.ph / Math.max(crossData.groupLabels.length, 1)) + 4"
                text-anchor="end" font-size="11" fill="#666">{{ label }}</text>
              <text v-for="(tick, tickIndex) in crossData.xTicks" :key="'cxt'+tickIndex"
                :x="tick.x" :y="crossData.mt+crossData.ph+18" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            </template>
            <template v-else>
              <line v-for="(tick, tickIndex) in crossData.yTicks" :key="'cyg'+tickIndex"
                :x1="crossData.ml" :y1="tick.y" :x2="crossData.ml+crossData.pw" :y2="tick.y" stroke="#eef1f5" stroke-width="1"/>
              <rect v-for="(mark, markIndex) in crossData.marks" :key="'cm'+markIndex"
                class="ap-crosstab-mark"
                :x="mark.x" :y="mark.y" :width="mark.w" :height="mark.h" :fill="mark.color"
                @mouseenter="$emit('show-crosstab-tip', $event, chart, mark)"
                @mousemove="$emit('move-tip', $event)"
                @mouseleave="$emit('hide-tip')"/>
              <text
                v-for="(mark, markIndex) in crosstabLabels(crossData)"
                :key="'cv'+markIndex"
                :x="mark.labelX"
                :y="mark.labelY+4"
                text-anchor="middle"
                font-size="10"
                fill="#111"
              >{{ crosstabMarkLabel(mark) }}</text>
              <text v-for="(label, labelIndex) in crossData.groupLabels" :key="'cxl'+labelIndex"
                :x="crossData.ml + (labelIndex + .5) * (crossData.pw / Math.max(crossData.groupLabels.length, 1))"
                :y="crossData.mt+crossData.ph+18" text-anchor="middle" font-size="11" fill="#666">{{ label }}</text>
              <text v-for="(tick, tickIndex) in crossData.yTicks" :key="'cyt'+tickIndex"
                :x="crossData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            </template>
            <line :x1="crossData.ml" :y1="crossData.mt+crossData.ph" :x2="crossData.ml+crossData.pw" :y2="crossData.mt+crossData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="crossData.ml" :y1="crossData.mt" :x2="crossData.ml" :y2="crossData.mt+crossData.ph" stroke="#bbb" stroke-width="1"/>
            <g class="ap-crosstab-legend">
              <g v-for="(label, labelIndex) in crossData.xLabels" :key="'cl'+labelIndex" :transform="`translate(${crossData.ml + labelIndex * 62}, ${crossData.H - 22})`">
                <rect width="10" height="10" :fill="crossData.marks.find(item => item.seriesLabel === label)?.color || '#2389e8'"/>
                <text x="15" y="9" font-size="11" fill="#666">{{ label }}</text>
              </g>
            </g>
          </svg>
        </template>
      </template>
      <template v-else-if="isMetricComparisonChart">
        <template v-for="metricData in [calcMetricComparison(chart.data, metricMode)]" :key="metricMode">
          <svg class="ap-chart-svg ap-chart-svg--metric" :viewBox="`0 0 ${metricData.W} ${metricData.H}`" :width="metricData.W" :height="metricData.H"
            @mouseleave="$emit('hide-tip')">
            <template v-if="metricMode === 'radar'">
              <polygon v-for="(ring, ringIndex) in metricData.rings" :key="'ring'+ringIndex" :points="ring" fill="none" stroke="#eef1f5" stroke-width="1"/>
              <line v-for="(point, pointIndex) in metricData.vertices" :key="'axis'+pointIndex"
                :x1="metricData.cx" :y1="metricData.cy" :x2="point.axisX" :y2="point.axisY" stroke="#eef1f5" stroke-width="1"/>
              <polygon :points="metricData.polygon" fill="rgba(35,137,232,.16)" stroke="#2389e8" stroke-width="2"/>
              <circle v-for="(point, pointIndex) in metricData.vertices" :key="'dot'+pointIndex"
                :cx="point.x" :cy="point.y" r="4" fill="#2389e8"
                @mouseenter="$emit('show-metric-tip', $event, chart, point)"
                @mousemove="$emit('move-tip', $event)"
                @mouseleave="$emit('hide-tip')"/>
              <text v-for="(point, pointIndex) in metricData.vertices" :key="'label'+pointIndex"
                :x="point.labelX" :y="point.labelY+4" :text-anchor="point.labelAnchor" font-size="11" fill="#666">{{ point.label }}</text>
            </template>
            <template v-else-if="metricMode === 'horizontalBar'">
              <rect :x="metricData.ml" :y="metricData.mt" :width="metricData.pw" :height="metricData.ph" fill="white"/>
              <line v-for="(tick, tickIndex) in metricData.xTicks" :key="'mxg'+tickIndex"
                :x1="tick.x" :y1="metricData.mt" :x2="tick.x" :y2="metricData.mt+metricData.ph" stroke="#eef1f5" stroke-width="1"/>
              <rect v-for="(bar, barIndex) in metricData.bars" :key="'mbar'+barIndex"
                class="ap-metric-mark"
                :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" fill="#2389e8" rx="2"
                @mouseenter="$emit('show-metric-tip', $event, chart, bar)"
                @mousemove="$emit('move-tip', $event)"
                @mouseleave="$emit('hide-tip')"/>
              <line :x1="metricData.ml" :y1="metricData.mt+metricData.ph" :x2="metricData.ml+metricData.pw" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <line :x1="metricData.ml" :y1="metricData.mt" :x2="metricData.ml" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <text v-for="(bar, barIndex) in metricData.bars" :key="'mhy'+barIndex"
                :x="metricData.ml-8" :y="bar.labelY+4" text-anchor="end" font-size="11" fill="#666">{{ bar.label }}</text>
              <text v-for="(tick, tickIndex) in metricData.xTicks" :key="'mhx'+tickIndex"
                :x="tick.x" :y="metricData.mt+metricData.ph+18" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            </template>
            <template v-else>
              <rect :x="metricData.ml" :y="metricData.mt" :width="metricData.pw" :height="metricData.ph" fill="white"/>
              <line v-for="(tick, tickIndex) in metricData.yTicks" :key="'myg'+tickIndex"
                :x1="metricData.ml" :y1="tick.y" :x2="metricData.ml+metricData.pw" :y2="tick.y" stroke="#eef1f5" stroke-width="1"/>
              <template v-if="metricMode === 'bar'">
                <rect v-for="(bar, barIndex) in metricData.bars" :key="'mvbar'+barIndex"
                  class="ap-metric-mark"
                  :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" fill="#2389e8" rx="2"
                  @mouseenter="$emit('show-metric-tip', $event, chart, bar)"
                  @mousemove="$emit('move-tip', $event)"
                  @mouseleave="$emit('hide-tip')"/>
              </template>
              <template v-else>
                <path :d="metricData.path" fill="none" stroke="#2389e8" stroke-width="2"/>
                <circle v-for="(point, pointIndex) in metricData.points" :key="'mp'+pointIndex"
                  class="ap-metric-mark"
                  :cx="point.x" :cy="point.y" r="4" fill="#2389e8"
                  @mouseenter="$emit('show-metric-tip', $event, chart, point)"
                  @mousemove="$emit('move-tip', $event)"
                  @mouseleave="$emit('hide-tip')"/>
              </template>
              <line :x1="metricData.ml" :y1="metricData.mt+metricData.ph" :x2="metricData.ml+metricData.pw" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <line :x1="metricData.ml" :y1="metricData.mt" :x2="metricData.ml" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <text v-for="(point, pointIndex) in metricData.points" :key="'mx'+pointIndex"
                :x="point.x" :y="metricData.mt+metricData.ph+18" text-anchor="middle" font-size="11" fill="#666">{{ metricData.shortLabel(point.label) }}</text>
              <text v-for="(tick, tickIndex) in metricData.yTicks" :key="'my'+tickIndex"
                :x="metricData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            </template>
          </svg>
        </template>
      </template>
    </div>
    <div v-if="isCategoryChart" class="ap-chart-mode-bar">
      <button
        v-for="option in categoryModeOptions"
        :key="option.value"
        class="ap-chart-mode-btn"
        :class="{ 'is-active': categoryMode === option.value }"
        @click="categoryMode = option.value"
      >
        {{ option.label }}
      </button>
    </div>
    <div v-if="isMetricComparisonChart" class="ap-chart-mode-bar">
      <button
        v-for="option in metricModeOptions"
        :key="option.value"
        class="ap-chart-mode-btn"
        :class="{ 'is-active': metricMode === option.value }"
        @click="metricMode = option.value"
      >
        {{ option.label }}
      </button>
    </div>
    <div v-if="isCrosstabChart" class="ap-chart-mode-bar">
      <button
        v-for="option in crosstabModeOptions"
        :key="option.value"
        class="ap-chart-mode-btn"
        :class="{ 'is-active': crosstabMode === option.value }"
        @click="crosstabMode = option.value"
      >
        {{ option.label }}
      </button>
    </div>
    <div class="ap-chart-actions">
      <button class="ap-chart-act-btn" @click="$emit('download-chart', sectionIndex, chartIndex, displayTitle)" title="保存图片">
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
    <div v-if="dataVisible && isCategoryChart" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>选项</th><th>频数</th><th>百分比(%)</th></tr></thead>
        <tbody>
          <tr v-for="(label, rowIndex) in chart.data.labels" :key="rowIndex">
            <td>{{ label }}</td>
            <td>{{ chart.data.counts[rowIndex] }}</td>
            <td>{{ percentLabel(chart.data.percents[rowIndex]) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="dataVisible && isMetricComparisonChart" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>名称</th><th>{{ chart.data.metric || '指标' }}</th></tr></thead>
        <tbody>
          <tr v-for="(label, rowIndex) in chart.data.labels" :key="rowIndex">
            <td>{{ label }}</td>
            <td>{{ Number(chart.data.values[rowIndex] || 0).toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="dataVisible && isCrosstabChart" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>名称</th><th v-for="label in chart.data.groupLabels" :key="label">{{ label }}</th><th>合计</th></tr></thead>
        <tbody>
          <tr v-for="(label, rowIndex) in chart.data.xLabels" :key="rowIndex">
            <td>{{ label }}</td>
            <td v-for="(_, colIndex) in chart.data.groupLabels" :key="colIndex">{{ chart.data.matrix[rowIndex]?.[colIndex] || 0 }}</td>
            <td>{{ (chart.data.matrix[rowIndex] || []).reduce((sum, value) => sum + Number(value || 0), 0) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  calcBox: { type: Function, required: true },
  calcCategoryBar: { type: Function, required: true },
  calcCategoryPie: { type: Function, required: true },
  calcCrosstab: { type: Function, required: true },
  calcHist: { type: Function, required: true },
  calcMetricComparison: { type: Function, required: true },
  chart: { type: Object, required: true },
  chartIndex: { type: Number, required: true },
  dataVisible: { type: Boolean, default: false },
  fmtBin: { type: Function, required: true },
  sectionIndex: { type: Number, required: true },
  setChartRef: { type: Function, required: true },
})

const categoryChartTypes = new Set(['category_distribution', 'category', 'categorical', 'categorical_distribution', 'frequency'])
const categoryMode = ref('bar')
const crosstabMode = ref('stackedColumn')
const labelMode = ref('percent')
const metricMode = ref('line')
const showDataLabels = ref(true)
const categoryModeOptions = [
  { value: 'bar', label: '柱状图' },
  { value: 'horizontalBar', label: '条形图' },
  { value: 'pie', label: '饼图' },
  { value: 'donut', label: '环形图' },
]
const isCategoryChart = computed(() => categoryChartTypes.has(props.chart.chartType))
const isCrosstabChart = computed(() => props.chart.chartType === 'crosstab_distribution')
const isMetricComparisonChart = computed(() => props.chart.chartType === 'metric_comparison')
const supportsDataLabels = computed(() => (
  isCrosstabChart.value
  || (isCategoryChart.value && ['bar', 'horizontalBar'].includes(categoryMode.value))
))
const supportsLabelMode = computed(() => supportsDataLabels.value)
const categoryTitle = computed(() => {
  const option = categoryModeOptions.find(item => item.value === categoryMode.value)
  const label = option?.label || '柱状图'
  return `${props.chart.varName || props.chart.data?.variable || props.chart.title}${label}`
})
const metricModeOptions = [
  { value: 'line', label: '折线图' },
  { value: 'bar', label: '柱形图' },
  { value: 'horizontalBar', label: '条形图' },
  { value: 'radar', label: '雷达图' },
]
const metricComparisonTitle = computed(() => {
  const option = metricModeOptions.find(item => item.value === metricMode.value)
  return `${props.chart.data?.metric || props.chart.title}${option?.label || '折线图'}`
})
const crosstabModeOptions = [
  { value: 'stackedColumn', label: '堆积柱形图' },
  { value: 'column', label: '柱形图' },
  { value: 'stackedBar', label: '堆积条形图' },
  { value: 'bar', label: '条形图' },
]
const crosstabTitle = computed(() => {
  const option = crosstabModeOptions.find(item => item.value === crosstabMode.value)
  return `${props.chart.title || '交叉图'}${option?.label || ''}`
})
const displayTitle = computed(() => {
  if (isCategoryChart.value) return categoryTitle.value
  if (isCrosstabChart.value) return crosstabTitle.value
  if (isMetricComparisonChart.value) return metricComparisonTitle.value
  return props.chart.title
})

function percentLabel(value) {
  const numberValue = Number(value || 0)
  return `${numberValue.toFixed(1)}%`
}

function chartValueLabel(count, percent) {
  return labelMode.value === 'count' ? String(count || 0) : percentLabel(percent)
}

function crosstabMarkLabel(mark) {
  return chartValueLabel(mark.count, mark.percent)
}

function crosstabLabels(crossData) {
  if (!showDataLabels.value) return []
  return (crossData.marks || []).filter((mark) => {
    if (!mark.count) return false
    if (!crossData.stacked) return mark.w >= 10 && mark.h >= 6
    if (crossData.horizontal) return mark.w >= 24 && mark.h >= 10
    return mark.h >= 14 && mark.w >= 12
  })
}

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
  'toggle-chart-data',
])
</script>
