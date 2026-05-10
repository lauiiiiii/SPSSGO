<template>
  <div
    ref="tableSectionRoot"
    class="ap-sec ap-sec--table"
    :class="{ 'ap-sec--table-inner-title': !showSectionHead }"
  >
    <div v-if="showSectionHead" class="ap-sec-head">
      <div class="ap-sec-head-main">
        <span class="ap-sec-head-title">{{ title }}</span>
      </div>
      <button
        v-if="copyable"
        class="ap-sec-copy"
        @click="copyActiveTable($event)"
      >
        <CopyIcon />
        <span class="ap-sec-copy-txt">复制</span>
      </button>
    </div>
    <div v-if="hasInlineTitle && copyable" class="ap-sec-inline-copy-bar">
      <button class="ap-sec-copy" @click="copyActiveTable($event)">
        <CopyIcon />
        <span class="ap-sec-copy-txt">复制</span>
      </button>
    </div>
    <div class="ap-table-wrap" v-if="section.headers?.length || section.headerRows?.length">
      <div v-if="hasTableToolbar" class="ap-table-mode-toolbar">
        <div class="ap-table-mode-center">
          <span class="ap-table-mode-title">{{ displayModeTitle }}</span>
          <select
            v-if="displayModes.length"
            v-model="selectedMode"
            class="ap-table-mode-select"
          >
            <option
              v-for="mode in displayModes"
              :key="mode.key"
              :value="mode.key"
            >
              {{ mode.label }}
            </option>
          </select>
          <div v-if="rowFilter" class="ap-table-filter" :class="{ 'filter-active': filterMenuOpen }" ref="filterRef">
            <button class="ap-table-filter-summary" @click="toggleFilterMenu">
              {{ rowFilter.label || '过滤指标' }}
            </button>
            <div
              v-if="filterMenuOpen"
              class="ap-table-filter-menu"
              :style="filterMenuStyle"
              ref="filterMenuRef"
            >
              <label class="ap-table-filter-item">
                <input
                  type="checkbox"
                  :checked="isAllFilterSelected"
                  @change="toggleAllFilter($event.target.checked)"
                />
                <span>{{ rowFilter.allLabel || '全选' }}</span>
              </label>
              <label
                v-for="choice in rowFilterChoices"
                :key="choice"
                class="ap-table-filter-item"
              >
                <input
                  type="checkbox"
                  :checked="selectedFilterValues.includes(choice)"
                  @change="toggleFilterChoice(choice)"
                />
                <span>{{ choice }}</span>
              </label>
            </div>
          </div>
        </div>
        <button
          v-if="copyable"
          class="ap-sec-copy ap-table-mode-copy"
          @click="copyActiveTable($event)"
        >
          <CopyIcon />
          <span class="ap-sec-copy-txt">复制</span>
        </button>
      </div>
      <table class="tlt">
        <thead>
          <tr
            v-for="(headerRow, headerRowIndex) in tableHeaderRows"
            :key="headerRowIndex"
          >
            <th
              v-for="(header, headerIndex) in headerRow"
              :key="headerIndex"
              :class="{ 'tlt-head-group': headerColspan(header) > 1 }"
              :colspan="headerColspan(header)"
              :rowspan="headerRowspan(header)"
            >
              {{ headerText(header) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in activeRows" :key="rowIndex">
            <td
              v-for="(cell, cellIndex) in row"
              :key="cellIndex"
              :class="cellClass(cellText(cell))"
              :colspan="cellColspan(cell)"
              :rowspan="cellRowspan(cell)"
            >
              {{ cellText(cell) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="section.note" class="ap-sec-note">{{ section.note }}</p>
    <div v-if="section.description" class="ap-sec-desc">{{ section.description }}</div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  cellClass: { type: Function, required: true },
  copyable: { type: Boolean, default: true },
  section: { type: Object, required: true },
})

const CopyIcon = {
  template: `
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
      <rect
        x="5"
        y="5"
        width="9"
        height="9"
        rx="1.5"
        stroke="currentColor"
        stroke-width="1.2"
      />
      <path
        d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5"
        stroke="currentColor"
        stroke-width="1.2"
      />
    </svg>
  `,
}

const emit = defineEmits(['copy-table'])

const tableSectionRoot = ref(null)
const filterRef = ref(null)
const filterMenuRef = ref(null)
const filterMenuOpen = ref(false)
const filterMenuStyle = ref({})
const title = computed(() => props.section.title || props.section.name)
const displayModeTitle = computed(() => (
  props.section.filterTitle || props.section.displayModeTitle || title.value
))
const displayModes = computed(() => props.section.displayModes || [])
const rowFilter = computed(() => props.section.rowFilter || null)
const rowFilterChoices = computed(() => rowFilter.value?.choices || [])
const tableHeaderRows = computed(() => (
  props.section.headerRows?.length ? props.section.headerRows : [props.section.headers || []]
))
const defaultMode = computed(() => (
  props.section.defaultDisplayMode || displayModes.value[0]?.key || ''
))
const selectedMode = ref(defaultMode.value)
const selectedFilterValues = ref([])
const bodyRowspanColumnCount = computed(() => Number(props.section.bodyRowspanColumns || 0))
const hasTableToolbar = computed(() => displayModes.value.length > 0 || !!rowFilter.value)
const hasInlineTitle = computed(() => !!props.section.inlineTitle)
const showSectionHead = computed(() => !hasTableToolbar.value && !hasInlineTitle.value)
const isAllFilterSelected = computed(() => (
  rowFilterChoices.value.length > 0
  && selectedFilterValues.value.length === rowFilterChoices.value.length
))

const activeRows = computed(() => {
  const mode = displayModes.value.find((item) => item.key === selectedMode.value)
  const rows = mode?.rows || props.section.rows || []
  if (!rowFilter.value || isAllFilterSelected.value) return rows
  const columnIndex = rowFilter.value.columnIndex ?? 0
  return rows.filter(row => selectedFilterValues.value.includes(filterCellValue(row, columnIndex)))
})

watch(defaultMode, (nextMode) => {
  selectedMode.value = nextMode
})

watch(rowFilter, (nextFilter) => {
  selectedFilterValues.value = [...(nextFilter?.default || nextFilter?.choices || [])]
}, { immediate: true })

function copyActiveTable(event) {
  emit('copy-table', { ...props.section, rows: activeRows.value }, event)
}

function headerText(header) {
  return typeof header === 'object' && header !== null ? header.text : header
}

function headerColspan(header) {
  const value = typeof header === 'object' && header !== null ? Number(header.colspan) : 1
  return Number.isFinite(value) && value > 1 ? value : 1
}

function headerRowspan(header) {
  const value = typeof header === 'object' && header !== null ? Number(header.rowspan) : 1
  return Number.isFinite(value) && value > 1 ? value : 1
}

function cellText(cell) {
  return headerText(cell)
}

function cellColspan(cell) {
  return headerColspan(cell)
}

function cellRowspan(cell) {
  return headerRowspan(cell)
}

function filterCellValue(row, columnIndex) {
  const offset = row.length < (props.section.headers?.length || 0)
    ? bodyRowspanColumnCount.value
    : 0
  return cellText(row[columnIndex - offset])
}

function toggleAllFilter(checked) {
  selectedFilterValues.value = checked
    ? [...rowFilterChoices.value]
    : rowFilterChoices.value.slice(0, 1)
}

function toggleFilterChoice(choice) {
  if (selectedFilterValues.value.includes(choice)) {
    if (selectedFilterValues.value.length <= 1) return
    selectedFilterValues.value = selectedFilterValues.value.filter(item => item !== choice)
    return
  }
  selectedFilterValues.value = [...selectedFilterValues.value, choice]
}

function toggleFilterMenu() {
  filterMenuOpen.value = !filterMenuOpen.value
  if (filterMenuOpen.value) {
    nextTick(() => {
      const btn = filterRef.value?.querySelector('.ap-table-filter-summary')
      const menu = filterMenuRef.value
      if (!btn || !menu) return
      const rect = btn.getBoundingClientRect()
      const menuHeight = menu.offsetHeight
      const spaceBelow = window.innerHeight - rect.bottom
      const spaceAbove = rect.top
      let top = rect.bottom + 6
      if (spaceBelow < menuHeight && spaceAbove > menuHeight) {
        top = rect.top - menuHeight - 6
      }
      filterMenuStyle.value = {
        position: 'fixed',
        top: `${top}px`,
        left: `${rect.left}px`,
        minWidth: `${rect.width}px`,
        zIndex: 9999,
      }
    })
  }
}

function closeTableFilters() {
  filterMenuOpen.value = false
}

function handleDocumentPointerDown(event) {
  if (event.target?.closest?.('.ap-table-filter')) return
  closeTableFilters()
}

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
})
</script>
