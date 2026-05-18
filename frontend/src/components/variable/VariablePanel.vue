<template>
  <aside class="variable-panel">
    <div class="vp-header">
      <div class="vp-title-row">
        <span class="vp-title">选择变量</span>
      </div>
      <div class="vp-filter-tabs">
        <button class="vp-ftab" :class="{ active: filter === 'all' }" @click="filter = 'all'">全部</button>
        <button class="vp-ftab" :class="{ active: filter === 'numeric' }" @click="filter = 'numeric'">定量</button>
        <button class="vp-ftab" :class="{ active: filter === 'categorical' }" @click="filter = 'categorical'">定类</button>
        <button class="vp-ftab" :class="{ active: filter === 'text' }" @click="filter = 'text'">字符</button>
      </div>
      <input class="vp-search" v-model="searchQuery" placeholder="搜索变量名..." />
    </div>

    <div class="vp-list">
      <div v-if="!variables.length" class="vp-empty">
        请先上传数据文件
      </div>
      <div v-else-if="!filteredVars.length" class="vp-empty">
        无匹配变量
      </div>
      <VariableRow
        v-for="v in filteredVars"
        :key="v.name"
        :variable="v"
        :selected="selectedVars.includes(v.name)"
        :dragging="draggingVar === v.name"
        :menu-open="menuVariable?.name === v.name"
        @toggle="toggleSelect"
        @drag-start="onDragStart"
        @drag-end="onDragEnd"
        @open-menu="openMenu"
      />
    </div>

    <div class="vp-footer" v-if="variables.length">
      {{ filteredVars.length }} / {{ variables.length }} 个变量 · {{ totalRows }} 行
    </div>
  </aside>

  <VariableContextMenu
    :visible="Boolean(menuVariable)"
    :variable="menuVariable"
    :position="menuPosition"
    @close="closeMenu"
    @change-type="onMenuChangeType"
    @rename="openRenameDialog"
    @batch-rename="openBatchRenameDialog"
    @delete="onMenuDelete"
  />

  <VariableRenameDialog
    :visible="renameVisible"
    :variable="renameVariable"
    @close="closeRenameDialog"
    @submit="submitRename"
  />

  <VariableBatchRenameDialog
    :visible="batchRenameVisible"
    :variables="variables"
    @close="closeBatchRenameDialog"
    @submit="submitBatchRename"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import VariableBatchRenameDialog from './VariableBatchRenameDialog.vue'
import VariableContextMenu from './VariableContextMenu.vue'
import VariableRenameDialog from './VariableRenameDialog.vue'
import VariableRow from './VariableRow.vue'
import {
  buildVariableDragPayload,
  filterVariables,
  getShiftRangeNames,
  positionVariableMenu,
} from '../../utils/variableList.js'

const props = defineProps({
  variables: { type: Array, default: () => [] },
  totalRows: { type: Number, default: 0 },
  selectedVars: { type: Array, default: () => [] },
  usedVars: { type: Set, default: () => new Set() },
})
const emit = defineEmits(['select', 'deselect', 'select-range', 'drag-start', 'drag-end', 'change-type', 'delete-variable', 'rename-variable', 'rename-batch'])

const filter = ref('all')
const searchQuery = ref('')
const draggingVar = ref(null)
const lastClickedIdx = ref(-1)
const menuVariable = ref(null)
const menuPosition = ref({ top: 0, left: 0 })
const renameVisible = ref(false)
const renameVariable = ref(null)
const batchRenameVisible = ref(false)

const filteredVars = computed(() => {
  return filterVariables({
    variables: props.variables,
    usedVars: props.usedVars,
    typeFilter: filter.value,
    query: searchQuery.value,
  })
})

function toggleSelect(e, v) {
  const idx = filteredVars.value.findIndex(fv => fv.name === v.name)

  if (e.shiftKey && lastClickedIdx.value >= 0 && lastClickedIdx.value !== idx) {
    const rangeNames = getShiftRangeNames(filteredVars.value, lastClickedIdx.value, idx)
    emit('select-range', rangeNames)
  } else {
    if (props.selectedVars.includes(v.name)) {
      emit('deselect', v.name)
    } else {
      emit('select', v.name)
    }
  }
  lastClickedIdx.value = idx
}

function onDragStart(e, v) {
  draggingVar.value = v.name
  const payload = buildVariableDragPayload(v.name, props.selectedVars)
  const names = payload.split(',').filter(Boolean)
  e.dataTransfer.setData('text/plain', payload)
  e.dataTransfer.effectAllowed = 'copy'
  emit('drag-start', names)
}

function onDragEnd() {
  draggingVar.value = null
  emit('drag-end')
}

function openMenu(v, e) {
  menuVariable.value = v
  menuPosition.value = positionVariableMenu(e.currentTarget.getBoundingClientRect())
}

function closeMenu() {
  menuVariable.value = null
}

function onMenuChangeType(targetType) {
  if (!menuVariable.value) return
  emit('change-type', menuVariable.value.name, targetType)
  closeMenu()
}

function onMenuDelete() {
  if (!menuVariable.value) return
  emit('delete-variable', menuVariable.value.name)
  closeMenu()
}

function openRenameDialog() {
  if (!menuVariable.value) return
  renameVariable.value = menuVariable.value
  renameVisible.value = true
  closeMenu()
}

function closeRenameDialog() {
  renameVisible.value = false
  renameVariable.value = null
}

function submitRename(payload) {
  emit('rename-variable', payload.oldName, payload.newName)
  closeRenameDialog()
}

function openBatchRenameDialog() {
  batchRenameVisible.value = true
  closeMenu()
}

function closeBatchRenameDialog() {
  batchRenameVisible.value = false
}

function submitBatchRename(changes) {
  if (changes.length) emit('rename-batch', changes)
  closeBatchRenameDialog()
}
</script>
