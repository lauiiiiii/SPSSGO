<template>
  <div class="sp-app">
    <input ref="dataInputRef" type="file" accept=".xlsx,.xls,.csv,.sav,.zsav,.dta,.sas7bdat,.xpt,.tsv,.txt,.json,.parquet" class="sr-only" @change="onDataFileByTarget" />

    <TopBar
      :has-results="historyItems.length > 0"
      :active-tab="currentTab"
      @upload="openUploadModal('workspace')"
      @export="downloadWord"
      @toggle-ai="toggleAi"
      @tab-change="onTabChange"
    />

    <div class="sp-body">
      <template v-if="currentTab === 'analysis'">
        <div class="analysis-shell">
          <MethodNav
            :methods="methodsMeta"
            :categories="methodCategories"
            :active-method="activeMethodKey"
            @select="onSelectMethod"
          />

          <div class="analysis-workbench">
            <HistoryPanel
              v-if="historyItems.length > 0"
              :items="historyItems"
              :active-index="activeHistoryIdx"
              :has-any-items="historyItems.length > 0"
              @select="applyHistoryItem"
              @rename="onRenameHistory"
              @delete="onDeleteHistory"
              @new-analysis="onNewAnalysis"
            />

            <div class="analysis-main">
              <VariablePanel
                v-if="showVariablePanel"
                :variables="variables"
                :total-rows="totalRows"
                :selected-vars="selectedVars"
                :used-vars="usedVars"
                @select="onVarSelect"
                @deselect="onVarDeselect"
                @select-range="onVarSelectRange"
                @drag-start="onVariableDragStart"
                @drag-end="onVariableDragEnd"
                @change-type="onChangeVariableType"
                @delete-variable="onDeleteVariable"
                @rename-variable="onRenameVariable"
                @rename-batch="onRenameVariablesBatch"
              />

              <AnalysisPanel
                :has-data="hasData"
                :method="activeMethodMeta"
                :method-key="activeMethodKey"
                :executing="executing"
                :results="currentResults"
                :variables="variables"
                :drag-preview-count="dragPreviewCount"
                :session-id="sessionId"
                :current-dataset-version-id="currentDatasetVersionId"
                :current-dataset-version-no="currentDatasetVersionNo"
                @upload="openUploadModal('workspace')"
                @go-mydata="currentTab = 'mydata'"
                @execute="executeCurrentMethod"
                @update:slotValues="sv => currentSlotValues = sv"
                @update:optionValues="ov => currentOptionValues = ov"
                @report-view="v => analysisReportVisible = v"
                @reset-variable-selection="selectedVars = []"
              />
            </div>
          </div>
        </div>
      </template>

      <DataProcessingPanel
        v-else-if="currentTab === 'processing'"
        :session-id="sessionId"
        :data-file-name="dataFileName"
        :variables="variables"
        :total-rows="totalRows"
        :has-data="hasData"
        @variables-updated="loadVariables"
        @upload="openUploadModal('workspace')"
        @go-mydata="currentTab = 'mydata'"
        @go-analysis="sid => { onGoAnalysis(resolveAnalysisSessionId(sid)) }"
        @go-visualization="sid => { onGoVisualization(resolveAnalysisSessionId(sid)) }"
      />

      <div v-else-if="currentTab === 'visualization'" class="visualization-shell">
        <VisualizationWorkbench
          :session-id="visualizationSessionId"
          :data-file-name="visualizationDataFileName"
          :active-result="activeVisualizationResult"
          :history-items="visualizationHistoryItems"
          :active-history-index="activeVisualizationHistoryIdx"
          :variables="visualizationVariables"
          :total-rows="visualizationTotalRows"
          :has-data="visualizationHasData"
          :selected-vars="visualizationSelectedVars"
          @upload="openUploadModal('visualization')"
          @go-mydata="currentTab = 'mydata'"
          @history-saved="refreshVisualizationHistory"
          @select-history="applyVisualizationHistoryItem"
          @rename-history="onRenameVisualizationHistory"
          @delete-history="onDeleteVisualizationHistory"
          @select-variable="onVisualizationVarSelect"
          @deselect-variable="onVisualizationVarDeselect"
          @select-range="onVisualizationVarSelectRange"
          @drag-start="onVariableDragStart"
          @drag-end="onVariableDragEnd"
        />
      </div>

      <MyDataPanel
        v-else-if="currentTab === 'mydata'"
        :data-file-name="dataFileName"
        :total-rows="totalRows"
        :variables="variables"
        :history-items="historyItems"
        :visualization-history-items="visualizationHistoryItems"
        :all-data-sets="allDataSets"
        :current-session-id="sessionId"
        :current-dataset-version-id="currentDatasetVersionId"
        :current-dataset-version-no="currentDatasetVersionNo"
        :folders="folders"
        :dataset-page="datasetPage"
        :dataset-page-size="datasetPageSize"
        :dataset-total="datasetTotal"
        :folder-data-sets-all="folderDataSetsAll"
        @open-result="onOpenResultFromMyData"
        @switch-session="onSwitchSession"
        @activate-version="onActivateDatasetVersion"
        @create-folder="onCreateFolder"
        @delete-folder="onDeleteFolder"
        @rename-folder="onRenameFolder"
        @move-to-folder="onMoveToFolder"
        @rename-dataset="onRenameDataSet"
        @go-analysis="onGoAnalysis"
        @go-processing="onGoProcessing"
        @go-visualization="onGoVisualization"
        @delete-dataset="onDeleteDataSet"
        @export-dataset="onExportDataSet"
        @copy-dataset="onCopyDataSet"
        @upload="openUploadModal('workspace')"
        @version-copied="onDatasetVersionCopied"
        @version-deleted="onDatasetVersionDeleted"
        @refresh-datasets="() => { loadAllDataSets(); loadFolderDataSets() }"
        @change-page="(p, s) => loadAllDataSets(p, s)"
      />

      <ProfilePanel v-else-if="currentTab === 'profile'" />
    </div>

    <UploadDataDialog
      v-if="showUploadModal"
      :drag-hover="dragHover"
      @close="showUploadModal = false"
      @choose-file="dataInputRef?.click()"
      @drop-file="onDropFileByTarget"
      @update:drag-hover="dragHover = $event"
    />

    <ConfirmDialog
      v-if="confirmDialog.visible"
      :dialog="confirmDialog"
      @close="closeConfirmDialog"
      @confirm="confirmActiveDeleteAction"
      @update-suppress="confirmDialog.suppressForHour = $event"
    />

    <RenameDialog
      v-if="renameDialog.visible"
      :dialog="renameDialog"
      @close="closeRenameDialog"
      @submit="submitActiveRenameDialog"
      @update-value="renameDialog.value = $event"
    />

    <AiAssistant ref="aiRef" :context="aiContext" />

    <div
      v-if="tooltip.visible && tooltip.text"
      class="g-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >{{ tooltip.text }}</div>
  </div>
