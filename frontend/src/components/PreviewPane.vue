<template>
  <aside class="preview-pane">
    <!-- Title bar -->
    <div class="xl-titlebar">
      <div class="xl-titlebar-left">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 1l-3 3v8l3 3h8l3-3V4l-3-3H4z" fill="#217346"/><path d="M4.5 5h2.3l1.2 2.6L9.2 5h2.3L9 8.9l2.8 4.1H9.5L8 10.2 6.5 13H4.2L7 8.9 4.5 5z" fill="#fff"/></svg>
        <span class="xl-filename">{{ title }}</span>
      </div>
      <button class="xl-close" @click="$emit('close')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </button>
    </div>

    <!-- Formula bar -->
    <div v-if="mode === 'sheet' && currentSheet" class="xl-formula-bar">
      <div class="xl-cell-ref">{{ activeCellRef }}</div>
      <div class="xl-fx">fx</div>
      <div class="xl-formula-value">{{ activeCellValue }}</div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="pv-loading">
      <div class="pv-spinner"></div>
      <span>加载中...</span>
    </div>

    <!-- Spreadsheet view -->
    <template v-else-if="mode === 'sheet' && currentSheet">
      <div class="xl-sheet-wrap">
        <div class="xl-sheet" @click="onCellClick">
          <table class="xl-table">
            <thead>
              <tr>
                <th class="xl-corner"></th>
                <th v-for="(h, i) in currentSheet.headers" :key="'l'+i"
                    class="xl-col-letter"
                    :class="{ 'xl-col-active': activeCol === i }">{{ columnLetter(i) }}</th>
              </tr>
              <tr class="xl-header-row">
                <th class="xl-row-num xl-header-num">1</th>
                <th v-for="(h, i) in currentSheet.headers" :key="'h'+i"
                    class="xl-header-cell"
                    :class="{ 'xl-cell-selected': activeRow === -1 && activeCol === i }"
                    :title="h"
                    @click.stop="selectCell(-1, i, h)">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in currentSheet.rows" :key="ri">
                <td class="xl-row-num" :class="{ 'xl-row-active': activeRow === ri }">{{ ri + 2 }}</td>
                <td v-for="(cell, ci) in row" :key="ci"
                    class="xl-cell"
                    :class="{
                      'xl-cell-num': isCellNumber(cell),
                      'xl-cell-selected': activeRow === ri && activeCol === ci
                    }"
                    :title="cell"
                    @click.stop="selectCell(ri, ci, cell)">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Status bar + Sheet tabs -->
      <div class="xl-bottom">
        <div class="xl-tabs">
          <button v-for="(s, i) in sheets" :key="i"
            class="xl-tab" :class="{ active: i === activeSheetIdx }"
            @click="activeSheetIdx = i">{{ s.name }}</button>
        </div>
        <div class="xl-status">
          <span>{{ totalRows }} 行 × {{ currentSheet.headers.length }} 列</span>
          <span class="xl-status-hint">显示前 {{ currentSheet.rows.length }} 行</span>
        </div>
      </div>
    </template>

    <!-- Text view -->
    <div v-else-if="mode === 'text' && content" class="pv-text-body">{{ content }}</div>

    <!-- Empty -->
    <div v-else-if="!loading" class="pv-empty">暂无预览内容</div>
  </aside>
</template>

<script setup>
import { toRef } from 'vue'
import { useWorkbookPreview } from '../composables/shared/useWorkbookPreview.js'
import { columnLetter, isCellNumber } from '../utils/spreadsheetPreview.js'

const props = defineProps({
  title: { type: String, default: '预览' },
  mode: { type: String, default: 'text' },
  content: { type: String, default: '' },
  fileBuffer: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})
defineEmits(['close'])

const {
  activeCellRef,
  activeCellValue,
  activeCol,
  activeRow,
  activeSheetIdx,
  currentSheet,
  resetActiveCell,
  selectCell,
  sheets,
  totalRows,
} = useWorkbookPreview(toRef(props, 'fileBuffer'))

function onCellClick() {
  resetActiveCell()
}
</script>
