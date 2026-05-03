<template>
  <div class="upload-overlay" @click.self="$emit('close')">
    <div class="upload-modal rename-modal">
      <div class="upload-modal-head">
        <span>{{ dialog.title }}</span>
        <button class="upload-modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="rename-modal-body">
        <label class="rename-modal-label" for="rename-history-input">分析结果名称</label>
        <input
          id="rename-history-input"
          ref="inputRef"
          :value="dialog.value"
          class="rename-modal-input"
          type="text"
          maxlength="200"
          @input="$emit('update-value', $event.target.value)"
          @keydown.enter.prevent="$emit('submit')"
        />
      </div>
      <div class="confirm-modal-actions">
        <button class="md-page-btn md-page-btn--ghost" @click="$emit('close')">取消</button>
        <button class="md-page-btn" @click="$emit('submit')">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  dialog: { type: Object, required: true },
})

defineEmits(['close', 'submit', 'update-value'])

const inputRef = ref(null)

watch(() => props.dialog.visible, async (visible) => {
  if (!visible) return
  await nextTick()
  inputRef.value?.focus()
  inputRef.value?.select()
})
</script>