</template>

<script setup>
import { defineAsyncComponent, ref, computed, onMounted, watch } from 'vue'
import { useGlobalTooltip } from '../composables/useGlobalTooltip.js'
import TopBar from '../components/layout/TopBar.vue'
import ConfirmDialog from '../components/dialogs/ConfirmDialog.vue'
import HistoryPanel from '../components/history/HistoryPanel.vue'
import MethodNav from '../components/analysis/MethodNav.vue'
import VariablePanel from '../components/variable/VariablePanel.vue'
import RenameDialog from '../components/dialogs/RenameDialog.vue'
import UploadDataDialog from '../components/dialogs/UploadDataDialog.vue'
import { useAppBootstrap } from '../composables/workspace/useAppBootstrap.js'
import { useAnalysisExecution } from '../composables/analysis/useAnalysisExecution.js'
import { useDataUpload } from '../composables/data/useDataUpload.js'
import { useDatasetLibrary } from '../composables/data/useDatasetLibrary.js'
import { useHistoryManager } from '../composables/history/useHistoryManager.js'
import { useTaskJobs } from '../composables/data/useTaskJobs.js'
import { useVariableActions } from '../composables/variable/useVariableActions.js'
import { useVariableSelection } from '../composables/variable/useVariableSelection.js'
import { useWorkspaceDeletion } from '../composables/workspace/useWorkspaceDeletion.js'
import { useWorkspaceExport } from '../composables/workspace/useWorkspaceExport.js'
import { useWorkspaceNavigation } from '../composables/workspace/useWorkspaceNavigation.js'
import { useWorkspaceDialogs } from '../composables/workspace/useWorkspaceDialogs.js'
import { useWorkspaceUiState } from '../composables/workspace/useWorkspaceUiState.js'
import { createStoredResultMapper } from '../utils/historyResults.js'
import * as api from '../api.js'

