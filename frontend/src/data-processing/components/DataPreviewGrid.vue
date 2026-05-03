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
})

const gridDefaultColDef = {
  sortable: false,
  resizable: true,
  suppressMovable: true,
  suppressMenu: true,
  minWidth: 92,
  flex: 1,
  cellClass: 'dp-grid-cell',
  headerClass: 'dp-grid-header-cell',
}

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
</script>
