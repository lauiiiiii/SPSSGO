<template>
  <div class="mydata-panel" @click="closeMenu">
    <div class="md-content">
      <div class="md-page-toolbar">
        <div class="md-page-toolbar-left">
          <div class="md-page-title">本地数据</div>
          <div class="md-page-summary">共 {{ allDataSets.length }} 份数据</div>
        </div>
        <div class="md-page-toolbar-actions">
          <button class="md-page-btn" @click.stop="$emit('upload')">
            <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M8 10.5V2.5M5 5.5l3-3 3 3M2.5 12.5v1h11v-1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            上传数据
          </button>
          <button class="md-page-btn md-page-btn--ghost" @click.stop="showNewFolder = true">
            <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
            新建文件夹
          </button>
        </div>
      </div>

      <!-- 当前数据概览条 -->
      <MyDataCurrentBar
        :current-session-id="currentSessionId"
        :data-file-name="currentDataSetName"
        :total-rows="totalRows"
        :variable-count="variables.length"
        @go-processing="$emit('go-processing', $event)"
        @go-analysis="$emit('go-analysis', $event)"
      />

      <!-- 分析记录 -->
      <div v-if="dataFileName" class="md-section">
        <div class="md-section-title">
          <span>分析记录</span>
          <span v-if="historyItems.length" class="md-section-count">{{ historyItems.length }}</span>
        </div>
        <div v-if="historyItems.length" class="md-tag-list">
          <button v-for="(item, idx) in historyItems" :key="idx"
            class="md-tag" :class="{ 'md-tag--active': expandedResultIdx === idx }"
            @click="toggleResult(idx)">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M2 6h12" stroke="currentColor" stroke-width="1" opacity=".5"/></svg>
            {{ item.name }}
          </button>
        </div>
        <div v-else class="md-empty-hint">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M2 6h12" stroke="currentColor" stroke-width="1" opacity=".5"/></svg>
          <span>该数据集暂无分析记录，右键数据卡片选择「数据分析」开始</span>
        </div>

        <!-- 内联展开的分析结果 -->
        <MyDataResultExpand
          v-if="expandedResultIdx >= 0 && expandedResult"
          :result="expandedResult"
          :results="displayExpandedResults"
          @close="closeExpandedResult"
        />
      </div>

      <!-- 全部数据 -->
      <div class="md-section">
        <div class="md-section-title">
          <span>全部数据</span>
          <span v-if="allDataSets.length" class="md-section-count">{{ allDataSets.length }}</span>
          <button class="md-toolbar-btn" @click.stop="showNewFolder = true" title="新建文件夹">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
            +
          </button>
        </div>

        <!-- 新建文件夹 -->
        <div v-if="showNewFolder" class="md-new-folder">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="md-folder-icon-sm"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
          <input ref="newFolderInput" v-model="newFolderName" class="md-inline-input" placeholder="文件夹名称"
            @keydown.enter="confirmNewFolder" @keydown.escape="showNewFolder = false" @blur="confirmNewFolder" />
        </div>

        <!-- 文件夹卡片网格 -->
        <div v-if="folders.length" class="md-card-grid">
          <MyDataFolderCard
            v-for="folder in folders"
            :key="folder.id"
            v-model="renamingValue"
            :drop-active="activeFolderDropId === folder.id"
            :file-count="folderDataSets(folder).length"
            :folder="folder"
            :open="!!openFolders[folder.id]"
            :renaming="renamingFolderId === folder.id"
            @toggle="toggleFolder"
            @open-menu="openFolderMenu"
            @card-drag-over="onFolderCardDragOver"
            @card-drag-leave="onFolderCardDragLeave"
            @drop-card="onDropToFolderCard"
            @confirm-rename="confirmRenameFolder"
            @cancel-rename="renamingFolderId = ''"
          />
        </div>

        <!-- 展开的文件夹内容 -->
        <div v-for="folder in folders" :key="'body-'+folder.id">
          <div v-if="openFolders[folder.id]" class="md-folder-expand" :class="{ 'md-folder-expand--active': activeFolderDropId === folder.id }">
            <div class="md-folder-expand-head">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="md-folder-icon-sm"><path d="M1 4h6l2-2h6v12H1V4z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" fill="#fef3c7"/></svg>
              <span>{{ folder.name }}</span>
              <button class="md-folder-close" @click="openFolders[folder.id] = false">&times;</button>
            </div>
            <div
              class="md-folder-dropzone"
              @dragover.prevent="onFolderBodyDragOver(folder.id)"
              @dragleave="onFolderBodyDragLeave($event, folder.id)"
              @drop.prevent="onDropToFolderBody($event, folder.id)"
            >
            <div v-if="!folderDataSets(folder).length" class="md-folder-empty">拖拽数据卡片到文件夹即可归类</div>
            <div class="md-card-grid">
              <MyDataSetCard
                v-for="ds in folderDataSets(folder)"
                :key="ds.sessionId"
                v-model="renamingValue"
                :data-set="ds"
                :format-date="formatDate"
                :in-folder="true"
                :renaming="renamingDsId === ds.sessionId"
                @switch="$emit('switch-session', $event)"
                @open-menu="openDsMenu"
                @open-menu-button="openDsMenuByButton"
                @drag-start="onDragStart"
                @confirm-rename="confirmRenameDs"
                @cancel-rename="renamingDsId = ''"
              />
            </div>
            </div>
          </div>
        </div>

        <!-- 未归类数据卡片 -->
        <div
          class="md-ungrouped-dropzone"
          :class="{ 'md-ungrouped-dropzone--active': ungroupedDropActive }"
          @dragover.prevent="onUngroupedDragOver"
          @dragleave="onUngroupedDragLeave"
          @drop.prevent="onDropToUngrouped"
        >
          <div v-if="ungroupedDataSets.length" class="md-card-grid" style="margin-top:8px">
          <MyDataSetCard
            v-for="ds in ungroupedDataSets"
            :key="ds.sessionId"
            v-model="renamingValue"
            :data-set="ds"
            :format-date="formatDate"
            :renaming="renamingDsId === ds.sessionId"
            @switch="$emit('switch-session', $event)"
            @open-menu="openDsMenu"
            @open-menu-button="openDsMenuByButton"
            @drag-start="onDragStart"
            @confirm-rename="confirmRenameDs"
            @cancel-rename="renamingDsId = ''"
          />
        </div>
          <div v-else class="md-ungrouped-space"></div>
        </div>

        <div v-if="!allDataSets.length" class="md-empty">暂无历史数据</div>
      </div>
    </div>

    <MyDataContextMenu
      :context-menu="contextMenu"
      :folders="folders"
      @start-rename-ds="startRenameDs"
      @start-rename-folder="startRenameFolder"
      @delete-folder="deleteFolder"
      @move-ds-to-folder="moveDsToFolder"
      @go-processing="emitDsAction('go-processing', $event)"
      @go-analysis="emitDsAction('go-analysis', $event)"
      @export-dataset="emitDsAction('export-dataset', $event)"
      @copy-dataset="emitDsAction('copy-dataset', $event)"
      @delete-dataset="emitDsAction('delete-dataset', $event)"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MyDataContextMenu from './MyDataContextMenu.vue'