const AnalysisPanel = defineAsyncComponent(() => import('../components/analysis/AnalysisPanel.vue'))
const MyDataPanel = defineAsyncComponent(() => import('../components/my-data/MyDataPanel.vue'))
const DataProcessingPanel = defineAsyncComponent(() => import('../data-processing/DataProcessingPanel.vue'))
const VisualizationWorkbench = defineAsyncComponent(() => import('../components/visualization/VisualizationWorkbench.vue'))
const ProfilePanel = defineAsyncComponent(() => import('../components/profile/ProfilePanel.vue'))
const AiAssistant = defineAsyncComponent(() => import('../components/AiAssistant.vue'))

const dataInputRef = ref(null)
const aiRef = ref(null)
const { tooltip } = useGlobalTooltip()
const VISUALIZATION_SESSION_KEY = 'spssgo_visualization_session_id'

const currentTab = ref('analysis')
const sessionId = ref('')
const hasData = ref(false)
const dataFileName = ref('')
const showUploadModal = ref(false)
const uploadTarget = ref('workspace')
const dragHover = ref(false)
const taskJobs = ref([])
const {
  closeConfirmDialog,
  closeRenameDialog,
  confirmDialog,
  openConfirmDialog,
  openRenameDialog,
  renameDialog,
} = useWorkspaceDialogs()

const methodsMeta = ref({})
const methodCategories = ref([])
const activeMethodKey = ref('')
const variables = ref([])
const totalRows = ref(0)
const selectedVars = ref([])
const visualizationSessionId = ref('')
const visualizationHasData = ref(false)
const visualizationDataFileName = ref('')
const visualizationVariables = ref([])
const visualizationTotalRows = ref(0)
const visualizationSelectedVars = ref([])
const visualizationSlotValues = ref({})
const visualizationHistoryItems = ref([])
const activeVisualizationHistoryIdx = ref(-1)
const dragPreviewCount = ref(0)

const executing = ref(false)
const currentResults = ref([])
const currentSlotValues = ref({})
const currentOptionValues = ref({})
const currentDatasetVersionId = ref(null)
const currentDatasetVersionNo = ref(null)

const historyItems = ref([])
const activeHistoryIdx = ref(-1)
/** 独立分析结果页打开时隐藏「选择变量」列 */
const analysisReportVisible = ref(false)
const activeMethodMeta = computed(() => {
  if (!activeMethodKey.value || !methodsMeta.value[activeMethodKey.value]) return null
  return methodsMeta.value[activeMethodKey.value]
})
const activeVisualizationResult = computed(() => {
  const item = visualizationHistoryItems.value[activeVisualizationHistoryIdx.value]
  return item?.results?.[0] || null
})
const showVariablePanel = computed(() => (
  hasData.value
  && !!activeMethodMeta.value
  && !activeMethodMeta.value.reserved
  && !executing.value
  && !analysisReportVisible.value
))

const {
  inferMethodKeyFromName,
  mapStoredResults,
} = createStoredResultMapper(methodsMeta)
const {
  activateFirstHistoryWithMethod,
  applyHistoryItem,
  clearCurrentAnalysis,
  confirmHistoryDelete,
  onDeleteHistory,
  onRenameHistory,
  submitRenameDialog,
} = useHistoryManager({
  activeHistoryIdx,
  activeMethodKey,
  analysisReportVisible,
  closeRenameDialog,
  currentResults,
  findMethodKeyFromItem: inferMethodKeyFromName,
  historyItems,
  methodsMeta,
  openConfirmDialog,
  openRenameDialog,
  renameDialog,
  sessionId,
})

