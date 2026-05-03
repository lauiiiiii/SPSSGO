<template>
  <div class="ap-sec ap-sec--table">
    <div class="ap-sec-head">
      <span class="ap-sec-head-title">{{ title }}</span>
      <button v-if="copyable" class="ap-sec-copy" @click="$emit('copy-table', section, $event)">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
        <span class="ap-sec-copy-txt">复制</span>
      </button>
    </div>
    <div class="ap-table-wrap" v-if="section.headers?.length">
      <table class="tlt">
        <thead><tr><th v-for="(header, headerIndex) in section.headers" :key="headerIndex">{{ header }}</th></tr></thead>
        <tbody><tr v-for="(row, rowIndex) in section.rows" :key="rowIndex"><td v-for="(cell, cellIndex) in row" :key="cellIndex" :class="cellClass(cell)">{{ cell }}</td></tr></tbody>
      </table>
    </div>
    <p v-if="section.note" class="ap-sec-note">{{ section.note }}</p>
    <div v-if="section.description" class="ap-sec-desc">{{ section.description }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cellClass: { type: Function, required: true },
  copyable: { type: Boolean, default: true },
  section: { type: Object, required: true },
})

defineEmits(['copy-table'])

const title = computed(() => props.section.title || props.section.name)
</script>
