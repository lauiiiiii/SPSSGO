export function formatBin(value) {
  if (value == null) return ''
  return Number.isInteger(value) ? value : parseFloat(value.toFixed(4))
}

export function calcHistogramLayout(data) {
  const { binEdges, counts } = data
  const W = 460, H = 230
  const ml = 50, mr = 20, mt = 16, mb = 44
  const pw = W - ml - mr
  const ph = H - mt - mb
  const maxC = Math.max(...counts, 1)
  const n = counts.length
  const bw = pw / n
  const bars = counts.map((count, index) => ({
    x: ml + index * bw + 1.5,
    y: mt + ph - (count / maxC) * ph,
    w: Math.max(bw - 3, 2),
    h: (count / maxC) * ph,
    c: count,
  }))
  const maxLabels = 8
  const step = Math.max(1, Math.ceil(binEdges.length / maxLabels))
  const xTicks = binEdges
    .map((edge, index) => ({ edge, index }))
    .filter(({ index }) => index % step === 0 || index === binEdges.length - 1)
    .map(({ edge, index }) => ({
      x: ml + (index / (binEdges.length - 1)) * pw,
      label: Math.abs(edge) >= 1000 ? Math.round(edge) : (Number.isInteger(edge) ? edge : parseFloat(edge.toFixed(2))),
    }))
  const ySteps = 5
  const yTicks = Array.from({ length: ySteps + 1 }, (_, index) => ({
    y: mt + ph - (index / ySteps) * ph,
    label: Math.round((index / ySteps) * maxC),
  }))
  return { W, H, ml, mr, mt, mb, pw, ph, bars, xTicks, yTicks }
}

export function calcBoxplotLayout(data) {
  const { whiskerLow, q1, median, q3, whiskerHigh, outliers } = data
  const W = 240, H = 300
  const ml = 46, mr = 20, mt = 20, mb = 40
  const ph = H - mt - mb
  const cx = ml + (W - ml - mr) / 2
  const bw = 26

  const allVals = [whiskerLow, q1, median, q3, whiskerHigh, ...(outliers || [])]
  const vmin = Math.min(...allVals)
  const vmax = Math.max(...allVals)
  const pad = Math.max((vmax - vmin) * 0.15, 0.5)
  const dmin = vmin - pad
  const dmax = vmax + pad
  const dr = dmax - dmin || 1

  const toY = value => mt + ph * (1 - (value - dmin) / dr)
  const yQ1 = toY(q1)
  const yQ3 = toY(q3)
  const yMed = toY(median)
  const yWL = toY(whiskerLow)
  const yWH = toY(whiskerHigh)
  const outlierPts = (outliers || []).map(value => ({ y: toY(value) }))

  const yTicks = Array.from({ length: 6 }, (_, index) => {
    const value = dmin + (index / 5) * dr
    return {
      y: toY(value),
      label: Math.abs(value) >= 100 ? Math.round(value) : parseFloat(value.toFixed(1)),
    }
  })

  return { W, H, ml, mt, ph, cx, bw, yQ1, yQ3, yMed, yWL, yWH, outlierPts, yTicks }
}

export function svgToCanvas(svgEl) {
  return new Promise((resolve) => {
    const svgData = new XMLSerializer().serializeToString(svgEl)
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const image = new Image()
    const dpr = window.devicePixelRatio || 2
    image.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = image.naturalWidth * dpr
      canvas.height = image.naturalHeight * dpr
      const ctx = canvas.getContext('2d')
      ctx.scale(dpr, dpr)
      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, image.naturalWidth, image.naturalHeight)
      ctx.drawImage(image, 0, 0)
      URL.revokeObjectURL(url)
      resolve(canvas)
    }
    image.src = url
  })
}

export async function downloadChartPng(svgEl, title) {
  if (!svgEl) return
  const canvas = await svgToCanvas(svgEl)
  const link = document.createElement('a')
  link.download = `${title || 'chart'}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

export async function copyChartPng(svgEl) {
  if (!svgEl) return
  const canvas = await svgToCanvas(svgEl)
  canvas.toBlob(async (blob) => {
    if (!blob) return
    await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
  }, 'image/png')
}
