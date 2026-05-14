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

export function calcNormalityHistogramLayout(data) {
  const layout = calcHistogramLayout(data)
  const curveX = data?.curveX || []
  const curveY = data?.curveY || []
  const maxCurve = Math.max(...curveY, 0)
  const maxCount = Math.max(...(data?.counts || []), 1)
  const maxValue = Math.max(maxCurve, maxCount, 1)
  const valueMin = curveX.length ? Math.min(...curveX) : (data?.binEdges?.[0] ?? 0)
  const valueMax = curveX.length ? Math.max(...curveX) : (data?.binEdges?.[data.binEdges.length - 1] ?? 1)
  const valueSpan = valueMax - valueMin || 1
  const curvePath = curveX.map((value, index) => {
    const x = layout.ml + ((value - valueMin) / valueSpan) * layout.pw
    const y = layout.mt + layout.ph - ((curveY[index] || 0) / maxValue) * layout.ph
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
  const bars = (layout.bars || []).map((bar) => ({
    ...bar,
    y: layout.mt + layout.ph - ((bar.c || 0) / maxValue) * layout.ph,
    h: ((bar.c || 0) / maxValue) * layout.ph,
  }))
  const yTicks = Array.from({ length: 6 }, (_, index) => ({
    y: layout.mt + layout.ph - (index / 5) * layout.ph,
    label: Math.round((index / 5) * maxValue),
  }))
  return { ...layout, bars, yTicks, curvePath }
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

const CATEGORY_COLORS = ['#2389e8', '#45d0bf', '#31c260', '#ffcf1a', '#eb9450', '#7a6ff0', '#f36ca2', '#8bc34a']

function shortLabel(value, maxLength = 10) {
  const text = String(value ?? '')
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

export function calcCategoryBarLayout(data, horizontal = false) {
  const labels = data?.labels || []
  const counts = data?.counts || []
  const percents = data?.percents || []
  const maxPercent = Math.max(...percents, 1)
  if (horizontal) {
    const W = 600, H = 330
    const ml = 96, mr = 72, mt = 22, mb = 46
    const pw = W - ml - mr
    const ph = H - mt - mb
    const rowH = ph / Math.max(labels.length, 1)
    const bars = labels.map((label, index) => {
      const value = percents[index] || 0
      const width = (value / maxPercent) * pw
      return {
        label,
        count: counts[index] || 0,
        percent: value,
        x: ml,
        y: mt + index * rowH + rowH * 0.18,
        w: width,
        h: Math.max(rowH * 0.56, 12),
        labelY: mt + index * rowH + rowH * 0.55,
      }
    })
    const xTicks = Array.from({ length: 6 }, (_, index) => {
      const value = (index / 5) * maxPercent
      return {
        x: ml + (index / 5) * pw,
        label: Math.round(value),
      }
    })
    return { W, H, ml, mr, mt, mb, pw, ph, bars, xTicks, horizontal: true }
  }

  const W = 600, H = 330
  const ml = 58, mr = 36, mt = 26, mb = 60
  const pw = W - ml - mr
  const ph = H - mt - mb
  const bw = pw / Math.max(labels.length, 1)
  const bars = labels.map((label, index) => {
    const value = percents[index] || 0
    const h = (value / maxPercent) * ph
    return {
      label,
      count: counts[index] || 0,
      percent: value,
      x: ml + index * bw + Math.max(bw * 0.18, 4),
      y: mt + ph - h,
      w: Math.max(bw * 0.64, 8),
      h,
      tickX: ml + index * bw + bw / 2,
    }
  })
  const yTicks = Array.from({ length: 6 }, (_, index) => {
    const value = (index / 5) * maxPercent
    return {
      y: mt + ph - (index / 5) * ph,
      label: Math.round(value),
    }
  })
  return { W, H, ml, mr, mt, mb, pw, ph, bars, yTicks, shortLabel, horizontal: false }
}

function polarToCartesian(cx, cy, radius, angle) {
  return {
    x: cx + radius * Math.cos(angle),
    y: cy + radius * Math.sin(angle),
  }
}

function arcPath(cx, cy, radius, startAngle, endAngle) {
  if (endAngle - startAngle >= Math.PI * 2 - 0.0001) {
    const top = polarToCartesian(cx, cy, radius, -Math.PI / 2)
    const bottom = polarToCartesian(cx, cy, radius, Math.PI / 2)
    return `M ${top.x} ${top.y} A ${radius} ${radius} 0 1 1 ${bottom.x} ${bottom.y} A ${radius} ${radius} 0 1 1 ${top.x} ${top.y}`
  }
  const start = polarToCartesian(cx, cy, radius, startAngle)
  const end = polarToCartesian(cx, cy, radius, endAngle)
  const largeArc = endAngle - startAngle > Math.PI ? 1 : 0
  return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y}`
}

export function calcCategoryPieLayout(data, donut = false) {
  const labels = data?.labels || []
  const counts = data?.counts || []
  const percents = data?.percents || []
  const W = 600, H = 330
  const cx = 300, cy = 160, r = 102, innerR = donut ? 48 : 0
  const total = counts.reduce((sum, value) => sum + Number(value || 0), 0) || 1
  let angle = -Math.PI / 2
  const slices = labels.map((label, index) => {
    const count = Number(counts[index] || 0)
    const percent = Number(percents[index] || 0)
    const span = (count / total) * Math.PI * 2
    const startAngle = angle
    const endAngle = angle + span
    angle = endAngle
    const mid = startAngle + span / 2
    const fillPath = `${arcPath(cx, cy, r, startAngle, endAngle)} L ${cx} ${cy} Z`
    const labelPoint = polarToCartesian(cx, cy, r + 28, mid)
    const lineStart = polarToCartesian(cx, cy, r, mid)
    const lineEnd = polarToCartesian(cx, cy, r + 20, mid)
    return {
      label,
      count,
      percent,
      path: fillPath,
      color: CATEGORY_COLORS[index % CATEGORY_COLORS.length],
      lineStart,
      lineEnd,
      labelX: labelPoint.x,
      labelY: labelPoint.y,
      labelAnchor: Math.cos(mid) >= 0 ? 'start' : 'end',
      labelText: `${shortLabel(label, 8)}: ${percent.toFixed(1)}%`,
    }
  }).filter(slice => slice.count > 0)
  return { W, H, cx, cy, r, innerR, slices, donut }
}

export function calcCrosstabLayout(data, mode = 'stackedColumn') {
  const groupLabels = data?.groupLabels || []
  const xLabels = data?.xLabels || []
  const matrix = data?.matrix || []
  const W = 720, H = 360
  const horizontal = mode === 'stackedBar' || mode === 'bar'
  const stacked = mode === 'stackedColumn' || mode === 'stackedBar'
  const percentBase = data?.percentBase === 'row' ? 'row' : 'column'
  const ml = horizontal ? 88 : 62
  const mr = 42
  const mt = 28
  const mb = horizontal ? 64 : 72
  const pw = W - ml - mr
  const ph = H - mt - mb
  const groupTotals = groupLabels.map((_, groupIndex) => (
    matrix.reduce((sum, row) => sum + Number(row[groupIndex] || 0), 0)
  ))
  const rowTotals = xLabels.map((_, rowIndex) => (
    (matrix[rowIndex] || []).reduce((sum, value) => sum + Number(value || 0), 0)
  ))
  const maxCount = Math.max(...matrix.flat().map(value => Number(value || 0)), 1)
  const rowStackMax = groupLabels.reduce((max, _, groupIndex) => {
    const stack = xLabels.reduce((sum, __, seriesIndex) => {
      const count = Number(matrix[seriesIndex]?.[groupIndex] || 0)
      const total = rowTotals[seriesIndex] || 0
      return sum + (total ? count / total * 100 : 0)
    }, 0)
    return Math.max(max, stack)
  }, 1)
  const maxValue = stacked
    ? (percentBase === 'row' ? Math.max(rowStackMax, 1) : 100)
    : maxCount

  function cellPercent(count, groupIndex, seriesIndex) {
    const total = percentBase === 'row'
      ? rowTotals[seriesIndex] || 0
      : groupTotals[groupIndex] || 0
    return total ? count / total * 100 : 0
  }

  const marks = []
  if (horizontal) {
    const rowH = ph / Math.max(groupLabels.length, 1)
    groupLabels.forEach((groupLabel, groupIndex) => {
      if (stacked) {
        let cursor = ml
        xLabels.forEach((seriesLabel, seriesIndex) => {
          const count = Number(matrix[seriesIndex]?.[groupIndex] || 0)
          const percent = cellPercent(count, groupIndex, seriesIndex)
          const width = percent / maxValue * pw
          marks.push({
            groupLabel,
            seriesLabel,
            count,
            percent,
            color: CATEGORY_COLORS[seriesIndex % CATEGORY_COLORS.length],
            x: cursor,
            y: mt + groupIndex * rowH + rowH * 0.18,
            w: width,
            h: Math.max(rowH * 0.58, 12),
            labelX: cursor + width / 2,
            labelY: mt + groupIndex * rowH + rowH * 0.5,
          })
          cursor += width
        })
      } else {
        const barH = Math.max(rowH * 0.68 / Math.max(xLabels.length, 1), 5)
        xLabels.forEach((seriesLabel, seriesIndex) => {
          const count = Number(matrix[seriesIndex]?.[groupIndex] || 0)
          const percent = cellPercent(count, groupIndex, seriesIndex)
          const width = count / maxValue * pw
          marks.push({
            groupLabel,
            seriesLabel,
            count,
            percent,
            color: CATEGORY_COLORS[seriesIndex % CATEGORY_COLORS.length],
            x: ml,
            y: mt + groupIndex * rowH + rowH * 0.16 + seriesIndex * barH,
            w: width,
            h: Math.max(barH - 1, 4),
            labelX: ml + width + 5,
            labelY: mt + groupIndex * rowH + rowH * 0.16 + seriesIndex * barH + barH / 2,
          })
        })
      }
    })
    const xTicks = Array.from({ length: 6 }, (_, index) => ({
      x: ml + index / 5 * pw,
      y: mt + ph - index / 5 * ph,
      label: Math.round(index / 5 * maxValue),
    }))
    return { W, H, ml, mr, mt, mb, pw, ph, marks, xTicks, groupLabels, xLabels, horizontal, stacked }
  }

  const groupW = pw / Math.max(groupLabels.length, 1)
  groupLabels.forEach((groupLabel, groupIndex) => {
    if (stacked) {
      let cursor = mt + ph
      xLabels.forEach((seriesLabel, seriesIndex) => {
        const count = Number(matrix[seriesIndex]?.[groupIndex] || 0)
        const percent = cellPercent(count, groupIndex, seriesIndex)
        const height = percent / maxValue * ph
        marks.push({
          groupLabel,
          seriesLabel,
          count,
          percent,
          color: CATEGORY_COLORS[seriesIndex % CATEGORY_COLORS.length],
          x: ml + groupIndex * groupW + Math.max(groupW * 0.2, 8),
          y: cursor - height,
          w: Math.max(groupW * 0.6, 12),
          h: height,
          labelX: ml + groupIndex * groupW + groupW / 2,
          labelY: cursor - height / 2,
        })
        cursor -= height
      })
    } else {
      const barW = Math.max(groupW * 0.7 / Math.max(xLabels.length, 1), 5)
      xLabels.forEach((seriesLabel, seriesIndex) => {
        const count = Number(matrix[seriesIndex]?.[groupIndex] || 0)
        const percent = cellPercent(count, groupIndex, seriesIndex)
        const height = count / maxValue * ph
        marks.push({
          groupLabel,
          seriesLabel,
          count,
          percent,
          color: CATEGORY_COLORS[seriesIndex % CATEGORY_COLORS.length],
          x: ml + groupIndex * groupW + groupW * 0.15 + seriesIndex * barW,
          y: mt + ph - height,
          w: Math.max(barW - 1, 4),
          h: height,
          labelX: ml + groupIndex * groupW + groupW * 0.15 + seriesIndex * barW + barW / 2,
          labelY: mt + ph - height - 6,
        })
      })
    }
  })
  const yTicks = Array.from({ length: 6 }, (_, index) => ({
    y: mt + ph - index / 5 * ph,
    label: Math.round(index / 5 * maxValue),
  }))
  return { W, H, ml, mr, mt, mb, pw, ph, marks, yTicks, groupLabels, xLabels, horizontal, stacked, shortLabel }
}

export function calcMetricComparisonLayout(data, mode = 'line') {
  const labels = data?.labels || []
  const values = (data?.values || []).map(value => Number(value || 0))
  const metric = data?.metric || '指标'
  const W = 640, H = 340
  const ml = mode === 'horizontalBar' ? 96 : 62
  const mr = 46
  const mt = 30
  const mb = 58
  const pw = W - ml - mr
  const ph = H - mt - mb
  const minV = Math.min(...values, 0)
  const maxV = Math.max(...values, 1)
  const span = maxV - minV || 1
  const pad = Math.max(span * 0.15, 0.1)
  const low = minV - pad
  const high = maxV + pad
  const toY = value => mt + ph * (1 - (value - low) / (high - low || 1))
  const toX = index => ml + (labels.length <= 1 ? pw / 2 : (index / (labels.length - 1)) * pw)
  const yTicks = Array.from({ length: 6 }, (_, index) => {
    const value = low + (index / 5) * (high - low)
    return { y: toY(value), label: Math.abs(value) >= 100 ? Math.round(value) : Number(value.toFixed(2)) }
  })
  const points = labels.map((label, index) => ({
    label,
    value: values[index],
    x: toX(index),
    y: toY(values[index]),
  }))
  if (mode === 'horizontalBar') {
    const rowH = ph / Math.max(labels.length, 1)
    const zeroX = ml + ((0 - low) / (high - low || 1)) * pw
    const bars = labels.map((label, index) => {
      const value = values[index]
      const x = ml + ((Math.min(0, value) - low) / (high - low || 1)) * pw
      const endX = ml + ((Math.max(0, value) - low) / (high - low || 1)) * pw
      return {
        label,
        value,
        x,
        y: mt + index * rowH + rowH * 0.18,
        w: Math.max(endX - x, 1),
        h: Math.max(rowH * 0.56, 12),
        labelY: mt + index * rowH + rowH * 0.55,
      }
    })
    const xTicks = Array.from({ length: 6 }, (_, index) => {
      const value = low + (index / 5) * (high - low)
      return { x: ml + (index / 5) * pw, label: Math.abs(value) >= 100 ? Math.round(value) : Number(value.toFixed(2)) }
    })
    return { W, H, ml, mr, mt, mb, pw, ph, metric, labels, bars, xTicks, zeroX, mode }
  }
  if (mode === 'radar') {
    const cx = W / 2
    const cy = H / 2 - 2
    const r = 112
    const maxAbs = Math.max(...values.map(value => Math.abs(value)), 1)
    const vertices = labels.map((label, index) => {
      const angle = -Math.PI / 2 + (index / Math.max(labels.length, 1)) * Math.PI * 2
      const radius = (Math.abs(values[index]) / maxAbs) * r
      const labelPoint = polarToCartesian(cx, cy, r + 24, angle)
      return {
        label,
        value: values[index],
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
        axisX: cx + r * Math.cos(angle),
        axisY: cy + r * Math.sin(angle),
        labelX: labelPoint.x,
        labelY: labelPoint.y,
        labelAnchor: Math.cos(angle) >= 0 ? 'start' : 'end',
      }
    })
    const polygon = vertices.map(point => `${point.x},${point.y}`).join(' ')
    const rings = [0.25, 0.5, 0.75, 1].map(scale => labels.map((_, index) => {
      const angle = -Math.PI / 2 + (index / Math.max(labels.length, 1)) * Math.PI * 2
      return `${cx + r * scale * Math.cos(angle)},${cy + r * scale * Math.sin(angle)}`
    }).join(' '))
    return { W, H, cx, cy, r, metric, vertices, polygon, rings, mode }
  }
  const bw = pw / Math.max(labels.length, 1)
  const bars = labels.map((label, index) => {
    const value = values[index]
    const y = toY(Math.max(0, value))
    const y0 = toY(0)
    return {
      label,
      value,
      x: ml + index * bw + Math.max(bw * 0.2, 4),
      y,
      w: Math.max(bw * 0.6, 8),
      h: Math.max(y0 - y, 1),
      tickX: ml + index * bw + bw / 2,
    }
  })
  const path = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ')
  if (data?.isPareto && mode === 'bar') {
    const cumulative = (data?.metrics?.['累计百分比'] || []).map(value => Number(value || 0))
    const toParetoY = value => mt + ph * (1 - Math.min(Math.max(value, 0), 100) / 100)
    const paretoPoints = labels.map((label, index) => ({
      label,
      metric: '累计百分比',
      value: cumulative[index] || 0,
      x: ml + index * bw + bw / 2,
      y: toParetoY(cumulative[index] || 0),
    }))
    const paretoPath = paretoPoints.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ')
    const rightTicks = Array.from({ length: 6 }, (_, index) => ({
      y: toParetoY(index * 20),
      label: `${index * 20}%`,
    }))
    return {
      W,
      H,
      ml,
      mr,
      mt,
      mb,
      pw,
      ph,
      metric,
      points,
      bars,
      yTicks,
      rightTicks,
      shortLabel,
      path,
      paretoPath,
      paretoPoints,
      barFill: '#10b981',
      lineFill: '#3b78ff',
      mode,
    }
  }
  return { W, H, ml, mr, mt, mb, pw, ph, metric, points, bars, yTicks, shortLabel, path, mode }
}

export function calcFactorHeatmapLayout(data) {
  const rowLabels = data?.rowLabels || []
  const colLabels = data?.colLabels || []
  const values = data?.values || []
  const cellScale = Math.min(Math.max(Number(data?.cellScale || 1), 0.45), 1.8)
  const cellW = Math.round(118 * cellScale)
  const cellH = Math.round(30 * cellScale)
  const ml = Math.max(96, Math.min(160, Math.max(...rowLabels.map(label => String(label).length), 2) * 10 + 24))
  const mt = 36
  const mr = 24
  const mb = 50
  const W = ml + colLabels.length * cellW + mr
  const H = mt + rowLabels.length * cellH + mb
  const flat = values.flat().map(value => Number(value)).filter(Number.isFinite)
  const maxAbs = Math.max(...flat.map(value => Math.abs(value)), 1)
  const cells = []
  rowLabels.forEach((rowLabel, rowIndex) => {
    colLabels.forEach((colLabel, colIndex) => {
      const rawValue = values[rowIndex]?.[colIndex]
      const value = Number(rawValue)
      const empty = rawValue === null || rawValue === '' || !Number.isFinite(value)
      const intensity = Math.min(Math.abs(value) / maxAbs, 1)
      const hue = value < 0 ? 214 : 0
      const saturation = Math.round(34 + intensity * 32)
      const lightness = Math.round(96 - intensity * 42)
      cells.push({
        rowLabel,
        colLabel,
        value,
        x: ml + colIndex * cellW,
        y: mt + rowIndex * cellH,
        w: cellW,
        h: cellH,
        empty,
        fill: empty ? '#fff' : `hsl(${hue}, ${saturation}%, ${lightness}%)`,
        textFill: intensity > 0.58 ? '#fff' : '#222',
      })
    })
  })
  return { W, H, ml, mt, mb, cellW, cellH, rowLabels, colLabels, cells }
}

export function calcProbabilityPlotLayout(data) {
  const points = data?.points || []
  const W = 520
  const H = 340
  const ml = 58
  const mr = 28
  const mt = 24
  const mb = 56
  const pw = W - ml - mr
  const ph = H - mt - mb
  const xs = points.map(item => Number(item.x || 0))
  const ys = points.map(item => Number(item.y || 0))
  const lineXs = [Number(data?.lineStart?.x || 0), Number(data?.lineEnd?.x || 1)]
  const lineYs = [Number(data?.lineStart?.y || 0), Number(data?.lineEnd?.y || 1)]
  const xMin = Math.min(...xs, ...lineXs)
  const xMax = Math.max(...xs, ...lineXs)
  const yMin = Math.min(...ys, ...lineYs)
  const yMax = Math.max(...ys, ...lineYs)
  const xPad = Math.max((xMax - xMin) * 0.08, 0.1)
  const yPad = Math.max((yMax - yMin) * 0.08, 0.1)
  const plotXMin = xMin - xPad
  const plotXMax = xMax + xPad
  const plotYMin = yMin - yPad
  const plotYMax = yMax + yPad
  const toX = value => ml + ((value - plotXMin) / (plotXMax - plotXMin || 1)) * pw
  const toY = value => mt + ph - ((value - plotYMin) / (plotYMax - plotYMin || 1)) * ph
  const marks = points.map((point) => ({
    x: toX(Number(point.x || 0)),
    y: toY(Number(point.y || 0)),
    rawX: Number(point.x || 0),
    rawY: Number(point.y || 0),
  }))
  const linePath = [
    `M ${toX(lineXs[0])} ${toY(lineYs[0])}`,
    `L ${toX(lineXs[1])} ${toY(lineYs[1])}`,
  ].join(' ')
  const xTicks = Array.from({ length: 6 }, (_, index) => {
    const value = plotXMin + (index / 5) * (plotXMax - plotXMin)
    return { x: toX(value), label: Number(value.toFixed(2)) }
  })
  const yTicks = Array.from({ length: 6 }, (_, index) => {
    const value = plotYMin + (index / 5) * (plotYMax - plotYMin)
    return { y: toY(value), label: Number(value.toFixed(2)) }
  })
  return { W, H, ml, mr, mt, mb, pw, ph, marks, linePath, xTicks, yTicks, xLabel: data?.xLabel || '', yLabel: data?.yLabel || '' }
}

export function calcCorrespondenceMapLayout(data) {
  const points = data?.points || []
  const W = 720
  const H = 390
  const ml = 64
  const mr = 34
  const mt = 32
  const mb = 58
  const pw = W - ml - mr
  const ph = H - mt - mb
  const xs = points.map(point => Number(point.x || 0))
  const ys = points.map(point => Number(point.y || 0))
  const xMaxAbs = Math.max(...xs.map(value => Math.abs(value)), 0.5)
  const yMaxAbs = Math.max(...ys.map(value => Math.abs(value)), 0.5)
  const xLimit = xMaxAbs * 1.18
  const yLimit = yMaxAbs * 1.18
  const xMin = -xLimit
  const xMax = xLimit
  const yMin = -yLimit
  const yMax = yLimit
  const toX = value => ml + ((value - xMin) / (xMax - xMin || 1)) * pw
  const toY = value => mt + ph - ((value - yMin) / (yMax - yMin || 1)) * ph
  const series = data?.series || [...new Set(points.map(point => point.series || '类别'))]
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
  const shapes = ['circle', 'diamond', 'triangle', 'square']
  const marks = points.map((point) => {
    const seriesIndex = Math.max(series.indexOf(point.series), 0)
    return {
      ...point,
      rawX: Number(point.x || 0),
      rawY: Number(point.y || 0),
      x: toX(Number(point.x || 0)),
      y: toY(Number(point.y || 0)),
      color: colors[seriesIndex % colors.length],
      shape: shapes[seriesIndex % shapes.length],
    }
  })
  const xTicks = Array.from({ length: 7 }, (_, index) => {
    const value = xMin + (index / 6) * (xMax - xMin)
    return { x: toX(value), label: Number(value.toFixed(2)) }
  })
  const yTicks = Array.from({ length: 7 }, (_, index) => {
    const value = yMin + (index / 6) * (yMax - yMin)
    return { y: toY(value), label: Number(value.toFixed(2)) }
  })
  const legend = series.map((label, index) => ({
    label,
    color: colors[index % colors.length],
    shape: shapes[index % shapes.length],
  }))
  return {
    W,
    H,
    ml,
    mr,
    mt,
    mb,
    pw,
    ph,
    marks,
    xTicks,
    yTicks,
    zeroX: toX(0),
    zeroY: toY(0),
    xLabel: data?.xLabel || '维度1',
    yLabel: data?.yLabel || '维度2',
    legend,
  }
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
