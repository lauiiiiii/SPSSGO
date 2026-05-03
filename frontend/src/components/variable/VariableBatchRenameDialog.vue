<template>
  <teleport to="body">
    <div v-if="visible" class="vp-modal-mask" @click.self="$emit('close')">
      <div class="vp-batch-modal">
        <div class="vp-modal-head">
          <h3>批量命名</h3>
          <button class="vp-modal-close" type="button" @click="$emit('close')">×</button>
        </div>
        <div class="vp-batch-table-wrap">
          <table class="vp-batch-table">
            <thead>
              <tr>
                <th>原名称</th>
                <th>新名称（支持Ctrl+V批量粘贴）</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in rows" :key="row.name">
                <td>{{ row.name }}</td>
                <td>
                  <input
                    v-model="row.newName"
                    class="vp-batch-input"
                    :class="isChanged(row) ? 'vp-batch-input--changed' : 'vp-batch-input--unchanged'"
                    @focus="$event.target.select()"
                    @paste="onPaste($event, idx)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
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
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'submit'])

const rows = ref([])

watch(
  () => [props.visible, props.variables],
  () => {
    if (!props.visible) return
    rows.value = props.variables.map(v => ({
      name: v.name,
      newName: v.display_name || v.name,
    }))
  },
  { immediate: true }
)

function isChanged(row) {
  return String(row?.newName || '').trim() !== row?.name
}

function onPaste(e, startIdx) {
  const text = e.clipboardData?.getData('text')
  if (!text || (!text.includes('\n') && !text.includes('\t'))) return
  e.preventDefault()
  const values = text
    .split(/\r?\n/)
    .map(line => line.split('\t')[0].trim())
    .filter(Boolean)
  values.forEach((value, offset) => {
    const row = rows.value[startIdx + offset]
    if (row) row.newName = value
  })
}

function submit() {
  const changes = rows.value
    .map(row => ({ oldName: row.name, newName: String(row.newName || '').trim() }))
    .filter(row => row.newName && row.oldName !== row.newName)
  const names = changes.map(row => row.newName)
  if (new Set(names).size !== names.length) {
    alert('新名称不能重复')
    return
  }
  emit('submit', changes)
}
</script>
