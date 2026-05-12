<template>
  <div ref="configRoot" class="ap-config">
    <div v-if="editingConfig && results.length" class="ap-report-banner">
      <span>已有本次分析结果，可随时查看完整报告页。</span>
      <button type="button" class="ap-btn ap-btn-primary ap-btn-sm" @click="$emit('show-report')">
        查看分析结果
      </button>
    </div>
    <div class="ap-method-title">
      <span class="ap-method-name">{{ method.label }}</span>
    </div>
    <div class="ap-method-desc">{{ method.description }}</div>
    <template v-if="isCfaMethod">
      <div class="ap-slot-label">
        放入
        <span class="ap-accept-tag accept-numeric">[定量]</span>
        变量
        <span class="ap-slot-constraint">（变量数≥2）</span>
      </div>
      <div class="ap-cfa-board">
        <div class="ap-cfa-sidebar">
          <button type="button" class="ap-factor-btn ap-factor-btn--wide" @click="$emit('add-factor')" :disabled="dynamicFactorCount >= maxDynamicFactors">
            + 新建因子
          </button>
          <div class="ap-cfa-factor-list">
            <button
              v-for="slot in displaySlots"
              :key="slot.key"
              type="button"
              class="ap-cfa-factor-item"
              :class="{ 'is-active': activeFactorKey === slot.key }"
              @click="$emit('select-factor', slot.key)"
            >
              <span class="ap-cfa-factor-name">{{ getFactorShortLabel(slot.key) }}</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-cfa-factor-badge">{{ slotValues[slot.key].length }}</span>
              <span class="ap-cfa-factor-menu-wrap">
                <button type="button" class="ap-cfa-factor-more" @click.stop="$emit('toggle-factor-menu', slot.key)">...</button>
                <div v-if="factorMenuKey === slot.key" class="ap-cfa-factor-menu">
                  <button type="button" class="ap-cfa-factor-menu-item" @click.stop="$emit('rename-factor', slot.key)">
                    重命名
                  </button>
                  <button type="button" class="ap-cfa-factor-menu-item is-danger" @click.stop="$emit('delete-factor', slot.key)" :disabled="dynamicFactorCount <= 1">
                    删除
                  </button>
                </div>
              </span>
            </button>
          </div>
          <div class="ap-factor-tip">点击左侧切换因子，变量会加入当前选中的因子。</div>
        </div>
        <div class="ap-cfa-main">
          <div class="ap-cfa-main-head">
            <span class="ap-cfa-main-title">{{ activeFactorTitle }}</span>
            <span class="ap-cfa-main-sub">{{ activeFactorItems.length }} 个题项</span>
          </div>
          <AnalysisDropZone
            v-if="activeFactorSlot"
            :drag-over-slot="dragOverSlot"
            :empty-text="`将待分析变量拖入到 ${activeFactorTitle}`"
            :get-var-type="getVarType"
            :get-var-type-class="getVarTypeClass"
            :slot="activeFactorSlot"
            :slot-key="activeFactorKey"
            :values="activeFactorItems"
            zone-class="ap-cfa-drop-zone"
            @drag-over="$emit('drag-over', $event)"
            @drag-leave="$emit('drag-leave')"
            @drop-slot="(...args) => $emit('drop-slot', ...args)"
            @remove-var="(...args) => $emit('remove-var', ...args)"
            @zone-click="$emit('close-factor-menu')"
          />
        </div>
      </div>
    </template>

    <div v-else v-for="(slot, slotIndex) in displaySlots" :key="slot.key" class="ap-slot" :class="{ 'ap-slot-grow': slotIndex === displaySlots.length - 1 }">
      <div class="ap-slot-label">
        放入
        <span v-if="slot.prefixLabel">{{ slot.prefixLabel }}</span>
        <span v-if="getAcceptLabel(slot)" class="ap-accept-tag" :class="'accept-' + slot.accept">
          [{{ getAcceptLabel(slot) }}]
        </span>
        {{ slot.label }}
        <span class="ap-slot-constraint">
          （{{ slot.type === 'single' ? '单个变量' : '变量数≥' + (slot.min ?? 1) }}）
        </span>
        <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
      </div>
      <AnalysisDropZone
        :drag-over-slot="dragOverSlot"
        :empty-text="`将待分析变量拖入到此区域${slot.type === 'single' ? '（单个变量）' : ''}`"
        :get-var-type="getVarType"
        :get-var-type-class="getVarTypeClass"
        :slot="slot"
        :slot-key="slot.key"
        :values="slotValues[slot.key] || []"
        @drag-over="$emit('drag-over', $event)"
        @drag-leave="$emit('drag-leave')"
        @drop-slot="(...args) => $emit('drop-slot', ...args)"
        @remove-var="(...args) => $emit('remove-var', ...args)"
      />
    </div>

    <div class="ap-actions">
      <button class="ap-btn ap-btn-ghost" @click="$emit('reset')">重置</button>
      <button class="ap-btn ap-btn-primary" :disabled="!canExecute || executing" @click="$emit('execute')">
        <svg v-if="!executing" width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 2l10 6-10 6V2z" fill="currentColor"/></svg>
        <span v-if="executing" class="spinner-sm"></span>
        {{ executing ? '分析中...' : '开始分析' }}
      </button>
      <div v-if="method.options?.length" class="ap-options ap-options--actions">
        <div v-for="option in method.options" :key="option.key" class="ap-option-group">
          <label v-if="option.type === 'checkbox'" class="ap-option-check">
            <input
              type="checkbox"
              :checked="!!optionValues[option.key]"
              @change="$emit('option-change', option.key, $event.target.checked)"
            />
            <span>{{ option.label }}</span>
          </label>
          <template v-else-if="option.type === 'multiple'">
            <label>{{ option.label }}：</label>
            <details class="ap-option-multi">
              <summary>{{ multiOptionText(option) }}</summary>
              <div class="ap-option-multi-menu">
                <label
                  v-for="choice in option.choices"
                  :key="choice"
                  class="ap-option-multi-item"
                >
                  <input
                    type="checkbox"
                    :checked="multiOptionValues(option.key).includes(choice)"
                    @change="toggleMultiOption(option, choice)"
                  />
                  <span>{{ choice }}</span>
                </label>
              </div>
            </details>
          </template>
          <template v-else>
            <label>{{ option.label }}：</label>
            <select :value="optionValues[option.key]" @change="$emit('option-change', option.key, $event.target.value)">
            <option v-for="choice in optionChoices(option)" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
            </select>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AnalysisDropZone from './AnalysisDropZone.vue'

