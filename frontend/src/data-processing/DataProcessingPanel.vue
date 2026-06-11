<template>
  <div class="dp-panel">
    <ProcessingSidebar
      :data-file-name="dataFileName"
      :active-method="activeMethod"
      :methods="processingMethods"
      @open-method="openMethod"
    />

    <div class="dp-main">
      <ProcessingTopbar
        v-if="hasData"
        :data-file-name="dataFileName"
        :total-rows="totalRows"
        :variables-count="variables.length"
        :current-version-no="currentVersionNo"
        :view-mode="viewMode"
        @update:view-mode="viewMode = $event"
        @open-version="openVersionDialog"
        @go-analysis="$emit('go-analysis')"
        @go-visualization="$emit('go-visualization')"
        @export-current="exportCurrent"
      />

      <div v-if="hasData && previewDiffSummary" class="dp-diff-notice">
        <span>{{ previewDiffSummary }}</span>
        <button type="button" @click="clearPreviewDiff">清除</button>
      </div>

      <DataPreviewGrid
        v-if="hasData && displayHeaders.length"
        :headers="previewHeaders"
        :display-headers="displayHeaders"
        :display-rows="displayRows"
        :column-diff-map="columnDiffMap"
        :preview-limit="previewLimit"
        :preview-limit-options="previewLimitOptions"
        :previewed-rows="previewedRowCount"
        :total-rows="totalRows"
        :column-width="previewColumnWidth"
        @update:preview-limit="handlePreviewLimitChange"
      />

      <div v-else-if="!hasData" class="dp-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="#d1d5db" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="#d1d5db" stroke-width="1" opacity=".35"/></svg>
        <p>暂无数据</p>
        <div class="dp-empty-actions">
          <button class="viz-primary-btn" type="button" @click="$emit('upload')">上传数据文件</button>
          <button class="viz-secondary-btn" type="button" @click="$emit('go-mydata')">去我的数据选择</button>
        </div>
      </div>

      <div v-if="hasData && previewLoading" class="dp-loading">加载数据中...</div>
    </div>

    <MethodConfigDialog
      v-if="activeMethod"
      :active-method="activeMethod"
      :active-method-component="activeMethodComponent"
      :active-method-label="activeMethodLabel"
      :cat-vars="catVars"
      :dialog-help-text="dialogHelpText"
      :encode-hint-text="encodeHintText"
      :error-msg="errorMsg"
      :is-variable-selectable="isVariableSelectable"
      :label-editable="labelEditable"
      :label-hint-text="labelHintText"
      :method-actions="methodActions"
      :method-runtime="methodRuntime"
      :min-vars="methodMinVars"
      :needs-multi-var="methodNeedsMultiVar"
      :numeric-vars="numericVars"
      :options="dialogOptions"
      :processing="processing"
      :selected-vars="dialogSelectedVars"
      :variables="variables"
      @close="closeDialogOverlays"
      @execute="executeProcess"
      @toggle-var="toggleDialogVar"
      @remove-var="removeDialogVar"
      @toggle-menu="toggleVarMenu"
    />

    <VariableActionMenu
      v-if="varMenu.visible"
      :menu="varMenu"
      @toggle-type="handleVarTypeToggle"
      @rename="handleVarRename"
      @delete="handleVarDelete"
    />

    <div v-if="successMsg" class="dp-success-toast">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="#10b981" stroke-width="1.5"/><path d="M6 10l3 3 5-5" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      {{ successMsg }}
    </div>

    <ExportDialog
      v-if="exportDialogVisible"
      :formats="exportFormats"
      @close="exportDialogVisible = false"
      @export-format="handleExportFormat"
    />

    <VersionDialog
      v-if="versionDialogVisible"
      :current-version-no="currentVersionNo"
      :loading="versionLoading"
      :versions="datasetVersions"
      :switching-id="versionSwitchingId"
      :format-time="formatVersionTime"
      @close="versionDialogVisible = false"
      @switch-version="switchDatasetVersion"
    />
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import ExportDialog from './components/ExportDialog.vue'
import MethodConfigDialog from './components/MethodConfigDialog.vue'
import ProcessingSidebar from './components/ProcessingSidebar.vue'
import ProcessingTopbar from './components/ProcessingTopbar.vue'
import VariableActionMenu from './components/VariableActionMenu.vue'
import VersionDialog from './components/VersionDialog.vue'
import { useDatasetExport } from './composables/useDatasetExport.js'
import { PREVIEW_LIMIT_OPTIONS, useDatasetPreview } from './composables/useDatasetPreview.js'
import { useDatasetVersions } from './composables/useDatasetVersions.js'
import { useProcessingMethodDialog } from './composables/useProcessingMethodDialog.js'
import { useProcessingOverlayControls, useProcessingShellState } from './composables/useProcessingShellState.js'
import { useProcessingVariableActions } from './composables/useProcessingVariableActions.js'
import { processingMethods } from './methodRegistry.js'

