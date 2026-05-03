<template>
  <div class="sp-app">
    <input ref="dataInputRef" type="file" accept=".xlsx,.xls,.csv,.sav,.zsav,.dta,.sas7bdat,.xpt,.tsv,.txt,.json,.parquet" class="sr-only" @change="onDataFile" />

    <TopBar
      :has-results="historyItems.length > 0"
      :active-tab="currentTab"
      :active-job-count="activeJobCount"
      @upload="showUploadModal = true"
      @export="downloadWord"
      @toggle-ai="toggleAi"
      @toggle-tasks="toggleTaskCenter"
      @tab-change="onTabChange"
    />

    <TaskCenter
      :open="taskCenterOpen"
      :jobs="taskJobs"
      @close="taskCenterOpen = false"
      @clear-completed="clearCompletedTaskJobs"
      @cancel-job="onCancelTaskJob"
      @retry-job="onRetryTaskJob"
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
                :session-id="sessionId"
                :current-dataset-version-id="currentDatasetVersionId"
                :current-dataset-version-no="currentDatasetVersionNo"
                @upload="showUploadModal = true"
                @execute="executeCurrentMethod"
                @update:slotValues="sv => currentSlotValues = sv"
                @update:optionValues="ov => currentOptionValues = ov"
                @report-view="v => analysisReportVisible = v"
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
        @go-analysis="sid => { onGoAnalysis(resolveAnalysisSessionId(sid)) }"
      />

      <MyDataPanel
        v-else-if="currentTab === 'mydata'"
        :data-file-name="dataFileName"
        :total-rows="totalRows"
        :variables="variables"
        :history-items="historyItems"
        :all-data-sets="allDataSets"
        :current-session-id="sessionId"
        :folders="folders"
        @open-result="onOpenResultFromMyData"
        @switch-session="onSwitchSession"
        @create-folder="onCreateFolder"
        @delete-folder="onDeleteFolder"
        @rename-folder="onRenameFolder"
        @move-to-folder="onMoveToFolder"
        @rename-dataset="onRenameDataSet"
        @go-analysis="onGoAnalysis"
        @go-processing="onGoProcessing"
        @delete-dataset="onDeleteDataSet"
        @export-dataset="onExportDataSet"
        @copy-dataset="onCopyDataSet"
        @upload="showUploadModal = true"
      />

      <ProfilePanel v-else-if="currentTab === 'profile'" />
    </div>

    <UploadDataDialog
      v-if="showUploadModal"
      :drag-hover="dragHover"
      @close="showUploadModal = false"
      @choose-file="dataInputRef?.click()"
      @drop-file="onDropFile"
      @update:drag-hover="dragHover = $event"
    />

    <ConfirmDialog
      v-if="confirmDialog.visible"
      :dialog="confirmDialog"
      @close="closeConfirmDialog"
      @confirm="confirmDeleteAction"
      @update-suppress="confirmDialog.suppressForHour = $event"
    />

    <RenameDialog
      v-if="renameDialog.visible"
      :dialog="renameDialog"
      @close="closeRenameDialog"
      @submit="submitRenameDialog"
      @update-value="renameDialog.value = $event"
    />

    <AiAssistant ref="aiRef" :context="aiContext" />
  </div>
</template>

<script setup>
import { defineAsyncComponent, ref, computed } from 'vue'
import TopBar from '../components/layout/TopBar.vue'
import TaskCenter from '../components/layout/TaskCenter.vue'
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

const AnalysisPanel = defineAsyncComponent(() => import('../components/analysis/AnalysisPanel.vue'))
const MyDataPanel = defineAsyncComponent(() => import('../components/my-data/MyDataPanel.vue'))
const DataProcessingPanel = defineAsyncComponent(() => import('../data-processing/DataProcessingPanel.vue'))
const ProfilePanel = defineAsyncComponent(() => import('../components/profile/ProfilePanel.vue'))
const AiAssistant = defineAsyncComponent(() => import('../components/AiAssistant.vue'))

const dataInputRef = ref(null)
const aiRef = ref(null)

const currentTab = ref('analysis')
const sessionId = ref('')
const hasData = ref(false)
const dataFileName = ref('')
const showUploadModal = ref(false)
const dragHover = ref(false)
const taskCenterOpen = ref(false)
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
const showVariablePanel = computed(() => (
  hasData.value
  && !!activeMethodMeta.value
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
  folders,
  loadAllDataSets,
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
  activeJobCount,
  clearCompletedTaskJobs,
  handleTrackedJobProgress,
  onCancelTaskJob,
  onRetryTaskJob,
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
  toggleTaskCenter,
} = useWorkspaceUiState({
  activeHistoryIdx,
  activeMethodKey,
  aiRef,
  analysisReportVisible,
  clearCurrentAnalysis,
  currentResults,
  selectedVars,
  taskCenterOpen,
})

const onChangeVariableType = variableActions.changeType
const onDeleteVariable = variableActions.deleteVariable
const onRenameVariable = variableActions.renameVariable
const onRenameVariablesBatch = variableActions.renameBatch
</script>