const aiContext = computed(() => {
  let ctx = ''
  if (dataFileName.value) ctx += `数据文件: ${dataFileName.value}\n`
  if (variables.value.length) {
    ctx += `变量(${variables.value.length}): ${variables.value.slice(0, 20).map(v => v.name).join(', ')}\n`
  }
  if (activeMethodKey.value) {
    const m = methodsMeta.value[activeMethodKey.value]
    if (m) ctx += `当前选中方法: ${m.label}\n`
  }
  if (currentResults.value.length) {
    ctx += `已完成分析: ${currentResults.value.map(r => r.name).join(', ')}\n`
  }
  return ctx
})

const {
  allDataSets,
  datasetPage,
  datasetPageSize,
  datasetTotal,
  folderDataSetsAll,
  folders,
  loadAllDataSets,
  loadFolderDataSets,
  onCopyDataSet,
  onCreateFolder,
  onDeleteDataSet,
  onDeleteFolder,
  onExportDataSet,
  onMoveToFolder,
  onRenameDataSet,
  onRenameFolder,
  saveFolders,
  switchSession,
} = useDatasetLibrary({
  activeHistoryIdx,
  activeMethodKey,
  confirmDialog,
  currentDatasetVersionId,
  currentDatasetVersionNo,
  currentResults,
  dataFileName,
  hasData,
  historyItems,
  mapStoredResults,
  sessionId,
  totalRows,
  variables,
})
const {
  onVarDeselect,
  onVarSelect,
  onVarSelectRange,
  usedVars,
} = useVariableSelection({
  currentSlotValues,
  selectedVars,
})
const {
  onVarDeselect: onVisualizationVarDeselect,
  onVarSelect: onVisualizationVarSelect,
  onVarSelectRange: onVisualizationVarSelectRange,
} = useVariableSelection({
  currentSlotValues: visualizationSlotValues,
  selectedVars: visualizationSelectedVars,
})

const {
  handleTrackedJobProgress,
  refreshTaskJobs,
  startTaskJobPolling,
  syncResultContext,
} = useTaskJobs({
  currentDatasetVersionId,
  currentDatasetVersionNo,
  historyItems,
  mapStoredResults,
  sessionId,
  taskJobs,
})
const {
  loadVariables,
  sessionStorageKey,
} = useAppBootstrap({
  hasData,
  dataFileName,
  historyItems,
  loadAllDataSets,
  loadFolderDataSets,
  mapStoredResults,
  methodCategories,
  methodsMeta,
  sessionId,
  startTaskJobPolling,
  syncResultContext,
  totalRows,
  variables,
})

function setCurrentDatasetVersion(result) {
  if (!result) return
  if (result.dataset_version_id) currentDatasetVersionId.value = result.dataset_version_id
  if (result.dataset_version_no) currentDatasetVersionNo.value = result.dataset_version_no
}

async function onActivateDatasetVersion(versionId) {
  if (!sessionId.value || !versionId) return
  if (currentResults.value.length) {
    const ok = window.confirm('切换数据版本后，当前临时分析结果会被清空，后续预览和分析都会基于新版本。确认切换吗？')
    if (!ok) return
  }
  try {
    const result = await api.activateDatasetVersion(sessionId.value, versionId)
    setCurrentDatasetVersion(result)
    await loadVariables()
    await loadAllDataSets()
    clearCurrentAnalysis()
  } catch (err) {
    alert(`切换数据版本失败：${err.message || err}`)
  }
}

async function onDatasetVersionDeleted() {
  await Promise.all([loadAllDataSets(), loadFolderDataSets(), refreshTaskJobs({ forceResults: true })])
}

async function onDatasetVersionCopied(result) {
  setCurrentDatasetVersion(result)
  clearCurrentAnalysis()
  await Promise.all([loadVariables(), loadAllDataSets(), loadFolderDataSets(), refreshTaskJobs({ forceResults: true })])
}

