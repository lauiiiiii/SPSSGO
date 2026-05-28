<template>
  <div class="ap-sec ap-sec--prediction">
    <div class="ap-sec-head">
      <span class="ap-sec-head-title">{{ section.title || '模型结果预测' }}</span>
    </div>
    <div class="ap-table-wrap ap-prediction-table-wrap">
      <table class="tlt tlt--prediction">
        <thead>
          <tr>
            <th>变量</th>
            <th>系数</th>
            <th>测试值</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>常数</td>
            <td>{{ formatNumber(section.intercept ?? section.defaultPrediction) }}</td>
            <td>1</td>
          </tr>
          <tr v-for="input in inputs" :key="input.key">
            <td>{{ input.label }}</td>
            <td>{{ formatNumber(inputCoefficient(input)) }}</td>
            <td>
              <label class="ap-prediction-cell-field">
                <span class="sr-only">{{ input.label }}</span>
                <input
                  v-if="input.type === 'numeric'"
                  v-model.number="inputValues[input.key]"
                  class="ap-prediction-input"
                  type="number"
                  step="any"
                />
                <select
                  v-else
                  v-model="inputValues[input.key]"
                  class="ap-prediction-input"
                >
                  <option
                    v-for="option in input.options || []"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>
            </td>
          </tr>
          <tr class="ap-prediction-total-row">
            <td colspan="2">预测结果 -</td>
            <td>{{ formatNumber(predictedValue) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="section.equation" class="ap-prediction-equation">{{ section.equation }}</div>
    <div v-if="predictionSummary" class="ap-prediction-live">
      <div class="ap-prediction-live-title">当前解读：</div>
      <div class="ap-prediction-live-headline">{{ predictionSummary.headline }}</div>
      <div class="ap-prediction-live-points">
        <div
          v-for="point in predictionSummary.points"
          :key="point.label"
          class="ap-prediction-live-point"
        >
          <span class="ap-prediction-live-label">{{ point.label }}</span>
          <span class="ap-prediction-live-text">{{ point.text }}</span>
        </div>
      </div>
    </div>
    <div v-if="predictionDescription" class="ap-sec-desc">{{ predictionDescription }}</div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { describeRegressionPredictionSection } from '../../utils/analysisCharts.js'

const props = defineProps({
  section: { type: Object, required: true },
})

const inputValues = reactive({})
const inputs = computed(() => props.section.inputs || [])
const predictionDescription = computed(() => describeRegressionPredictionSection(props.section))

const contributionRows = computed(() => {
  const intercept = Number(props.section.intercept ?? props.section.defaultPrediction ?? 0)
  const rows = [{
    type: 'intercept',
    label: '常数项',
    valueLabel: '1',
    coefficient: Number.isFinite(intercept) ? intercept : 0,
    contribution: Number.isFinite(intercept) ? intercept : 0,
  }]
  for (const input of inputs.value) {
    if (input.type === 'numeric') {
      const value = Number(inputValues[input.key] ?? input.defaultValue ?? 0)
      const safeValue = Number.isFinite(value) ? value : 0
      const coefficient = Number(input.coefficient || 0)
      rows.push({
        type: 'numeric',
        label: input.label,
        value: safeValue,
        valueLabel: formatNumber(safeValue),
        coefficient,
        contribution: safeValue * coefficient,
      })
      continue
    }
    const selected = inputValues[input.key] ?? input.defaultValue
    const option = (input.options || []).find(item => item.value === selected)
    const coefficient = Number(option?.coefficient || 0)
    rows.push({
      type: 'categorical',
      label: input.label,
      valueLabel: option?.label ?? selected ?? '—',
      coefficient,
      contribution: coefficient,
    })
  }
  return rows
})

const predictedValue = computed(() => {
  const intercept = Number(props.section.intercept ?? props.section.defaultPrediction ?? 0)
  return inputs.value.reduce((sum, input) => {
    if (input.type === 'numeric') {
      const value = Number(inputValues[input.key] ?? input.defaultValue ?? 0)
      const coefficient = Number(input.coefficient || 0)
      return sum + (Number.isFinite(value) ? value : 0) * coefficient
    }
    return sum + inputCoefficient(input)
  }, Number.isFinite(intercept) ? intercept : 0)
})

const predictionSummary = computed(() => {
  const dependent = props.section.dependent || '因变量'
  const predicted = Number(predictedValue.value)
  if (!Number.isFinite(predicted)) return null
  const inputText = currentInputText()
  const points = [
    {
      label: '当前条件',
      text: inputText ? `你现在代入的是：${inputText}。` : '当前没有可调自变量，预测值主要来自常数项。',
    },
    {
      label: '怎么读',
      text: `预测值就是模型按公式算出来的“预计得分”，它能帮你看趋势和模拟情况，但不能当成确定结论。这里的 ${formatNumber(predicted)} 是 ${dependent} 的预测值，按 ${dependent} 原来的单位或量表来读；它不是概率、不是显著性，也不是“真实答案”。${predictedScaleText(predicted, dependent)}`,
    },
    {
      label: '为什么是这个数',
      text: `它是把常数项和各变量贡献加起来得到的：${contributionText()}。`,
    },
    {
      label: '调数字怎么看',
      text: directionText(dependent),
    },
  ]
  const warning = rangeWarning()
  if (warning) points.push({ label: '注意', text: warning })
  return {
    headline: `按当前输入，模型估计 ${dependent} 大约是 ${formatNumber(predicted)}。`,
    points,
  }
})

watch(
  inputs,
  (nextInputs) => {
    for (const input of nextInputs) {
      inputValues[input.key] = input.defaultValue ?? (input.type === 'numeric' ? 0 : input.options?.[0]?.value)
    }
  },
  { immediate: true },
)

function inputCoefficient(input) {
  if (input.type === 'numeric') return Number(input.coefficient || 0)
  const selected = inputValues[input.key] ?? input.defaultValue
  const option = (input.options || []).find(item => item.value === selected)
  return Number(option?.coefficient || 0)
}

function formatNumber(value) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return '—'
  return numberValue.toFixed(3)
}

function signedNumber(value) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return '—'
  return `${numberValue >= 0 ? '+' : ''}${numberValue.toFixed(3)}`
}

