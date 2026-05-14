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
    <template v-if="isSummaryTMethod">
      <div class="ap-summary-t-card">
        <div class="ap-summary-t-tabs">
          <button
            type="button"
            :class="{ 'is-active': optionValues.test_type !== 'independent' }"
            @click="$emit('option-change', 'test_type', 'one_sample')"
          >
            单样本T检验
          </button>
          <button
            type="button"
            :class="{ 'is-active': optionValues.test_type === 'independent' }"
            @click="$emit('option-change', 'test_type', 'independent')"
          >
            独立样本T检验
          </button>
        </div>

        <div v-if="optionValues.test_type === 'independent'" class="ap-summary-t-form ap-summary-t-form--two">
          <div class="ap-summary-t-head"></div>
          <div class="ap-summary-t-head">第1组</div>
          <div class="ap-summary-t-head">第2组</div>

          <label>平均值</label>
          <input type="number" step="any" :value="optionValues.group1_mean" placeholder="请输入" @input="$emit('option-change', 'group1_mean', $event.target.value)" />
          <input type="number" step="any" :value="optionValues.group2_mean" placeholder="请输入" @input="$emit('option-change', 'group2_mean', $event.target.value)" />

          <label>标准差</label>
          <input type="number" step="any" min="0" :value="optionValues.group1_std" placeholder="请输入" @input="$emit('option-change', 'group1_std', $event.target.value)" />
          <input type="number" step="any" min="0" :value="optionValues.group2_std" placeholder="请输入" @input="$emit('option-change', 'group2_std', $event.target.value)" />

          <label>样本量</label>
          <input type="number" step="1" min="2" :value="optionValues.group1_n" placeholder="请输入" @input="$emit('option-change', 'group1_n', $event.target.value)" />
          <input type="number" step="1" min="2" :value="optionValues.group2_n" placeholder="请输入" @input="$emit('option-change', 'group2_n', $event.target.value)" />

          <label>差值对比</label>
          <input class="ap-summary-t-wide" type="number" step="any" :value="optionValues.diff_test_value" placeholder="默认0" @input="$emit('option-change', 'diff_test_value', $event.target.value)" />

          <label>置信水平</label>
          <select class="ap-summary-t-wide" :value="optionValues.confidence_level" @change="$emit('option-change', 'confidence_level', $event.target.value)">
            <option value="90">90%</option>
            <option value="95">95%</option>
            <option value="99">99%</option>
          </select>

          <label>假设检验</label>
          <select class="ap-summary-t-wide" :value="optionValues.alternative" @change="$emit('option-change', 'alternative', $event.target.value)">
            <option value="等于">等于</option>
            <option value="大于">大于</option>
            <option value="小于">小于</option>
          </select>
        </div>

        <div v-else class="ap-summary-t-form">
          <label>平均值</label>
          <input type="number" step="any" :value="optionValues.mean" placeholder="请输入" @input="$emit('option-change', 'mean', $event.target.value)" />

          <label>标准差</label>
          <input type="number" step="any" min="0" :value="optionValues.std" placeholder="请输入" @input="$emit('option-change', 'std', $event.target.value)" />

          <label>样本量</label>
          <input type="number" step="1" min="2" :value="optionValues.n" placeholder="请输入" @input="$emit('option-change', 'n', $event.target.value)" />

          <label>对比均值</label>
          <input type="number" step="any" :value="optionValues.test_value" placeholder="默认0" @input="$emit('option-change', 'test_value', $event.target.value)" />

          <label>置信水平</label>
          <select :value="optionValues.confidence_level" @change="$emit('option-change', 'confidence_level', $event.target.value)">
            <option value="90">90%</option>
            <option value="95">95%</option>
            <option value="99">99%</option>
          </select>

          <label>假设检验</label>
          <select :value="optionValues.alternative" @change="$emit('option-change', 'alternative', $event.target.value)">
            <option value="等于">等于</option>
            <option value="大于">大于</option>
            <option value="小于">小于</option>
          </select>
        </div>
      </div>
    </template>
    <template v-else-if="isCfaMethod">
      <div class="ap-slot-label">
        放入
        <span class="ap-accept-tag accept-numeric">[定量]</span>
        变量
        <span class="ap-slot-constraint">（变量数≥2）</span>
      </div>
      <div class="ap-cfa-board" :class="{ 'ap-cfa-board--with-second-order': optionValues.second_order_model }">
        <div class="ap-cfa-sidebar">
          <button type="button" class="ap-factor-btn ap-factor-btn--wide" @click="$emit('add-factor')" :disabled="dynamicFactorCount >= maxDynamicFactors">
            {{ dynamicGroupAddText }}
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
          <div class="ap-factor-tip">{{ dynamicGroupTip }}</div>
        </div>
        <div class="ap-cfa-main">
          <div class="ap-cfa-main-head">
            <label class="ap-cfa-title-edit">
              <input
                ref="titleInputRef"
                class="ap-cfa-title-input"
                :value="activeFactorTitle"
                @change="$emit('rename-factor-inline', activeFactorKey, $event.target.value)"
              />
              <span class="ap-cfa-title-edit-btn" title="重命名">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </span>
            </label>
            <span class="ap-cfa-main-sub">{{ activeFactorItems.length }} 个{{ dynamicGroupItemName }}</span>
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
      <div v-if="optionValues.second_order_model" class="ap-slot-label ap-second-order-label">
        归属
        <span class="ap-accept-tag accept-numeric">[一阶因子]</span>
        因子
        <span class="ap-slot-constraint">（因子数≥2）</span>
      </div>
      <div v-if="optionValues.second_order_model" class="ap-cfa-board ap-second-order-board">
        <div class="ap-cfa-sidebar ap-second-order-sidebar">
          <button type="button" class="ap-factor-btn ap-factor-btn--wide" @click="$emit('add-second-order-model')" :disabled="secondOrderModels.length >= maxSecondOrderModels">
            + 新建模型
          </button>
          <div class="ap-cfa-factor-list">
            <button
              v-for="model in secondOrderModels"
              :key="model.key"
              type="button"
              class="ap-cfa-factor-item"
              :class="{ 'is-active': activeSecondOrderKey === model.key }"
              @click="$emit('select-second-order-model', model.key)"
            >
              <span class="ap-cfa-factor-name">{{ model.label }}</span>
              <span class="ap-cfa-factor-badge">{{ model.members.length }}</span>
              <span class="ap-cfa-factor-menu-wrap">
                <button
                  type="button"
                  class="ap-cfa-factor-more"
                  @click.stop="$emit('delete-second-order-model', model.key)"
                  :disabled="secondOrderModels.length <= 1"
                >
                  ×
                </button>
              </span>
            </button>
          </div>
          <div class="ap-factor-tip">点击右侧一阶因子，将其加入或移出当前二阶模型。</div>
        </div>
        <div class="ap-cfa-main">
          <div class="ap-cfa-main-head">
            <label class="ap-cfa-title-edit">
              <input
                class="ap-cfa-title-input"
                :value="activeSecondOrderFactorName"
                @change="$emit('rename-second-order-factor', $event.target.value)"
              />
              <span class="ap-cfa-title-edit-btn" title="重命名">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </span>
            </label>
            <span class="ap-cfa-main-sub">{{ activeSecondOrderMembers.length }} 个一阶因子</span>
          </div>
          <div class="ap-second-order-drop-zone">
            <button
              v-for="factor in secondOrderFactorChoices"
              :key="factor.key"
              type="button"
              class="ap-second-order-factor-row"
              :class="{ 'is-included': activeSecondOrderMembers.includes(factor.key), 'is-disabled': factor.disabled }"
              :disabled="factor.disabled"
              @click="$emit('toggle-second-order-member', factor.key)"
            >
              <span class="ap-second-order-check">
                <svg v-if="activeSecondOrderMembers.includes(factor.key)" width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M3.5 8.2 6.7 11.2 12.6 4.8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="ap-var-row-name">{{ factor.label }}</span>
              <span v-if="factor.disabled" class="ap-second-order-owner">已归属：{{ factor.ownerLabel }}</span>
              <span class="ap-var-row-tag accept-numeric">{{ factor.count }} 个题项</span>
            </button>
            <div v-if="!firstOrderFactorChoices.length" class="ap-drop-empty">
              先在上方建立一阶因子
            </div>
          </div>
          <div v-if="activeSecondOrderMembers.length < 2" class="ap-second-order-warning">
            二阶因子至少需要选择 2 个一阶因子。
          </div>
        </div>
      </div>
    </template>

    <div
      v-else
      v-for="(slot, slotIndex) in displaySlots"
      :key="slot.key"
      class="ap-slot"
      :class="{
        'ap-slot-grow': !usesEqualSlotHeights && slotIndex === displaySlots.length - 1,
        'ap-slot-equal': usesEqualSlotHeights,
      }"
    >
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
      <div v-if="method.options?.length && !isSummaryTMethod" class="ap-options ap-options--actions">
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
            <label>
              {{ option.label }}：
              <span v-if="option.hint" class="ap-option-help" :data-hint="option.hint">?</span>
            </label>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AnalysisDropZone from './AnalysisDropZone.vue'

