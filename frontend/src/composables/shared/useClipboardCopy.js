import { ref } from 'vue'

export function useClipboardCopy({ resetDelay = 1500 } = {}) {
  const copied = ref(false)

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(String(text || ''))
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, resetDelay)
      return true
    } catch {
      copied.value = false
      return false
    }
  }

  return {
    copied,
    copyText,
  }
}
