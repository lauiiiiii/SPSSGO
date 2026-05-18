<template>
  <div class="ap-chart-item">
    <div class="ap-chart-caption">{{ displayTitle }}</div>
    <div v-if="supportsDataLabels || hasMetricSwitcher" class="ap-chart-label-toolbar">
      <select
        v-if="hasMetricSwitcher"
        v-model="selectedMetric"
        class="ap-chart-label-select"
        title="切换统计量"
      >
        <option v-for="label in metricOptions" :key="label" :value="label">{{ label }}</option>
      </select>
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
    <div
      class="ap-chart-wrap"
      :ref="el => setChartRef(sectionIndex, chartIndex, el)"
      :style="chartWrapStyle"
    >
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
      <template v-else-if="chart.chartType === 'normality_histogram'">
        <template v-for="histogramData in [calcNormalityHist(chart.data)]" :key="0">
          <svg class="ap-chart-svg ap-chart-svg--normality" :viewBox="`0 0 ${histogramData.W} ${histogramData.H}`" :width="histogramData.W" :height="histogramData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="histogramData.ml" :y="histogramData.mt" :width="histogramData.pw" :height="histogramData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in histogramData.yTicks" :key="'nyg'+tickIndex"
              :x1="histogramData.ml" :y1="tick.y" :x2="histogramData.ml+histogramData.pw" :y2="tick.y"
              stroke="#efefef" stroke-width="1"/>
            <rect v-for="(bar, barIndex) in histogramData.bars" :key="barIndex"
              :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h"
              fill="#3b82f6" rx="1"
              style="cursor:pointer"
              @mouseenter="$emit('show-hist-tip', $event, chart.data, barIndex)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <text v-for="(bar, barIndex) in histogramData.bars" :key="'nhv'+barIndex"
              :x="bar.x + bar.w / 2" :y="Math.max(bar.y - 6, 12)" text-anchor="middle" font-size="11" fill="#333">{{ bar.c }}</text>
            <path :d="histogramData.curvePath" fill="none" stroke="#10b981" stroke-width="2"/>
            <line :x1="histogramData.ml" :y1="histogramData.mt+histogramData.ph" :x2="histogramData.ml+histogramData.pw" :y2="histogramData.mt+histogramData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="histogramData.ml" :y1="histogramData.mt" :x2="histogramData.ml" :y2="histogramData.mt+histogramData.ph" stroke="#bbb" stroke-width="1"/>
            <text v-for="(tick, tickIndex) in histogramData.xTicks" :key="'nxl'+tickIndex"
              :x="tick.x" :y="histogramData.mt+histogramData.ph+16" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            <text v-for="(tick, tickIndex) in histogramData.yTicks" :key="'nyl'+tickIndex"
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
      <template v-else-if="chart.chartType === 'pp_plot' || chart.chartType === 'qq_plot'">
        <template v-for="plotData in [calcProbabilityPlot(chart.data)]" :key="0">
          <svg class="ap-chart-svg ap-chart-svg--normality" :viewBox="`0 0 ${plotData.W} ${plotData.H}`" :width="plotData.W" :height="plotData.H"
            @mouseleave="$emit('hide-tip')">
            <rect :x="plotData.ml" :y="plotData.mt" :width="plotData.pw" :height="plotData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in plotData.yTicks" :key="'pyg'+tickIndex"
              :x1="plotData.ml" :y1="tick.y" :x2="plotData.ml+plotData.pw" :y2="tick.y"
              stroke="#efefef" stroke-width="1"/>
            <line v-for="(tick, tickIndex) in plotData.xTicks" :key="'pxg'+tickIndex"
              :x1="tick.x" :y1="plotData.mt" :x2="tick.x" :y2="plotData.mt+plotData.ph"
              stroke="#f5f5f5" stroke-width="1"/>
            <path :d="plotData.linePath" fill="none" stroke="#10b981" stroke-width="2"/>
            <circle v-for="(point, pointIndex) in plotData.marks" :key="'pp'+pointIndex"
              :cx="point.x" :cy="point.y" r="2.4" fill="#7aa5ff"
              style="cursor:pointer"
              @mouseenter="$emit('show-probability-tip', $event, chart, point)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"/>
            <text v-for="(point, pointIndex) in plotData.marks" :key="'ppt'+pointIndex"
              v-show="pointIndex === 0 || pointIndex === plotData.marks.length - 1 || pointIndex === Math.floor(plotData.marks.length / 2)"
              :x="point.x + 5" :y="point.y - 4" text-anchor="start" font-size="10" fill="#666">{{ Number(point.rawY).toFixed(2) }}</text>
            <line :x1="plotData.ml" :y1="plotData.mt+plotData.ph" :x2="plotData.ml+plotData.pw" :y2="plotData.mt+plotData.ph" stroke="#bbb" stroke-width="1"/>
            <line :x1="plotData.ml" :y1="plotData.mt" :x2="plotData.ml" :y2="plotData.mt+plotData.ph" stroke="#bbb" stroke-width="1"/>
            <text v-for="(tick, tickIndex) in plotData.xTicks" :key="'pxt'+tickIndex"
              :x="tick.x" :y="plotData.mt+plotData.ph+18" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            <text v-for="(tick, tickIndex) in plotData.yTicks" :key="'pyt'+tickIndex"
              :x="plotData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            <text :x="plotData.ml+plotData.pw/2" :y="plotData.H-10" text-anchor="middle" font-size="11" fill="#777">{{ plotData.xLabel }}</text>
            <text :x="13" :y="plotData.mt+plotData.ph/2" text-anchor="middle" font-size="11" fill="#aaa"
              :transform="`rotate(-90,13,${plotData.mt+plotData.ph/2})`">{{ plotData.yLabel }}</text>
          </svg>
        </template>
      </template>
      <template v-else-if="isCorrespondenceMap">
        <template v-for="mapData in [calcCorrespondenceMap(chart.data)]" :key="0">
          <svg class="ap-chart-svg ap-chart-svg--correspondence" :viewBox="`0 0 ${mapData.W} ${mapData.H}`" :width="mapData.W" :height="mapData.H">
            <rect :x="mapData.ml" :y="mapData.mt" :width="mapData.pw" :height="mapData.ph" fill="white"/>
            <line v-for="(tick, tickIndex) in mapData.xTicks" :key="'cxg'+tickIndex"
              :x1="tick.x" :y1="mapData.mt" :x2="tick.x" :y2="mapData.mt+mapData.ph" stroke="#f2f4f7" stroke-width="1"/>
            <line v-for="(tick, tickIndex) in mapData.yTicks" :key="'cyg'+tickIndex"
              :x1="mapData.ml" :y1="tick.y" :x2="mapData.ml+mapData.pw" :y2="tick.y" stroke="#f2f4f7" stroke-width="1"/>
            <line :x1="mapData.ml" :y1="mapData.zeroY" :x2="mapData.ml+mapData.pw" :y2="mapData.zeroY" stroke="#111827" stroke-width="1"/>
            <line :x1="mapData.zeroX" :y1="mapData.mt" :x2="mapData.zeroX" :y2="mapData.mt+mapData.ph" stroke="#111827" stroke-width="1"/>
            <g v-for="(mark, markIndex) in mapData.marks" :key="'cam'+markIndex">
              <circle
                v-if="mark.shape === 'circle'"
                :cx="mark.x"
                :cy="mark.y"
                r="4.5"
                :fill="mark.color"
              />
              <rect
                v-else-if="mark.shape === 'square'"
                :x="mark.x - 4"
                :y="mark.y - 4"
                width="8"
                height="8"
                :fill="mark.color"
              />
              <path
                v-else-if="mark.shape === 'triangle'"
                :d="`M ${mark.x} ${mark.y - 5} L ${mark.x - 5} ${mark.y + 4} L ${mark.x + 5} ${mark.y + 4} Z`"
                :fill="mark.color"
              />
              <rect
                v-else
                :x="mark.x - 4"
                :y="mark.y - 4"
                width="8"
                height="8"
                :fill="mark.color"
                :transform="`rotate(45 ${mark.x} ${mark.y})`"
              />
              <text :x="mark.x + 7" :y="mark.y - 6" font-size="11" :fill="mark.color">{{ mark.label }}</text>
            </g>
            <text v-for="(tick, tickIndex) in mapData.xTicks" :key="'cax'+tickIndex"
              :x="tick.x" :y="mapData.mt+mapData.ph+18" text-anchor="middle" font-size="11" fill="#888">{{ tick.label }}</text>
            <text v-for="(tick, tickIndex) in mapData.yTicks" :key="'cay'+tickIndex"
              :x="mapData.ml-8" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
            <text :x="mapData.ml+mapData.pw/2" :y="mapData.H-14" text-anchor="middle" font-size="12" fill="#555">{{ mapData.xLabel }}</text>
            <text :x="18" :y="mapData.mt+mapData.ph/2" text-anchor="middle" font-size="12" fill="#555"
              :transform="`rotate(-90,18,${mapData.mt+mapData.ph/2})`">{{ mapData.yLabel }}</text>
            <g v-for="(item, itemIndex) in mapData.legend" :key="'cal'+itemIndex" :transform="`translate(${mapData.ml + itemIndex * 132}, ${mapData.H - 34})`">
              <circle cx="0" cy="0" r="4.5" :fill="item.color"/>
              <text x="12" y="4" font-size="12" fill="#555">{{ item.label }}</text>
            </g>
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
      <template v-else-if="isKanoBetterWorseChart">
        <template v-for="plotData in [calcKanoBetterWorse(chart.data)]" :key="0">
          <svg
            class="ap-chart-svg ap-chart-svg--kano-bw"
            :viewBox="`0 0 ${plotData.W} ${plotData.H}`"
            :width="plotData.W"
            :height="plotData.H"
            @mouseleave="$emit('hide-tip')"
          >
            <defs>
              <linearGradient id="kanoBwBg" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stop-color="#f8fbff"/>
                <stop offset="100%" stop-color="#ffffff"/>
              </linearGradient>
              <filter id="kanoBwShadow" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#0f172a" flood-opacity=".16"/>
              </filter>
            </defs>
            <rect :x="plotData.ml" :y="plotData.mt" :width="plotData.pw" :height="plotData.ph" fill="url(#kanoBwBg)" stroke="#cbd5e1" stroke-width="1.2"/>
            <rect :x="plotData.ml" :y="plotData.mt" :width="plotData.meanX - plotData.ml" :height="plotData.meanY - plotData.mt" fill="#eaf5ff" opacity=".42"/>
            <rect :x="plotData.meanX" :y="plotData.mt" :width="plotData.ml + plotData.pw - plotData.meanX" :height="plotData.meanY - plotData.mt" fill="#ecfdf5" opacity=".38"/>
            <rect :x="plotData.ml" :y="plotData.meanY" :width="plotData.meanX - plotData.ml" :height="plotData.mt + plotData.ph - plotData.meanY" fill="#f8fafc" opacity=".7"/>
            <rect :x="plotData.meanX" :y="plotData.meanY" :width="plotData.ml + plotData.pw - plotData.meanX" :height="plotData.mt + plotData.ph - plotData.meanY" fill="#fff7ed" opacity=".38"/>
            <line
              v-for="(tick, tickIndex) in plotData.xTicks"
              :key="'kxg'+tickIndex"
              :x1="tick.x"
              :y1="plotData.mt"
              :x2="tick.x"
              :y2="plotData.mt + plotData.ph"
              stroke="#eef1f5"
              stroke-width="1"
            />
            <line
              v-for="(tick, tickIndex) in plotData.yTicks"
              :key="'kyg'+tickIndex"
              :x1="plotData.ml"
              :y1="tick.y"
              :x2="plotData.ml + plotData.pw"
              :y2="tick.y"
              stroke="#eef1f5"
              stroke-width="1"
            />
            <line :x1="plotData.meanX" :y1="plotData.mt" :x2="plotData.meanX" :y2="plotData.mt + plotData.ph" stroke="#334155" stroke-width="1.2" stroke-dasharray="4 4"/>
            <line :x1="plotData.ml" :y1="plotData.meanY" :x2="plotData.ml + plotData.pw" :y2="plotData.meanY" stroke="#334155" stroke-width="1.2" stroke-dasharray="4 4"/>
            <text :x="plotData.meanX + 6" :y="plotData.mt + 16" font-size="11" font-style="italic" fill="#9a5a00">{{ plotData.xMeanLabel }}</text>
            <text :x="plotData.ml + plotData.pw - 8" :y="plotData.meanY - 7" text-anchor="end" font-size="11" font-style="italic" fill="#9a5a00">{{ plotData.yMeanLabel }}</text>
            <text
              v-for="quadrant in plotData.quadrants"
              :key="quadrant.label"
              :x="quadrant.x"
              :y="quadrant.y"
              text-anchor="middle"
              font-size="13"
              font-weight="600"
              :fill="quadrant.color"
              opacity=".42"
            >{{ quadrant.label }}</text>
            <circle
              v-for="(point, pointIndex) in plotData.points"
              :key="'kpt'+pointIndex"
              class="ap-kano-bw-point"
              :cx="point.x"
              :cy="point.y"
              r="4.8"
              :fill="point.color"
              stroke="#fff"
              stroke-width="1.4"
              filter="url(#kanoBwShadow)"
              @mouseenter="$emit('show-metric-tip', $event, chart, point)"
              @mousemove="$emit('move-tip', $event)"
              @mouseleave="$emit('hide-tip')"
            />
            <rect
              v-for="(point, pointIndex) in plotData.points"
              :key="'kpb'+pointIndex"
              :x="point.boxX"
              :y="point.boxY"
              :width="point.boxW"
              height="16"
              rx="3"
              fill="white"
              opacity=".82"
            />
            <text
              v-for="(point, pointIndex) in plotData.points"
              :key="'kpl'+pointIndex"
              :x="point.labelX"
              :y="point.labelY"
              :text-anchor="point.labelAnchor"
              font-size="11"
              fill="#003a75"
            >{{ point.label }}</text>
            <line :x1="plotData.ml" :y1="plotData.mt + plotData.ph" :x2="plotData.ml + plotData.pw" :y2="plotData.mt + plotData.ph" stroke="#64748b" stroke-width="1.2"/>
            <line :x1="plotData.ml" :y1="plotData.mt" :x2="plotData.ml" :y2="plotData.mt + plotData.ph" stroke="#64748b" stroke-width="1.2"/>
            <text
              v-for="(tick, tickIndex) in plotData.xTicks"
              :key="'kxt'+tickIndex"
              :x="tick.x"
              :y="plotData.mt + plotData.ph + 20"
              text-anchor="middle"
              font-size="11"
              fill="#345"
            >{{ tick.label }}</text>
            <text
              v-for="(tick, tickIndex) in plotData.yTicks"
              :key="'kyt'+tickIndex"
              :x="plotData.ml - 8"
              :y="tick.y + 4"
              text-anchor="end"
              font-size="11"
              fill="#345"
            >{{ tick.label }}</text>
            <text :x="plotData.ml + plotData.pw / 2" :y="plotData.H - 20" text-anchor="middle" font-size="12" fill="#003a75">{{ plotData.xLabel }}</text>
            <text
              :x="22"
              :y="plotData.mt + plotData.ph / 2"
              text-anchor="middle"
              font-size="12"
              fill="#003a75"
              :transform="`rotate(-90,22,${plotData.mt + plotData.ph / 2})`"
            >{{ plotData.yLabel }}</text>
          </svg>
        </template>
      </template>
      <template v-else-if="isMetricComparisonChart">
        <template v-for="metricData in [calcMetricComparison(metricChartData, metricMode)]" :key="metricMode">
          <svg
            class="ap-chart-svg ap-chart-svg--metric"
            :viewBox="`0 0 ${metricData.W} ${metricData.H}`"
            :width="Math.round(metricData.W * metricChartZoom)"
            :height="Math.round(metricData.H * metricChartZoom)"
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
              <text v-for="(bar, barIndex) in metricData.bars" :key="'mhv'+barIndex"
                v-show="showDataLabels"
                :x="bar.x + bar.w + 5" :y="bar.labelY + 4" text-anchor="start" font-size="11" fill="#333">{{ metricValueLabel(bar.value) }}</text>
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
                  :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" :fill="metricData.barFill || '#2389e8'" rx="2"
                  @mouseenter="$emit('show-metric-tip', $event, chart, bar)"
                  @mousemove="$emit('move-tip', $event)"
                  @mouseleave="$emit('hide-tip')"/>
                <text v-for="(bar, barIndex) in metricData.bars" :key="'mbv'+barIndex"
                  v-show="showDataLabels"
                  :x="bar.x + bar.w / 2" :y="Math.max(bar.y - 6, 12)" text-anchor="middle" font-size="11" fill="#333">{{ metricValueLabel(bar.value) }}</text>
                <path v-if="metricData.paretoPath" :d="metricData.paretoPath" fill="none" :stroke="metricData.lineFill || '#3b78ff'" stroke-width="2"/>
                <circle v-for="(point, pointIndex) in metricData.paretoPoints || []" :key="'pareto'+pointIndex"
                  class="ap-metric-mark"
                  :cx="point.x" :cy="point.y" r="3.5" :fill="metricData.lineFill || '#3b78ff'"
                  @mouseenter="$emit('show-metric-tip', $event, chart, point)"
                  @mousemove="$emit('move-tip', $event)"
                  @mouseleave="$emit('hide-tip')"/>
                <text v-for="(point, pointIndex) in metricData.paretoPoints || []" :key="'paretov'+pointIndex"
                  v-show="showDataLabels"
                  :x="point.x" :y="Math.max(point.y - 10, 12)" text-anchor="middle" font-size="11" fill="#333">{{ percentLabel(point.value) }}</text>
              </template>
              <template v-else>
                <template v-if="metricData.multiSeries">
                  <path v-for="(series, seriesIndex) in metricData.series" :key="'msline'+seriesIndex"
                    :d="series.path" fill="none" :stroke="series.color" stroke-width="2" :stroke-dasharray="series.dash"/>
                  <circle v-for="(point, pointIndex) in multiMetricPoints(metricData)" :key="'msp'+pointIndex"
                    class="ap-metric-mark"
                    :cx="point.x" :cy="point.y" r="3.4" :fill="point.color"
                    @mouseenter="$emit('show-metric-tip', $event, chart, point)"
                    @mousemove="$emit('move-tip', $event)"
                    @mouseleave="$emit('hide-tip')"/>
                  <text v-for="(point, pointIndex) in multiMetricPoints(metricData)" :key="'mspv'+pointIndex"
                    v-show="showDataLabels"
                    :x="point.x" :y="Math.max(point.y - 9, 12)" text-anchor="middle" font-size="10" :fill="point.color">{{ metricValueLabel(point.value) }}</text>
                  <rect v-for="(hit, hitIndex) in metricData.hitAreas" :key="'mshit'+hitIndex"
                    :x="hit.rectX" :y="metricData.mt" :width="hit.rectW" :height="metricData.ph"
                    fill="transparent"
                    @mouseenter="$emit('show-metric-tip', $event, chart, hit)"
                    @mousemove="$emit('move-tip', $event)"
                    @mouseleave="$emit('hide-tip')"/>
                  <line v-for="(hit, hitIndex) in metricData.hitAreas" :key="'msvx'+hitIndex"
                    :x1="hit.x" :y1="metricData.mt" :x2="hit.x" :y2="metricData.mt+metricData.ph"
                    stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 3" opacity=".28"/>
                  <g v-for="(legend, legendIndex) in metricData.legend" :key="'mslg'+legendIndex">
                    <line :x1="legend.x" :y1="legend.y" :x2="legend.x + 18" :y2="legend.y" :stroke="legend.color" stroke-width="2" :stroke-dasharray="legend.dash"/>
                    <circle :cx="legend.x + 9" :cy="legend.y" r="3" :fill="legend.color"/>
                    <text :x="legend.x + 24" :y="legend.y + 4" font-size="11" fill="#333">{{ legend.name }}</text>
                  </g>
                </template>
                <template v-else>
                  <path :d="metricData.path" fill="none" stroke="#2389e8" stroke-width="2"/>
                  <circle v-for="(point, pointIndex) in metricData.points" :key="'mp'+pointIndex"
                    class="ap-metric-mark"
                    :cx="point.x" :cy="point.y" r="4" fill="#2389e8"
                    @mouseenter="$emit('show-metric-tip', $event, chart, point)"
                    @mousemove="$emit('move-tip', $event)"
                    @mouseleave="$emit('hide-tip')"/>
                  <text v-for="(point, pointIndex) in metricData.points" :key="'mpv'+pointIndex"
                    v-show="showDataLabels"
                    :x="point.x" :y="Math.max(point.y - 10, 12)" text-anchor="middle" font-size="11" fill="#333">{{ metricValueLabel(point.value) }}</text>
                </template>
              </template>
              <line :x1="metricData.ml" :y1="metricData.mt+metricData.ph" :x2="metricData.ml+metricData.pw" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <line :x1="metricData.ml" :y1="metricData.mt" :x2="metricData.ml" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
              <text v-for="(point, pointIndex) in metricData.points" :key="'mx'+pointIndex"
                :x="point.x" :y="metricData.mt+metricData.ph+18" text-anchor="middle" font-size="11" fill="#666">{{ metricData.shortLabel(point.label) }}</text>
              <text v-for="(tick, tickIndex) in metricData.yTicks" :key="'my'+tickIndex"
                :x="metricData.ml-6" :y="tick.y+4" text-anchor="end" font-size="11" fill="#888">{{ tick.label }}</text>
              <template v-if="metricData.rightTicks">
                <line :x1="metricData.ml+metricData.pw" :y1="metricData.mt" :x2="metricData.ml+metricData.pw" :y2="metricData.mt+metricData.ph" stroke="#bbb" stroke-width="1"/>
                <text v-for="(tick, tickIndex) in metricData.rightTicks" :key="'mry'+tickIndex"
                  :x="metricData.ml+metricData.pw+8" :y="tick.y+4" text-anchor="start" font-size="11" fill="#888">{{ tick.label }}</text>
              </template>
            </template>
          </svg>
        </template>
      </template>
      <template v-else-if="isHeatmapChart">
        <template v-for="heatmapData in [calcFactorHeatmap(activeHeatmapData)]" :key="0">
          <svg class="ap-chart-svg ap-chart-svg--heatmap" :viewBox="`0 0 ${heatmapData.W} ${heatmapData.H}`" :width="heatmapData.W" :height="heatmapData.H">
            <rect x="0" y="0" :width="heatmapData.W" :height="heatmapData.H" fill="white"/>
            <text
              v-for="(label, labelIndex) in heatmapData.colLabels"
              :key="'hc'+labelIndex"
              :x="heatmapData.ml + labelIndex * heatmapData.cellW + heatmapData.cellW / 2"
              :y="22"
              text-anchor="middle"
              font-size="12"
              fill="#555"
            >{{ label }}</text>
            <text
              v-for="(label, labelIndex) in heatmapData.rowLabels"
              :key="'hr'+labelIndex"
              :x="heatmapData.ml - 10"
              :y="heatmapData.mt + labelIndex * heatmapData.cellH + heatmapData.cellH / 2 + 4"
              text-anchor="end"
              font-size="12"
              fill="#555"
            >{{ label }}</text>
            <g v-for="(cell, cellIndex) in heatmapData.cells" :key="'hm'+cellIndex">
              <rect :x="cell.x" :y="cell.y" :width="cell.w" :height="cell.h" :fill="cell.fill" stroke="rgba(255,255,255,.55)" stroke-width="1"/>
              <text v-if="!cell.empty" :x="cell.x + cell.w / 2" :y="cell.y + cell.h / 2 + 4" text-anchor="middle" font-size="12" :fill="cell.textFill">{{ Number(cell.value).toFixed(3) }}</text>
            </g>
            <text :x="heatmapData.ml + heatmapData.colLabels.length * heatmapData.cellW / 2" :y="heatmapData.H - 16" text-anchor="middle" font-size="11" fill="#777">颜色越深表示绝对值越大</text>
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
    <div v-if="isHeatmapChart && heatmapModeOptions.length" class="ap-chart-mode-bar">
      <button
        v-for="option in heatmapModeOptions"
        :key="option.value"
        class="ap-chart-mode-btn"
        :class="{ 'is-active': heatmapMode === option.value }"
        @click="heatmapMode = option.value"
      >
        {{ option.label }}
      </button>
    </div>
    <div class="ap-chart-actions">
      <label v-if="isKanoBetterWorseChart" class="ap-chart-size-control">
        <span>缩放：</span>
        <input
          v-model.number="kanoChartZoom"
          type="range"
          min="0.75"
          max="1.6"
          step="0.05"
        />
      </label>
      <label v-if="isHeatmapChart" class="ap-chart-size-control">
        <span>尺寸：</span>
        <input
          v-model.number="heatmapSize"
          type="range"
          min="0.45"
          max="1.6"
          step="0.05"
        />
      </label>
      <label v-if="isMetricComparisonChart" class="ap-chart-size-control">
        <span>尺寸：</span>
        <input
          v-model.number="metricChartZoom"
          type="range"
          min="0.7"
          max="1.8"
          step="0.05"
        />
      </label>
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
    <div v-if="dataVisible && isKanoBetterWorseChart" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>功能/服务</th><th>Better</th><th>Worse绝对值</th></tr></thead>
        <tbody>
          <tr v-for="(label, rowIndex) in chart.data.labels" :key="rowIndex">
            <td>{{ label }}</td>
            <td>{{ Number(chart.data.better?.[rowIndex] || 0).toFixed(3) }}</td>
            <td>{{ Number(chart.data.worseAbs?.[rowIndex] || 0).toFixed(3) }}</td>
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
    <div v-if="dataVisible && isHeatmapChart" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>名称</th><th v-for="label in chart.data.colLabels" :key="label">{{ label }}</th></tr></thead>
        <tbody>
          <tr v-for="(label, rowIndex) in chart.data.rowLabels" :key="label">
            <td>{{ label }}</td>
            <td v-for="(_, colIndex) in chart.data.colLabels" :key="colIndex">{{ Number(chart.data.values[rowIndex]?.[colIndex] || 0).toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="dataVisible && chart.chartType === 'normality_histogram'" class="ap-chart-data-table">
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
    <div v-if="dataVisible && (chart.chartType === 'pp_plot' || chart.chartType === 'qq_plot')" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>{{ chart.data.xLabel }}</th><th>{{ chart.data.yLabel }}</th></tr></thead>
        <tbody>
          <tr v-for="(point, pointIndex) in chart.data.points" :key="pointIndex">
            <td>{{ Number(point.x).toFixed(3) }}</td>
            <td>{{ Number(point.y).toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="dataVisible && isCorrespondenceMap" class="ap-chart-data-table">
      <table class="tlt tlt--sm">
        <thead><tr><th>类别</th><th>字段</th><th>维度1</th><th>维度2</th></tr></thead>
        <tbody>
          <tr v-for="(point, pointIndex) in chart.data.points" :key="pointIndex">
            <td>{{ point.label }}</td>
            <td>{{ point.series }}</td>
            <td>{{ Number(point.x || 0).toFixed(3) }}</td>
            <td>{{ Number(point.y || 0).toFixed(3) }}</td>
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
  calcCorrespondenceMap: { type: Function, required: true },
  calcCrosstab: { type: Function, required: true },
  calcFactorHeatmap: { type: Function, required: true },
  calcHist: { type: Function, required: true },
  calcMetricComparison: { type: Function, required: true },
  calcNormalityHist: { type: Function, required: true },
  calcProbabilityPlot: { type: Function, required: true },
  chart: { type: Object, required: true },
  chartIndex: { type: Number, required: true },
  dataVisible: { type: Boolean, default: false },
  fmtBin: { type: Function, required: true },
  sectionIndex: { type: Number, required: true },
  setChartRef: { type: Function, required: true },
})

const categoryChartTypes = new Set(['category_distribution', 'category', 'categorical', 'categorical_distribution', 'frequency'])
const categoryMode = ref(props.chart.data?.defaultMode || 'bar')
const crosstabMode = ref(props.chart.data?.defaultMode || 'stackedColumn')
const heatmapSize = ref(1)
const kanoChartZoom = ref(1)
const metricChartZoom = ref(props.chart.data?.multiSeries ? 1.15 : 1)
const labelMode = ref(props.chart.data?.defaultLabelMode || 'percent')
const metricMode = ref(props.chart.data?.defaultMode || 'bar')
const showDataLabels = ref(true)
const selectedMetric = ref(props.chart.data?.metric || '')
const categoryModeOptions = [
  { value: 'bar', label: '柱状图' },
  { value: 'horizontalBar', label: '条形图' },
  { value: 'pie', label: '饼图' },
  { value: 'donut', label: '环形图' },
]
const isCategoryChart = computed(() => categoryChartTypes.has(props.chart.chartType))
const isCorrespondenceMap = computed(() => props.chart.chartType === 'correspondence_map')
const isCrosstabChart = computed(() => props.chart.chartType === 'crosstab_distribution')
const isHeatmapChart = computed(() => ['factor_loading_heatmap', 'correlation_heatmap'].includes(props.chart.chartType))
const isKanoBetterWorseChart = computed(() => props.chart.chartType === 'kano_better_worse')
const isMetricComparisonChart = computed(() => props.chart.chartType === 'metric_comparison')
const supportsDataLabels = computed(() => (
  isCrosstabChart.value
  || isMetricComparisonChart.value
  || (isCategoryChart.value && ['bar', 'horizontalBar'].includes(categoryMode.value))
))
const supportsLabelMode = computed(() => (
  isCrosstabChart.value
  || (isCategoryChart.value && ['bar', 'horizontalBar'].includes(categoryMode.value))
))
const hasMetricSwitcher = computed(() => (
  isMetricComparisonChart.value
  && !props.chart.data?.multiSeries
  && props.chart.data?.metrics
  && Object.keys(props.chart.data.metrics).length > 1
))
const metricOptions = computed(() => (
  hasMetricSwitcher.value ? Object.keys(props.chart.data.metrics) : []
))
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
const metricChartData = computed(() => {
  const data = props.chart.data
  if (!hasMetricSwitcher.value || !selectedMetric.value) return data
  const values = data.metrics?.[selectedMetric.value]
  if (!values) return data
  return {
    ...data,
    metric: selectedMetric.value,
    values,
  }
})
const heatmapModeOptions = computed(() => (
  (props.chart.data?.displayModes || []).map(mode => ({ value: mode.key, label: mode.label || mode.key }))
))
const heatmapMode = ref(props.chart.data?.defaultDisplayMode || heatmapModeOptions.value[0]?.value || '')
const activeHeatmapData = computed(() => {
  const data = props.chart.data || {}
  const mode = (data.displayModes || []).find(item => item.key === heatmapMode.value)
  if (!mode) return { ...data, cellScale: heatmapSize.value }
  return {
    ...data,
    ...mode,
    cellScale: heatmapSize.value,
    displayModes: data.displayModes,
    defaultDisplayMode: data.defaultDisplayMode,
  }
})
const chartWrapStyle = computed(() => {
  if (isMetricComparisonChart.value) {
    const baseWidth = props.chart.data?.multiSeries ? 760 : 640
    const baseHeight = props.chart.data?.multiSeries ? 390 : 340
    return {
      width: `${Math.round(baseWidth * metricChartZoom.value)}px`,
      height: `${Math.round(baseHeight * metricChartZoom.value)}px`,
    }
  }
  if (!isKanoBetterWorseChart.value) return {}
  return {
    width: `${Math.round(760 * kanoChartZoom.value)}px`,
    height: `${Math.round(420 * kanoChartZoom.value)}px`,
  }
})
const metricComparisonTitle = computed(() => {
  const option = metricModeOptions.find(item => item.value === metricMode.value)
  const data = metricChartData.value
  if (data?.displayTitle) return data.displayTitle
  return `${data?.metric || props.chart.title}${option?.label || '柱形图'}`
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
  if (isKanoBetterWorseChart.value) return props.chart.title || 'Better-Worse系数图'
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

function metricValueLabel(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return ''
  if (Math.abs(num) >= 100) return String(Math.round(num))
  return Number(num.toFixed(2)).toString()
}

function multiMetricPoints(metricData) {
  return (metricData.series || []).flatMap(series => series.points || [])
}

function chartMean(values) {
  const nums = values.map(value => Number(value)).filter(Number.isFinite)
  if (!nums.length) return 0
  return nums.reduce((sum, value) => sum + value, 0) / nums.length
}

function compactNumber(value) {
  const num = Number(value || 0)
  if (Math.abs(num) >= 10) return num.toFixed(2).replace(/\.?0+$/, '')
  return num.toFixed(2).replace(/\.?0+$/, '')
}

function chartTicks(maxValue, mapValue) {
  const steps = 5
  return Array.from({ length: steps + 1 }, (_, index) => {
    const value = (maxValue / steps) * index
    return {
      label: compactNumber(value),
      x: mapValue(value),
      y: mapValue(value),
    }
  })
}

function labelBox(point) {
  const width = Math.max(42, String(point.label || '').length * 6.3 + 8)
  const x = point.labelAnchor === 'end' ? point.labelX - width + 3 : point.labelX - 3
  return {
    ...point,
    boxX: x,
    boxY: point.labelY - 12,
    boxW: width,
  }
}

function spreadKanoLabels(points, mt, ph) {
  const minY = mt + 14
  const maxY = mt + ph - 8
  const groups = [
    points.filter(point => point.labelAnchor !== 'end'),
    points.filter(point => point.labelAnchor === 'end'),
  ]
  groups.forEach((group) => {
    group.sort((a, b) => a.labelY - b.labelY)
    group.forEach((point, index) => {
      if (index === 0) {
        point.labelY = Math.max(point.labelY, minY)
      } else {
        point.labelY = Math.max(point.labelY, group[index - 1].labelY + 15)
      }
    })
    for (let index = group.length - 1; index >= 0; index -= 1) {
      const next = group[index + 1]
      pointBound(group[index], next, maxY)
    }
  })
  return points.map(labelBox)
}

function pointBound(point, next, maxY) {
  point.labelY = Math.min(point.labelY, next ? next.labelY - 15 : maxY)
}

function calcKanoBetterWorse(data = {}) {
  const labels = data.labels || []
  const better = (data.better || []).map(value => Number(value || 0))
  const worseAbs = (data.worseAbs || data.worse || []).map(value => Math.abs(Number(value || 0)))
  const W = 760
  const H = 420
  const ml = 76
  const mt = 34
  const mr = 54
  const mb = 62
  const pw = W - ml - mr
  const ph = H - mt - mb
  const maxX = Math.max(1, ...worseAbs)
  const maxY = Math.max(1, ...better)
  const xMax = maxX * 1.12
  const yMax = maxY * 1.12
  const xMean = Number.isFinite(Number(data.xMean)) ? Number(data.xMean) : chartMean(worseAbs)
  const yMean = Number.isFinite(Number(data.yMean)) ? Number(data.yMean) : chartMean(better)
  const toX = value => ml + (Number(value || 0) / xMax) * pw
  const toY = value => mt + ph - (Number(value || 0) / yMax) * ph
  const meanX = toX(xMean)
  const meanY = toY(yMean)
  const pointPalette = ['#2389e8', '#16a34a', '#f97316', '#7c3aed', '#dc2626', '#0891b2']
  const points = labels.map((label, index) => {
    const xValue = worseAbs[index] || 0
    const yValue = better[index] || 0
    const x = toX(xValue)
    const y = toY(yValue)
    const nearRight = x > ml + pw - 110
    const nearLeft = x < ml + 24
    const nearTop = y < mt + 20
    return {
      label,
      metric: 'Better',
      value: yValue,
      better: yValue,
      worseAbs: xValue,
      x,
      y,
      color: pointPalette[index % pointPalette.length],
      labelX: nearRight ? x - 8 : x + (nearLeft ? 10 : 8),
      labelY: nearTop ? y + 16 : y - 8,
      labelAnchor: nearRight ? 'end' : 'start',
    }
  })
  return {
    W,
    H,
    ml,
    mt,
    pw,
    ph,
    meanX,
    meanY,
    xLabel: data.xLabel || 'Worse绝对值',
    yLabel: data.yLabel || 'Better',
    xMeanLabel: compactNumber(xMean),
    yMeanLabel: compactNumber(yMean),
    xTicks: chartTicks(xMax, toX),
    yTicks: chartTicks(yMax, toY),
    points: spreadKanoLabels(points, mt, ph),
    quadrants: [
      {
        label: '魅力属性',
        x: ml + (meanX - ml) / 2,
        y: mt + (meanY - mt) / 2,
        color: '#2563eb',
      },
      {
        label: '期望属性',
        x: meanX + (ml + pw - meanX) / 2,
        y: mt + (meanY - mt) / 2,
        color: '#059669',
      },
      {
        label: '无差异属性',
        x: ml + (meanX - ml) / 2,
        y: meanY + (mt + ph - meanY) / 2,
        color: '#64748b',
      },
      {
        label: '必备属性',
        x: meanX + (ml + pw - meanX) / 2,
        y: meanY + (mt + ph - meanY) / 2,
        color: '#ea580c',
      },
    ],
  }
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
  'show-probability-tip',
  'toggle-chart-data',
])
</script>