const DataPreviewGrid = defineAsyncComponent(() => import('./components/DataPreviewGrid.vue'))

const props = defineProps({
  sessionId: { type: String, default: '' },
  dataFileName: { type: String, default: '' },
  variables: { type: Array, default: () => [] },
  totalRows: { type: Number, default: 0 },
  hasData: { type: Boolean, default: false },
})

const emit = defineEmits(['variables-updated', 'go-analysis', 'go-visualization', 'upload', 'go-mydata'])
const previewDiff = ref(null)
const previewColumnWidth = 70
const previewLimitOptions = computed(() => buildPreviewLimitOptions(props.totalRows))

const {
  catVars,
  notifySuccess,
  numericVars,
  successMsg,
  viewMode,
} = useProcessingShellState(props)
const {
  createPreviewSnapshot,
  displayHeaders,
  displayRows,
  loadPreview,
  previewHeaders,
  previewLimit,
  previewLoading,
  previewMeta,
  previewRows,
  previewedRowCount,
  setPreviewLimit,
  variableMetaMap,
} = useDatasetPreview(props, viewMode)
const columnDiffMap = computed(() => previewDiff.value?.columnDiffMap || {})
const previewDiffSummary = computed(() => {
  const diff = previewDiff.value
  if (!diff) return ''
  const removedText = diff.removedColumns.length
    ? `，删除：${formatRemovedColumns(diff.removedColumns)}`
    : ''
  return `已和切换前 v${diff.baseVersionNo || '-'} 对比：新增 ${diff.addedColumns.length} 列，变化 ${diff.changedColumns.length} 列，删除 ${diff.removedColumns.length} 列${removedText}`
})
const {
  exportCurrent,
  exportDialogVisible,
  exportFormats,
  handleExportFormat,
} = useDatasetExport(props)
const {
  currentVersionNo,
  datasetVersions,
  formatVersionTime,
  loadVersions,
  openVersionDialog,
  switchDatasetVersion,
  versionDialogVisible,
  versionLoading,
  versionSwitchingId,
} = useDatasetVersions(props, {
  createPreviewSnapshot,
  emit,
  loadPreview,
  notifySuccess,
  onVersionSwitched: applyVersionDiff,
})
const {
  activeMethod,
  activeMethodComponent,
  activeMethodLabel,
  closeDialogOverlays: closeProcessingDialog,
  dialogHelpText,
  dialogOptions,
  dialogSelectedVars,
  encodeHintText,
  errorMsg,
  executeProcess,
  isVariableSelectable,
  labelEditable,
  labelHintText,
  methodActions,
  methodMinVars,
  methodNeedsMultiVar,
  methodRuntime,
  openMethod: openProcessingMethod,
  processing,
  removeDialogVar,
  toggleDialogVar,
} = useProcessingMethodDialog(props, {
  emit,
  loadPreview,
  loadVersions,
  notifySuccess,
  onPreviewMutated: clearPreviewDiff,
  variableMetaMap,
})
const {
  closeVarMenu,
  handleGlobalClick,
  handleVarDelete,
  handleVarRename,
  handleVarTypeToggle,
  toggleVarMenu,
  varMenu,
} = useProcessingVariableActions(props, {
  dialogSelectedVars,
  emit,
  loadPreview,
  loadVersions,
  notifySuccess,
})

