import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useGlobalTooltip() {
  const tooltip = ref({ visible: false, text: '', x: 0, y: 0 })

  function show(el) {
    const text = el.getAttribute('data-tooltip')
    if (!text) return
    const rect = el.getBoundingClientRect()
    tooltip.value = {
      visible: true,
      text,
      x: rect.left + rect.width / 2,
      y: rect.top,
    }
  }

  function hide() {
    tooltip.value.visible = false
  }

  function onOver(e) {
    const el = e.target?.closest?.('[data-tooltip]')
    if (el) show(el)
    else hide()
  }

  function onOut(e) {
    if (!e.relatedTarget?.closest?.('[data-tooltip]')) hide()
  }

  onMounted(() => {
    document.addEventListener('mouseover', onOver)
    document.addEventListener('mouseout', onOut)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('mouseover', onOver)
    document.removeEventListener('mouseout', onOut)
  })

  return { tooltip }
}