const configRoot = ref(null)

const props = defineProps({
  activeFactorItems: { type: Array, default: () => [] },
  activeFactorKey: { type: String, default: '' },
  activeFactorSlot: { type: Object, default: null },
  activeFactorTitle: { type: String, default: '' },
  canExecute: { type: Boolean, default: false },
  displaySlots: { type: Array, default: () => [] },
  dragOverSlot: { type: String, default: null },
  dynamicFactorCount: { type: Number, default: 1 },
  editingConfig: { type: Boolean, default: false },
  executing: { type: Boolean, default: false },
  factorMenuKey: { type: String, default: null },
  getFactorShortLabel: { type: Function, required: true },
  getVarType: { type: Function, required: true },
  getVarTypeClass: { type: Function, required: true },
  isCfaMethod: { type: Boolean, default: false },
  maxDynamicFactors: { type: Number, default: 12 },
  method: { type: Object, required: true },
  optionValues: { type: Object, required: true },
  results: { type: Array, default: () => [] },
  slotValues: { type: Object, required: true },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'add-factor',
  'close-factor-menu',
  'delete-factor',
  'drag-leave',
  'drag-over',
  'drop-slot',
  'execute',
  'option-change',
  'remove-var',
  'rename-factor',
  'reset',
  'select-factor',
  'show-report',
  'toggle-factor-menu',
])

function getAcceptLabel(slot) {
  if (slot.acceptLabel) return slot.acceptLabel
  if (!slot.accept || slot.accept === 'any') return ''
  if (slot.accept === 'numeric') return '定量'
  if (slot.accept === 'categorical') return '定类'
  return slot.accept
}

function multiOptionValues(key) {
  const value = props.optionValues[key]
  return Array.isArray(value) ? value : [value].filter(Boolean)
}

function multiOptionText(option) {
  const values = multiOptionValues(option.key)
  return values.length ? values.join('、') : '请选择'
}

function optionChoices(option) {
  if (option.type !== 'factor_count') {
    return (option.choices || []).map(choice => ({ value: choice, label: choice }))
  }
  const selectedCount = Array.isArray(props.slotValues.variables) ? props.slotValues.variables.length : 0
  const numericCount = props.variables.filter(variable => variable?.type === 'numeric').length
  const max = Math.max(selectedCount, numericCount)
  const choices = [{ value: 'auto', label: '自动抽取' }]
  for (let index = 1; index <= max; index += 1) {
    choices.push({ value: String(index), label: String(index) })
  }
  return choices
}

function toggleMultiOption(option, choice) {
  const values = multiOptionValues(option.key)
  const next = values.includes(choice)
    ? values.filter(item => item !== choice)
    : [...values, choice]
  emit('option-change', option.key, next.length ? next : [option.choices[0]])
}

function closeMultiOptions() {
  configRoot.value
    ?.querySelectorAll('.ap-option-multi[open]')
    .forEach(el => {
      el.open = false
    })
}

function handleDocumentPointerDown(event) {
  if (event.target?.closest?.('.ap-option-multi')) return
  closeMultiOptions()
}

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
})
</script>
