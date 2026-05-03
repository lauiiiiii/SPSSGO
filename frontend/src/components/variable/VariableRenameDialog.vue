<template>
  <teleport to="body">
    <div v-if="visible && variable" class="vp-modal-mask" @click.self="$emit('close')">
      <div class="vp-single-modal">
        <div class="vp-modal-head">
          <h3>重命名变量</h3>
          <button class="vp-modal-close" type="button" @click="$emit('close')">×</button>
        </div>
        <div class="vp-single-body">
          <label class="vp-single-label">原名称</label>
          <div class="vp-single-old">{{ variable.name }}</div>
          <label class="vp-single-label" for="vp-single-rename-input">新名称</label>
          <input
            id="vp-single-rename-input"
            ref="inputRef"
            v-model="newName"
            class="vp-single-input"
            @keydown.enter="submit"
            @keydown.esc="$emit('close')"
          />
        </div>
        <div class="vp-modal-actions">
          <button type="button" class="vp-modal-btn" @click="$emit('close')">取消</button>
          <button type="button" class="vp-modal-btn vp-modal-btn--primary" @click="submit">确认</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  variable: { type: Object, default: null },
})

const emit = defineEmits(['close', 'submit'])

const inputRef = ref(null)
const newName = ref('')

watch(
  () => [props.visible, props.variable],
  () => {
    if (!props.visible || !props.variable) return
    newName.value = props.variable.display_name || props.variable.name || ''
    nextTick(() => inputRef.value?.focus())
  },
  { immediate: true }
)

function submit() {
  const oldName = props.variable?.name || ''
  const nextName = String(newName.value || '').trim()
  if (!oldName || !nextName || oldName === nextName) {
    emit('close')
    return
  }
  emit('submit', { oldName, newName: nextName })
}
</script>