const configRoot = ref(null)
const titleInputRef = ref(null)

const props = defineProps({
  activeSecondOrderFactorName: { type: String, default: '二阶模型1' },
  activeSecondOrderKey: { type: String, default: 'second_order_1' },
  activeSecondOrderMembers: { type: Array, default: () => [] },
  activeFactorItems: { type: Array, default: () => [] },
  activeFactorKey: { type: String, default: '' },
  activeFactorSlot: { type: Object, default: null },
  activeFactorTitle: { type: String, default: '' },
  canExecute: { type: Boolean, default: false },
  displaySlots: { type: Array, default: () => [] },
  dragOverSlot: { type: String, default: null },
  dynamicFactorCount: { type: Number, default: 1 },
  dynamicGroupAddText: { type: String, default: '+ 新建因子' },
  dynamicGroupItemName: { type: String, default: '题项' },
  dynamicGroupTip: { type: String, default: '' },
  editingConfig: { type: Boolean, default: false },
  executing: { type: Boolean, default: false },
  factorMenuKey: { type: String, default: null },
  firstOrderFactorChoices: { type: Array, default: () => [] },
  getFactorShortLabel: { type: Function, required: true },
  getVarType: { type: Function, required: true },
  getVarTypeClass: { type: Function, required: true },
  isCfaMethod: { type: Boolean, default: false },
  isSummaryTMethod: { type: Boolean, default: false },
  maxDynamicFactors: { type: Number, default: 12 },
  maxSecondOrderModels: { type: Number, default: 8 },
  method: { type: Object, required: true },
  optionValues: { type: Object, required: true },
  renameFocusToken: { type: Object, default: () => ({ key: '', nonce: 0 }) },
  results: { type: Array, default: () => [] },
  secondOrderModels: { type: Array, default: () => [] },
  secondOrderFactorChoices: { type: Array, default: () => [] },
  slotValues: { type: Object, required: true },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'add-second-order-model',
  'add-factor',
  'close-factor-menu',
  'delete-factor',
  'delete-second-order-model',
  'drag-leave',
  'drag-over',
  'drop-slot',
  'execute',
  'option-change',
  'remove-var',
  'rename-second-order-factor',
  'rename-factor',
  'rename-factor-inline',
  'reset',
  'select-factor',
  'select-second-order-model',
  'show-report',
  'toggle-factor-menu',
  'toggle-second-order-member',
])

const equalSlotMethodLabels = new Set([
  'Kano模型',
  '多选-多选（交叉分析）',
  '多选-单选（对比分析）',
  '单选-多选（对比分析）',
])
const usesEqualSlotHeights = computed(() => equalSlotMethodLabels.has(props.method?.label))

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
    return (option.choices || []).map(choice => {
      const value = typeof choice === 'object' ? choice.value : choice
      const label = typeof choice === 'object'
        ? (choice.label || choice.value)
        : (option.choice_labels?.[choice] || choice)
      return { value, label }
    })
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

watch(
  () => props.renameFocusToken,
  async token => {
    if (!token?.key || token.key !== props.activeFactorKey) return
    await nextTick()
    titleInputRef.value?.focus?.()
    titleInputRef.value?.select?.()
  },
  { deep: true },
)

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
})
</script>