function currentInputText() {
  return contributionRows.value
    .filter(row => row.type !== 'intercept')
    .map(row => `${row.label}=${row.valueLabel}`)
    .join('、')
}

function contributionText() {
  const parts = contributionRows.value.map(row => {
    if (row.type === 'intercept') return `常数项 ${formatNumber(row.contribution)}`
    if (row.type === 'numeric') {
      return `${row.label}: ${formatNumber(row.value)}×${formatNumber(row.coefficient)}=${signedNumber(row.contribution)}`
    }
    return `${row.label}=${row.valueLabel}: ${signedNumber(row.contribution)}`
  })
  return `${parts.join('，')}，合计 ${formatNumber(predictedValue.value)}`
}

function directionText(dependent) {
  const texts = inputs.value.map(input => {
    if (input.type === 'numeric') {
      const coefficient = Number(input.coefficient || 0)
      if (Math.abs(coefficient) < 0.005) return `${input.label} 每增加 1，${dependent} 基本不变`
      const action = coefficient > 0 ? '增加' : '减少'
      return `${input.label} 每增加 1，${dependent} 约${action} ${formatNumber(Math.abs(coefficient))}`
    }
    const selected = inputValues[input.key] ?? input.defaultValue
    const option = (input.options || []).find(item => item.value === selected)
    const coefficient = Number(option?.coefficient || 0)
    if (Math.abs(coefficient) < 0.005) return `${input.label} 当前类别相对参考类别几乎不改变预测值`
    const action = coefficient > 0 ? '高' : '低'
    return `${input.label} 选为 ${option?.label ?? selected ?? '当前类别'} 时，${dependent} 比参考类别约${action} ${formatNumber(Math.abs(coefficient))}`
  })
  return texts.length ? `${texts.join('；')}。所以你改测试值时，预测值会按这些系数同步上升或下降。` : '当前没有可调自变量。'
}

function predictedScaleText(value, dependent) {
  if (value >= 1 && value <= 5) {
    let level = '中等'
    if (value < 1.8) level = '很低'
    else if (value < 2.6) level = '偏低'
    else if (value < 3.4) level = '中等'
    else if (value < 4.2) level = '偏高'
    else level = '很高'
    return `如果 ${dependent} 是 1-5 分题，这个值大致属于${level}水平。`
  }
  return `如果 ${dependent} 是 1-5 分题，这个值已经超出 1-5 的常见范围，需要谨慎解释。`
}

function rangeWarning() {
  const outOfRangeRows = contributionRows.value
    .filter(row => row.type === 'numeric' && (row.value < 1 || row.value > 5))
  if (!outOfRangeRows.length) return ''
  const names = outOfRangeRows.map(row => `${row.label}=${row.valueLabel}`).join('、')
  return `如果这些变量是 1-5 分问卷题，${names} 已经超出常见取值范围；这种结果更像“假设推演”，不建议当作稳定预测结论。`
}
</script>
