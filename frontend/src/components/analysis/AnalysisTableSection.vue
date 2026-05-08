<template>
  <div class="ap-sec ap-sec--table" :class="{ 'ap-sec--table-inner-title': !showSectionHead }">
    <div v-if="showSectionHead" class="ap-sec-head">
      <div class="ap-sec-head-main">
        <span class="ap-sec-head-title">{{ title }}</span>
      </div>
      <button v-if="copyable" class="ap-sec-copy" @click="copyActiveTable($event)">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
        <span class="ap-sec-copy-txt">复制</span>
      </button>
    </div>
    <div class="ap-table-wrap" v-if="section.headers?.length">
      <div v-if="displayModes.length" class="ap-table-mode-toolbar">
        <div class="ap-table-mode-center">
          <span class="ap-table-mode-title">{{ displayModeTitle }}</span>
          <select v-model="selectedMode" class="ap-table-mode-select">
            <option
              v-for="mode in displayModes"
              :key="mode.key"
              :value="mode.key"
            >
              {{ mode.label }}
            </option>
          </select>
        </div>
        <button
          v-if="copyable"
          class="ap-sec-copy ap-table-mode-copy"
          @click="copyActiveTable($event)"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
          <span class="ap-sec-copy-txt">复制</span>
        </button>
      </div>
      <table class="tlt">
        <thead><tr><th v-for="(header, headerIndex) in section.headers" :key="headerIndex">{{ header }}</th></tr></thead>
        <tbody><tr v-for="(row, rowIndex) in activeRows" :key="rowIndex"><td v-for="(cell, cellIndex) in row" :key="cellIndex" :class="cellClass(cell)">{{ cell }}</td></tr></tbody>
      </table>
    </div>
    <p v-if="section.note" class="ap-sec-note">{{ section.note }}</p>
    <div v-if="section.description" class="ap-sec-desc">{{ section.description }}</div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  cellClass: { type: Function, required: true },
  copyable: { type: Boolean, default: true },
  section: { type: Object, required: true },
})

const emit = defineEmits(['copy-table'])

const title = computed(() => props.section.title || props.section.name)
const displayModeTitle = computed(() => props.section.displayModeTitle || title.value)
const displayModes = computed(() => props.section.displayModes || [])
const defaultMode = computed(() => props.section.defaultDisplayMode || displayModes.value[0]?.key || '')
const selectedMode = ref(defaultMode.value)
const showSectionHead = computed(() => displayModes.value.length === 0)

const activeRows = computed(() => {
  const mode = displayModes.value.find((item) => item.key === selectedMode.value)
  return mode?.rows || props.section.rows || []
})

watch(defaultMode, (nextMode) => {
  selectedMode.value = nextMode
})

function copyActiveTable(event) {
  emit('copy-table', { ...props.section, rows: activeRows.value }, event)
}
</script>
