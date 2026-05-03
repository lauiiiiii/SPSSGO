<template>
  <section ref="rootRef" class="history-strip">
    <HistoryChipList
      v-if="items.length"
      :active-index="activeIndex"
      :collapsed-limit="collapsedLimit"
      :expanded="expanded"
      :hovered-idx="hoveredIdx"
      :items="items"
      :menu-idx="menuIdx"
      @hover="hoveredIdx = $event"
      @leave="onLeaveChip"
      @open-context-menu="openContextMenu"
      @select="selectHistory"
      @toggle-expanded="expanded = !expanded"
      @toggle-menu="toggleMenu"
    />

    <div v-else class="hs-empty">
      尚无分析记录，执行分析后会显示在这里
    </div>
  </section>

  <HistoryContextMenu
    :visible="menuIdx >= 0"
    :menu-style="menuStyle"
    @rename="emitRename"
    @delete="emitDelete"
  />
</template>

<script setup>
import { ref } from 'vue'
import HistoryChipList from './HistoryChipList.vue'
import HistoryContextMenu from './HistoryContextMenu.vue'
import { useHistoryContextMenu } from '../../composables/history/useHistoryContextMenu.js'
import '../../styles/history-panel.css'

const props = defineProps({
  items: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: -1 },
  hasAnyItems: { type: Boolean, default: false },
})

const expanded = ref(false)
const collapsedLimit = 8
const rootRef = ref(null)

const emit = defineEmits(['select', 'new-analysis', 'rename', 'delete'])
const {
  closeMenu,
  hoveredIdx,
  menuIdx,
  menuStyle,
  onLeaveChip,
  openContextMenu,
  toggleMenu,
} = useHistoryContextMenu({ expanded, rootRef })

function selectHistory(idx) {
  emit('select', idx)
  expanded.value = false
  closeMenu()
}

function emitRename() {
  if (menuIdx.value < 0) return
  emit('rename', menuIdx.value)
  closeMenu()
}

function emitDelete() {
  if (menuIdx.value < 0) return
  emit('delete', menuIdx.value)
  closeMenu()
}
</script>
