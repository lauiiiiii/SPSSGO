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
        @export-current="exportCurrent"
      />

      <DataPreviewGrid
        v-if="hasData && displayHeaders.length"
        :headers="previewHeaders"
        :display-headers="displayHeaders"
        :display-rows="displayRows"
      />

      <div v-else-if="!hasData" class="dp-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none"><path d="M3 3h18v18H3V3z" stroke="#d1d5db" stroke-width="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke="#d1d5db" stroke-width="1" opacity=".35"/></svg>
        <p>请先上传数据文件</p>
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
import { defineAsyncComponent } from 'vue'
import ExportDialog from './components/ExportDialog.vue'
import MethodConfigDialog from './components/MethodConfigDialog.vue'
import ProcessingSidebar from './components/ProcessingSidebar.vue'
import ProcessingTopbar from './components/ProcessingTopbar.vue'
import VariableActionMenu from './components/VariableActionMenu.vue'
import VersionDialog from './components/VersionDialog.vue'
import { useDatasetExport } from './composables/useDatasetExport.js'
import { useDatasetPreview } from './composables/useDatasetPreview.js'
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

const emit = defineEmits(['variables-updated', 'go-analysis'])

const {
  catVars,
  notifySuccess,
  numericVars,
  successMsg,
  viewMode,
} = useProcessingShellState(props)
const {
  displayHeaders,
  displayRows,
  loadPreview,
  previewHeaders,
  previewLoading,
  variableMetaMap,
} = useDatasetPreview(props, viewMode)
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
} = useDatasetVersions(props, { emit, loadPreview, notifySuccess })
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
</script>
