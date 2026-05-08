<template>
  <div class="dp-table-wrap">
    <div class="dp-grid-frame ag-theme-quartz">
      <AgGridVue
        class="dp-grid"
        :columnDefs="gridColumnDefs"
        :rowData="gridRowData"
        :pinnedTopRowData="gridPinnedTopRowData"
        :defaultColDef="gridDefaultColDef"
        :headerHeight="34"
        :rowHeight="34"
        :rowSelection="{ mode: 'singleRow', checkboxes: false, enableClickSelection: false }"
        :suppressRowClickSelection="true"
        :suppressCellFocus="true"
        :suppressHeaderFocus="true"
        :suppressContextMenu="true"
        :suppressDragLeaveHidesColumns="true"
        :suppressMovableColumns="true"
        :suppressColumnMoveAnimation="true"
        :animateRows="false"
      />
      <div class="dp-grid-statusbar">
        <span>预览 {{ previewedRows }} / {{ totalRows }} 行</span>
        <label>
          <span>显示前</span>
          <select
            :value="previewLimit"
            @change="$emit('update:previewLimit', Number($event.target.value))"
          >
            <option
              v-for="limit in previewLimitOptions"
              :key="limit"
              :value="limit"
            >
              {{ limit }}
            </option>
          </select>
          <span>行</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import {
  CellStyleModule,
  ClientSideRowModelModule,
  ColumnAutoSizeModule,
  ModuleRegistry,
  PinnedRowModule,
  RowSelectionModule,
  TooltipModule,
  ValidationModule,
} from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

ModuleRegistry.registerModules([
  CellStyleModule,
  ClientSideRowModelModule,
  ColumnAutoSizeModule,
  PinnedRowModule,
  RowSelectionModule,
  TooltipModule,
  ValidationModule,
])

const props = defineProps({
  headers: { type: Array, default: () => [] },
  displayHeaders: { type: Array, default: () => [] },
  displayRows: { type: Array, default: () => [] },
  columnDiffMap: { type: Object, default: () => ({}) },
  previewLimit: { type: Number, default: 100 },
  previewLimitOptions: { type: Array, default: () => [100, 500, 1000] },
  previewedRows: { type: Number, default: 0 },
  totalRows: { type: Number, default: 0 },
  columnWidth: { type: Number, default: 70 },
})

defineEmits(['update:previewLimit'])

const gridDefaultColDef = computed(() => ({
  sortable: false,
  resizable: true,
  suppressMovable: true,
  suppressMenu: true,
  width: props.columnWidth,
  minWidth: props.columnWidth,
  cellClass: 'dp-grid-cell',
  headerClass: 'dp-grid-header-cell',
}))

const gridColumnDefs = computed(() => {
  const baseColumn = {
    headerName: '',
    field: '__rowIndex',
    pinned: 'left',
    width: 56,
    minWidth: 56,
    maxWidth: 56,
    resizable: false,
    sortable: false,
    suppressMovable: true,
    suppressMenu: true,
    lockPinned: true,
    cellClass: 'dp-grid-row-index',
    headerClass: 'dp-grid-row-index-header',
    valueGetter: params => params.data?.__rowIndex,
  }
  const columns = props.headers.map((header, index) => ({
    headerName: columnLetter(index),
    field: `col_${index}`,
    headerTooltip: props.displayHeaders[index] || header,
    cellClass: ['dp-grid-cell', diffCellClass(header)],
    headerClass: ['dp-grid-header-cell', diffHeaderClass(header)],
  }))
  return [baseColumn, ...columns]
})

const gridPinnedTopRowData = computed(() => {
  const record = { __rowIndex: 1 }
  props.displayHeaders.forEach((header, index) => {
    record[`col_${index}`] = header
  })
  return [record]
})

const gridRowData = computed(() => props.displayRows.map((row, rowIndex) => {
  const record = { __rowIndex: rowIndex + 2 }
  row.forEach((cell, cellIndex) => {
    record[`col_${cellIndex}`] = cell
  })
  return record
}))

function columnLetter(index) {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  if (index < 26) return letters[index]
  return letters[Math.floor(index / 26) - 1] + letters[index % 26]
}

function diffCellClass(header) {
  const diffType = props.columnDiffMap?.[header]
  if (diffType === 'added') return 'dp-grid-cell--added'
  if (diffType === 'changed') return 'dp-grid-cell--changed'
  return ''
}

function diffHeaderClass(header) {
  const diffType = props.columnDiffMap?.[header]
  if (diffType === 'added') return 'dp-grid-header-cell--added'
  if (diffType === 'changed') return 'dp-grid-header-cell--changed'
  return ''
}
</script>
