import { computed, ref, watch } from 'vue'
import * as XLSX from 'xlsx'
import { columnLetter, workbookToPreviewSheets } from '../../utils/spreadsheetPreview.js'

export function useWorkbookPreview(fileBuffer) {
  const sheets = ref([])
  const activeSheetIdx = ref(0)
  const totalRows = ref(0)
  const activeRow = ref(-2)
  const activeCol = ref(-1)
  const activeCellValue = ref('')

  const currentSheet = computed(() => sheets.value[activeSheetIdx.value] || null)

  const activeCellRef = computed(() => {
    if (activeCol.value < 0) return ''
    const letter = columnLetter(activeCol.value)
    const row = activeRow.value === -1 ? 1 : activeRow.value + 2
    return `${letter}${row}`
  })

  function resetActiveCell() {
    activeRow.value = -2
    activeCol.value = -1
    activeCellValue.value = ''
  }

  function selectCell(rowIndex, colIndex, value) {
    activeRow.value = rowIndex
    activeCol.value = colIndex
    activeCellValue.value = value || ''
  }

  function parseWorkbook(buffer) {
    try {
      const data = buffer instanceof ArrayBuffer ? new Uint8Array(buffer) : buffer
      const workbook = XLSX.read(data, { type: 'array' })
      const preview = workbookToPreviewSheets(workbook, XLSX.utils.sheet_to_json)
      sheets.value = preview.sheets
      totalRows.value = preview.totalRows
      activeSheetIdx.value = 0
      resetActiveCell()
    } catch (error) {
      console.error('xlsx parse error', error)
      sheets.value = []
      totalRows.value = 0
      resetActiveCell()
    }
  }

  watch(fileBuffer, (buffer) => {
    if (buffer) parseWorkbook(buffer)
  }, { immediate: true })

  return {
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
  }
}
