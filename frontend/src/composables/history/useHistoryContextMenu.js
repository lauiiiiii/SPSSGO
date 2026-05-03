import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { positionFloatingMenuFromPoint, positionFloatingMenuFromRect } from '../../utils/floatingMenu.js'

export function useHistoryContextMenu({ expanded, rootRef }) {
  const hoveredIdx = ref(-1)
  const menuIdx = ref(-1)
  const menuTop = ref(0)
  const menuLeft = ref(0)

  const menuStyle = computed(() => ({
    top: `${menuTop.value}px`,
    left: `${menuLeft.value}px`,
  }))

  function closeMenu() {
    menuIdx.value = -1
  }

  function toggleMenu(idx, event) {
    if (menuIdx.value === idx) {
      closeMenu()
      return
    }
    menuIdx.value = idx
    const position = positionFloatingMenuFromRect(event.currentTarget.getBoundingClientRect())
    menuLeft.value = position.left
    menuTop.value = position.top
  }

  function openContextMenu(idx, event) {
    hoveredIdx.value = idx
    menuIdx.value = idx
    const position = positionFloatingMenuFromPoint(event.clientX, event.clientY)
    menuLeft.value = position.left
    menuTop.value = position.top
  }

  function onLeaveChip(idx) {
    if (hoveredIdx.value === idx && menuIdx.value !== idx) {
      hoveredIdx.value = -1
    }
  }

  function handleWindowPointerDown(event) {
    const target = event.target

    if (menuIdx.value >= 0) {
      if (!target?.closest?.('.hs-hover-menu') && !target?.closest?.('.hs-chip-more')) {
        closeMenu()
      }
    }

    if (expanded.value && rootRef.value && !rootRef.value.contains(target)) {
      expanded.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('pointerdown', handleWindowPointerDown)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('pointerdown', handleWindowPointerDown)
  })

  return {
    closeMenu,
    hoveredIdx,
    menuIdx,
    menuStyle,
    onLeaveChip,
    openContextMenu,
    toggleMenu,
  }
}