const variableActions = useVariableActions({
  sessionId,
  selectedVars,
  loadVariables,
  loadAllDataSets,
  setDatasetVersion: setCurrentDatasetVersion,
})
const {
  onDataFile,
  onDropFile,
} = useDataUpload({
  dataFileName,
  dragHover,
  handleTrackedJobProgress,
  hasData,
  loadAllDataSets,
  loadVariables,
  sessionId,
  showUploadModal,
})
const {
  executeCurrentMethod,
} = useAnalysisExecution({
  activeHistoryIdx,
  activeMethodKey,
  activeMethodMeta,
  currentOptionValues,
  currentResults,
  currentSlotValues,
  executing,
  handleTrackedJobProgress,
  historyItems,
  mapStoredResults,
  sessionId,
  syncResultContext,
})
const {
  onGoAnalysis,
  onGoProcessing,
  onOpenResultFromMyData,
  onSwitchSession,
  onTabChange,
  resolveAnalysisSessionId,
} = useWorkspaceNavigation({
  activateFirstHistoryWithMethod,
  applyHistoryItem,
  currentTab,
  sessionId,
  switchSession,
})
const {
  confirmDeleteAction,
} = useWorkspaceDeletion({
  allDataSets,
  closeConfirmDialog,
  confirmDialog,
  confirmHistoryDelete,
  currentDatasetVersionId,
  currentDatasetVersionNo,
  currentResults,
  dataFileName,
  folders,
  hasData,
  historyItems,
  saveFolders,
  sessionId,
  sessionStorageKey,
  totalRows,
  variables,
})
const {
  downloadWord,
} = useWorkspaceExport({
  handleTrackedJobProgress,
  sessionId,
})
const {
  onNewAnalysis,
  onSelectMethod,
  toggleAi,
} = useWorkspaceUiState({
  activeHistoryIdx,
  activeMethodKey,
  aiRef,
  analysisReportVisible,
  clearCurrentAnalysis,
  currentResults,
  selectedVars,
})

const onChangeVariableType = variableActions.changeType
const onDeleteVariable = variableActions.deleteVariable
const onRenameVariable = variableActions.renameVariable
const onRenameVariablesBatch = variableActions.renameBatch

function openUploadModal(target = 'workspace') {
  uploadTarget.value = target
  showUploadModal.value = true
}

async function onDataFileByTarget(event) {
  const file = event.target.files[0]
  if (!file) {
    event.target.value = ''
    return
  }
  if (uploadTarget.value === 'visualization') {
    showUploadModal.value = false
    await uploadVisualizationData(file)
    event.target.value = ''
    return
  }
  onDataFile(event)
}

async function onDropFileByTarget(event) {
  if (uploadTarget.value === 'visualization') {
    dragHover.value = false
    const file = event.dataTransfer?.files?.[0]
    if (file) {
      showUploadModal.value = false
      await uploadVisualizationData(file)
    }
    return
  }
  onDropFile(event)
}

async function uploadVisualizationData(file) {
  try {
    const session = await api.createSession()
    const sid = session.session_id
    const uploaded = await api.uploadFile(sid, file, { onProgress: handleTrackedJobProgress })
    if (uploaded.job) handleTrackedJobProgress(uploaded.job)
    await loadVisualizationSession(sid, { persist: true })
    await Promise.all([loadAllDataSets(), loadFolderDataSets()])
    currentTab.value = 'visualization'
  } catch (e) {
    alert('上传失败: ' + e.message)
  }
}

async function loadVisualizationSession(sid, options = {}) {
  const { persist = false, switchTab = false } = options
  if (!sid) return false

  try {
    const [files, varsData] = await Promise.all([
      api.getFiles(sid),
      api.getVariables(sid).catch(() => ({ variables: [], total_rows: 0 })),
    ])
    const dataFiles = files.data_files || []
    if (!dataFiles.length) {
      if (persist) localStorage.removeItem(VISUALIZATION_SESSION_KEY)
      return false
    }

    visualizationSessionId.value = sid
    visualizationHasData.value = true
    visualizationDataFileName.value = dataFiles[0].name
    visualizationVariables.value = varsData.variables || []
    visualizationTotalRows.value = varsData.total_rows || 0
    visualizationSelectedVars.value = []
    visualizationSlotValues.value = {}
    activeVisualizationHistoryIdx.value = -1
    await refreshVisualizationHistory()
    if (persist) localStorage.setItem(VISUALIZATION_SESSION_KEY, sid)
    if (switchTab) currentTab.value = 'visualization'
    return true
  } catch (_) {
    if (persist) localStorage.removeItem(VISUALIZATION_SESSION_KEY)
    return false
  }
}

