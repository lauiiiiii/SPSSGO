import { reactive } from 'vue'
import {
  calcBoxplotLayout,
  calcHistogramLayout,
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

  function calcBox(data) {
    return calcBoxplotLayout(data)
  }

  function resetCharts() {
    tip.show = false
    for (const key of Object.keys(chartDataVisible)) delete chartDataVisible[key]
  }

  return {
    calcBox,
    calcHist,
    chartDataVisible,
    copyChart,
    downloadChart,
    fmtBin,
    hideTip,
    moveTip,
    resetCharts,
    setChartRef,
    showBoxTip,
    showHistTip,
    tip,
    toggleChartData,
  }
}