const {
  closeDialogOverlays,
  openMethod,
} = useProcessingOverlayControls({
  closeProcessingDialog,
  closeVarMenu,
  handleGlobalClick,
  openProcessingMethod,
})

async function handlePreviewLimitChange(limit) {
  clearPreviewDiff()
  await setPreviewLimit(limit)
}

function clearPreviewDiff() {
  previewDiff.value = null
}

function applyVersionDiff(baseSnapshot) {
  previewDiff.value = buildPreviewDiff(baseSnapshot, {
    headers: previewHeaders.value,
    rows: previewRows.value,
    datasetVersionNo: previewMeta.value.datasetVersionNo,
  })
}

function buildPreviewDiff(baseSnapshot, currentSnapshot) {
  const baseHeaders = baseSnapshot?.headers || []
  const currentHeaders = currentSnapshot?.headers || []
  const baseRows = baseSnapshot?.rows || []
  const currentRows = currentSnapshot?.rows || []
  const baseIndexMap = buildHeaderIndexMap(baseHeaders)
  const currentIndexMap = buildHeaderIndexMap(currentHeaders)

  const addedColumns = currentHeaders.filter(header => !baseIndexMap.has(header))
  const removedColumns = baseHeaders.filter(header => !currentIndexMap.has(header))
  const changedColumns = currentHeaders.filter((header) => {
    if (!baseIndexMap.has(header)) return false
    return columnHasPreviewChange(
      baseRows,
      currentRows,
      baseIndexMap.get(header),
      currentIndexMap.get(header),
    )
  })

  const columnDiffMap = {}
  for (const header of addedColumns) columnDiffMap[header] = 'added'
  for (const header of changedColumns) columnDiffMap[header] = 'changed'

  if (!addedColumns.length && !removedColumns.length && !changedColumns.length) {
    return null
  }
  return {
    addedColumns,
    baseVersionNo: baseSnapshot?.datasetVersionNo || '',
    changedColumns,
    columnDiffMap,
    currentVersionNo: currentSnapshot?.datasetVersionNo || '',
    removedColumns: removedColumns.map((header) => {
      const index = baseIndexMap.get(header)
      return baseSnapshot?.displayHeaders?.[index] || header
    }),
  }
}

function buildHeaderIndexMap(headers) {
  const map = new Map()
  headers.forEach((header, index) => {
    if (!map.has(header)) map.set(header, index)
  })
  return map
}

function columnHasPreviewChange(baseRows, currentRows, baseIndex, currentIndex) {
  const maxRows = Math.max(baseRows.length, currentRows.length)
  for (let rowIndex = 0; rowIndex < maxRows; rowIndex += 1) {
    const baseValue = baseRows[rowIndex]?.[baseIndex] ?? ''
    const currentValue = currentRows[rowIndex]?.[currentIndex] ?? ''
    if (String(baseValue) !== String(currentValue)) return true
  }
  return false
}

function formatRemovedColumns(columns) {
  const visible = columns.slice(0, 4).join('、')
  if (columns.length <= 4) return visible
  return `${visible} 等 ${columns.length} 个`
}

watch(() => props.sessionId, clearPreviewDiff)
watch(() => props.hasData, (hasData) => {
  if (!hasData) clearPreviewDiff()
})

watch(previewLimitOptions, async (options) => {
  if (!options.length || options.includes(previewLimit.value)) return
  await handlePreviewLimitChange(options[options.length - 1])
})

function buildPreviewLimitOptions(totalRows) {
  const total = Number(totalRows || 0)
  if (!total) return PREVIEW_LIMIT_OPTIONS
  const maxPreviewRows = Math.min(total, PREVIEW_LIMIT_OPTIONS[PREVIEW_LIMIT_OPTIONS.length - 1])
  return [...new Set([
    ...PREVIEW_LIMIT_OPTIONS.filter(limit => limit < maxPreviewRows),
    maxPreviewRows,
  ])]
}
</script>