async function refreshVisualizationHistory() {
  if (!visualizationSessionId.value) {
    visualizationHistoryItems.value = []
    activeVisualizationHistoryIdx.value = -1
    return
  }
  try {
    const resultData = await api.getResults(visualizationSessionId.value)
    visualizationHistoryItems.value = mapStoredResults(resultData.results || [], { kind: 'visualization' })
    activeVisualizationHistoryIdx.value = visualizationHistoryItems.value.length ? 0 : -1
  } catch (_) {
    visualizationHistoryItems.value = []
    activeVisualizationHistoryIdx.value = -1
  }
}

function applyVisualizationHistoryItem(idx) {
  activeVisualizationHistoryIdx.value = idx
}

function onRenameVisualizationHistory(idx) {
  const item = visualizationHistoryItems.value[idx]
  if (!item) return
  openRenameDialog({
    context: 'visualization',
    title: '重命名可视化记录',
    value: item.name || '',
    targetId: item.id || '',
    targetIndex: idx,
  })
}

function onDeleteVisualizationHistory(idx) {
  const item = visualizationHistoryItems.value[idx]
  if (!item) return
  openConfirmDialog({
    context: 'visualization',
    title: '删除后不可恢复',
    message: '确认删除可视化记录吗？',
    type: 'visualization-history',
    targetId: item.id || '',
    targetIndex: idx,
  })
}

async function submitVisualizationRenameDialog() {
  const idx = renameDialog.targetIndex
  const item = visualizationHistoryItems.value[idx]
  const trimmed = String(renameDialog.value || '').trim()
  if (!item) {
    closeRenameDialog()
    return
  }
  if (!trimmed) return
  if (trimmed === item.name) {
    closeRenameDialog()
    return
  }
  try {
    await api.renameAnalysisResult(visualizationSessionId.value, renameDialog.targetId, trimmed)
    item.name = trimmed
    if (item.results?.length) item.results[0].name = trimmed
    closeRenameDialog()
  } catch (e) {
    alert('重命名失败: ' + e.message)
  }
}

async function submitActiveRenameDialog() {
  if (renameDialog.context === 'visualization') {
    await submitVisualizationRenameDialog()
    return
  }
  await submitRenameDialog()
}

async function confirmVisualizationHistoryDelete(targetId, targetIndex) {
  try {
    if (targetId) await api.deleteAnalysisResult(visualizationSessionId.value, targetId)
    visualizationHistoryItems.value.splice(targetIndex, 1)
    if (!visualizationHistoryItems.value.length) {
      activeVisualizationHistoryIdx.value = -1
      return
    }
    if (activeVisualizationHistoryIdx.value === targetIndex) {
      activeVisualizationHistoryIdx.value = Math.min(targetIndex, visualizationHistoryItems.value.length - 1)
      return
    }
    if (activeVisualizationHistoryIdx.value > targetIndex) activeVisualizationHistoryIdx.value -= 1
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}

async function confirmActiveDeleteAction() {
  if (confirmDialog.type === 'visualization-history' || confirmDialog.context === 'visualization') {
    const targetId = confirmDialog.targetId
    const targetIndex = confirmDialog.targetIndex
    closeConfirmDialog()
    await confirmVisualizationHistoryDelete(targetId, targetIndex)
    return
  }
  await confirmDeleteAction()
}

async function onGoVisualization(sid) {
  const loaded = await loadVisualizationSession(sid, { persist: true, switchTab: true })
  if (!loaded) alert('加载可视化数据失败，请重新选择或上传数据')
}

async function refreshCurrentSessionVisualizationHistory() {
  if (!sessionId.value) {
    visualizationHistoryItems.value = []
    activeVisualizationHistoryIdx.value = -1
    return
  }
  visualizationSessionId.value = sessionId.value
  await refreshVisualizationHistory()
}

onMounted(() => {
  const savedVisualizationSessionId = localStorage.getItem(VISUALIZATION_SESSION_KEY)
  if (savedVisualizationSessionId) {
    loadVisualizationSession(savedVisualizationSessionId).catch(() => {})
  }
})

watch([currentTab, sessionId], () => {
  if (currentTab.value === 'mydata') {
    refreshCurrentSessionVisualizationHistory().catch(() => {})
  }
})

function onVariableDragStart(names) {
  dragPreviewCount.value = Array.isArray(names) && names.length ? names.length : 1
}

function onVariableDragEnd() {
  dragPreviewCount.value = 0
}
</script>
