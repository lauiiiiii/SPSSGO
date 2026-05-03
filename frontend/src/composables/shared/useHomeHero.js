import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

export function useHomeHero(copies, intervalMs = 8000) {
  const heroCopyIndex = ref(0)
  let heroCopyTimer = null

  const activeHeroCopy = computed(() => copies[heroCopyIndex.value])

  onMounted(() => {
    heroCopyTimer = window.setInterval(() => {
      heroCopyIndex.value = (heroCopyIndex.value + 1) % copies.length
    }, intervalMs)
  })

  onBeforeUnmount(() => {
    if (heroCopyTimer) {
      window.clearInterval(heroCopyTimer)
      heroCopyTimer = null
    }
  })

  return {
    activeHeroCopy,
    heroCopyIndex,
  }
}
