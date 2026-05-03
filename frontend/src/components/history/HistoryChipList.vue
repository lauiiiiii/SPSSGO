<template>
  <div class="hs-card" :class="{ expanded }">
    <div class="hs-chip-wrap" :class="{ expanded }">
      <div
        v-for="(item, idx) in items"
        :key="idx"
        class="hs-chip-item"
        @mouseenter="$emit('hover', idx)"
        @mouseleave="$emit('leave', idx)"
      >
        <button
          class="hs-chip"
          :class="{ active: idx === activeIndex }"
          :title="formatHistoryChipTitle(item)"
          @click="$emit('select', idx)"
          @contextmenu.prevent="$emit('open-context-menu', idx, $event)"
        >
          <span class="hs-chip-inner">
            <span class="hs-chip-serial">N{{ items.length - idx }}</span>
            <span class="hs-chip-text">{{ item.name }}</span>
          </span>
        </button>

        <button
          v-if="hoveredIdx === idx || menuIdx === idx"
          class="hs-chip-more"
          @click.stop="$emit('toggle-menu', idx, $event)"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <circle cx="3" cy="7" r="1.2" fill="currentColor" />
            <circle cx="7" cy="7" r="1.2" fill="currentColor" />
            <circle cx="11" cy="7" r="1.2" fill="currentColor" />
          </svg>
        </button>
      </div>
    </div>

    <div class="hs-side">
      <button
        v-if="items.length > collapsedLimit"
        class="hs-round-btn"
        :title="expanded ? '收起结果' : '展开结果'"
        @click="$emit('toggle-expanded')"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            :d="expanded ? 'M4 10l4-4 4 4' : 'M4 6l4 4 4-4'"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { formatHistoryChipTitle } from '../../utils/historyItemMeta.js'

defineProps({
  activeIndex: { type: Number, default: -1 },
  collapsedLimit: { type: Number, default: 8 },
  expanded: { type: Boolean, default: false },
  hoveredIdx: { type: Number, default: -1 },
  items: { type: Array, default: () => [] },
  menuIdx: { type: Number, default: -1 },
})

defineEmits([
  'hover',
  'leave',
  'open-context-menu',
  'select',
  'toggle-expanded',
  'toggle-menu',
])
</script>