import MyDataCurrentBar from './MyDataCurrentBar.vue'
import MyDataFolderCard from './MyDataFolderCard.vue'
import MyDataResultExpand from './MyDataResultExpand.vue'
import MyDataSetCard from './MyDataSetCard.vue'
import { useExpandedResults } from '../../composables/data/useExpandedResults.js'
import { useMyDataFolders } from '../../composables/data/useMyDataFolders.js'
import { formatShortDateTime } from '../../utils/dateFormat.js'

const props = defineProps({
  dataFileName: { type: String, default: '' },
  totalRows: { type: Number, default: 0 },
  variables: { type: Array, default: () => [] },
  historyItems: { type: Array, default: () => [] },
  allDataSets: { type: Array, default: () => [] },
  currentSessionId: { type: String, default: '' },
  folders: { type: Array, default: () => [] },
})
const emit = defineEmits([
  'open-result', 'switch-session', 'create-folder', 'delete-folder',
  'rename-folder', 'move-to-folder', 'rename-dataset',
  'go-analysis', 'go-processing', 'delete-dataset',
  'export-dataset', 'copy-dataset', 'upload',
])

const currentDataSetName = computed(() => {
  const current = props.allDataSets.find(item => item.sessionId === props.currentSessionId)
  return current?.topic || current?.fileName || props.dataFileName
})

const {
  closeExpandedResult,
  displayExpandedResults,
  expandedResult,
  expandedResultIdx,
  toggleResult,
} = useExpandedResults(props)
const {
  activeFolderDropId,
  closeMenu,
  confirmNewFolder,
  confirmRenameDs,
  confirmRenameFolder,
  contextMenu,
  deleteFolder,
  folderDataSets,
  moveDsToFolder,
  newFolderInput,
  newFolderName,
  onDragStart,
  onDropToFolderBody,
  onDropToFolderCard,
  onDropToUngrouped,
  onFolderBodyDragLeave,
  onFolderBodyDragOver,
  onFolderCardDragLeave,
  onFolderCardDragOver,
  onUngroupedDragLeave,
  onUngroupedDragOver,
  openDsMenu,
  openDsMenuByButton,
  openFolderMenu,
  openFolders,
  renamingDsId,
  renamingFolderId,
  renamingValue,
  showNewFolder,
  startRenameDs,
  startRenameFolder,
  toggleFolder,
  ungroupedDataSets,
  ungroupedDropActive,
} = useMyDataFolders(props, emit)

function formatDate(ts) {
  return formatShortDateTime(ts)
}

function emitDsAction(eventName, sessionId) {
  emit(eventName, sessionId)
  closeMenu()
}

</script>
