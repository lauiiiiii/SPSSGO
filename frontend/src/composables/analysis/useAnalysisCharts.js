import { reactive } from 'vue'
import {
  calcBoxplotLayout,
  calcGroupedBoxplotLayout,
  calcCategoryBarLayout,
  calcCategoryPieLayout,
  calcCorrespondenceMapLayout,
  calcCrosstabLayout,
  calcFactorHeatmapLayout,
  calcHistogramLayout,
  calcMetricComparisonLayout,
  calcNormalityHistogramLayout,
  calcProbabilityPlotLayout,
  calcScatterPlotLayout,
  copyChartPng,
  downloadChartPng,
  formatBin,
} from '../../utils/analysisCharts.js'

export function useAnalysisCharts() {
  const chartDataVisible = reactive({})
  const chartRefs = {}
  const tip = reactive({ show: false, x: 0, y: 0, lines: [] })

  function setChartRef(sectionIndex, chartIndex, el) {
    chartRefs[sectionIndex + '_' + chartIndex] = el
  }

  function fmtBin(value) {
    return formatBin(value)
  }

  function moveTip(event) {
    tip.x = event.clientX + 12
    tip.y = event.clientY - 10
  }

  function hideTip() {
    tip.show = false
  }

  function toggleChartData(sectionIndex, chartIndex) {
    const key = sectionIndex + '_' + chartIndex
    chartDataVisible[key] = !chartDataVisible[key]
  }

  function showHistTip(event, data, binIndex) {
    const lo = fmtBin(data.binEdges[binIndex])
    const hi = fmtBin(data.binEdges[binIndex + 1])
    tip.lines = [
      { text: `${lo}-${hi}`, dot: null },
      { text: `${data.counts[binIndex]}`, dot: '#5b8ff9' },
    ]
    moveTip(event)
    tip.show = true
  }

  function showBoxTip(event, chart) {
    const data = chart.data
    tip.lines = [
      { text: chart.varName || chart.title.replace('箱型图', ''), dot: null },
      { text: `极小值：${data.whiskerLow}`, dot: '#5b8ff9' },
      { text: `25%分位数：${data.q1}`, dot: '#5b8ff9' },
      { text: `中位数：${data.median}`, dot: '#5b8ff9' },
      { text: `75%分位数：${data.q3}`, dot: '#5b8ff9' },
      { text: `极大值：${data.whiskerHigh}`, dot: '#5b8ff9' },
    ]
    if (data.outliers?.length) {
      tip.lines.push({ text: `最大值：${Math.max(...data.outliers, data.whiskerHigh)}`, dot: '#52c41a' })
      tip.lines.push({ text: `最小值：${Math.min(...data.outliers, data.whiskerLow)}`, dot: '#52c41a' })
    }
    moveTip(event)
    tip.show = true
  }

  function showCategoryTip(event, chart, dataPoint) {
    tip.lines = [
      { text: chart.varName || chart.data?.variable || chart.title, dot: null },
      { text: `选项：${dataPoint.label}`, dot: '#2389e8' },
      { text: `频数：${dataPoint.count}`, dot: '#2389e8' },
      { text: `百分比：${Number(dataPoint.percent || 0).toFixed(1)}%`, dot: '#2389e8' },
    ]
    moveTip(event)
    tip.show = true
  }

  function showMetricTip(event, chart, dataPoint) {
    if (Array.isArray(dataPoint.seriesItems)) {
      tip.lines = [
        { text: dataPoint.label || chart.title || '指标对比', dot: null },
        ...dataPoint.seriesItems.map(item => ({
          text: `${item.label}：${Number(item.value || 0).toFixed(3)}`,
          dot: item.color || '#2389e8',
        })),
      ]
      moveTip(event)
      tip.show = true
      return
    }
    const metric = dataPoint.metric || chart.data?.metric || '指标'
    if (dataPoint.ciLow != null || dataPoint.ciHigh != null) {
      const fmt = value => {
        const num = Number(value)
        return Number.isFinite(num) ? num.toFixed(3) : '—'
      }
      tip.lines = [
        { text: chart.title || '回归系数95% CI', dot: null },
        { text: `项：${dataPoint.label}`, dot: '#1687d9' },
        { text: `${metric}：${fmt(dataPoint.value)}`, dot: '#1687d9' },
        { text: `95% CI：[${fmt(dataPoint.ciLow)}, ${fmt(dataPoint.ciHigh)}]`, dot: '#111827' },
      ]
      moveTip(event)
      tip.show = true
      return
    }
    tip.lines = [
      { text: chart.title || `${metric}对比图`, dot: null },
      { text: `名称：${dataPoint.label}`, dot: '#2389e8' },
      { text: `${metric}：${Number(dataPoint.value || 0).toFixed(3)}`, dot: '#2389e8' },
    ]
    moveTip(event)
    tip.show = true
  }

  function showProbabilityTip(event, chart, dataPoint) {
    const xLabel = chart.data?.xLabel || 'X'
    const yLabel = chart.data?.yLabel || 'Y'
    tip.lines = [
      { text: chart.title || chart.varName || '概率图', dot: null },
      { text: `${xLabel}：${Number(dataPoint.rawX || 0).toFixed(3)}`, dot: '#10b981' },
      { text: `${yLabel}：${Number(dataPoint.rawY || 0).toFixed(3)}`, dot: '#7aa5ff' },
    ]
    moveTip(event)
    tip.show = true
  }

  async function downloadChart(sectionIndex, chartIndex, title) {
    const svg = getChartSvg(sectionIndex, chartIndex)
    if (!svg) return
    await downloadChartPng(svg, title)
  }

  async function copyChart(sectionIndex, chartIndex) {
    const svg = getChartSvg(sectionIndex, chartIndex)
    if (!svg) return
    try {
      await copyChartPng(svg)
    } catch { /* ignore */ }
  }

  function getChartSvg(sectionIndex, chartIndex) {
    const wrap = chartRefs[sectionIndex + '_' + chartIndex]
    return wrap?.querySelector('svg') || null
  }

  function calcHist(data) {
    return calcHistogramLayout(data)
  }

  function calcNormalityHist(data) {
    return calcNormalityHistogramLayout(data)
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

  function calcCrosstab(data, mode = 'stackedColumn') {
    return calcCrosstabLayout(data, mode)
  }

  function calcProbabilityPlot(data) {
    return calcProbabilityPlotLayout(data)
  }

  function calcCorrespondenceMap(data) {
    return calcCorrespondenceMapLayout(data)
  }

  function calcScatterPlot(data) {
    return calcScatterPlotLayout(data)
  }

  function showScatterTip(event, chart, dataPoint) {
    tip.lines = [
      { text: chart.title || '散点图', dot: null },
      { text: `${chart.data?.xLabel || 'X'}：${Number(dataPoint.rawX || 0).toFixed(3)}`, dot: '#2389e8' },
      { text: `${chart.data?.yLabel || 'Y'}：${Number(dataPoint.rawY || 0).toFixed(3)}`, dot: '#10b981' },
    ]
    moveTip(event)
    tip.show = true
  }

  function showCrosstabTip(event, chart, dataPoint) {
    tip.lines = [
      { text: chart.title || '交叉图', dot: null },
      { text: `分组：${dataPoint.groupLabel}`, dot: dataPoint.color },
      { text: `名称：${dataPoint.seriesLabel}`, dot: dataPoint.color },
      { text: `频数：${dataPoint.count}`, dot: dataPoint.color },
      { text: `百分比：${Number(dataPoint.percent || 0).toFixed(2)}%`, dot: dataPoint.color },
    ]
    moveTip(event)
    tip.show = true
  }

  function resetCharts() {
    tip.show = false
    for (const key of Object.keys(chartDataVisible)) delete chartDataVisible[key]
  }

  return {
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
    resetCharts,
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
  }
}
