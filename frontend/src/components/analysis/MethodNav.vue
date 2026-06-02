<template>
  <aside class="method-nav">
    <div class="mn-header">
      <input
        class="mn-search"
        v-model="search"
        placeholder="搜索分析方法..."
      />
    </div>
    <div class="mn-list">
      <div
        v-for="cat in filteredCategories"
        :key="cat.key"
        class="mn-category"
      >
        <div class="mn-cat-header" @click="toggleCat(cat.key)">
          <svg class="mn-cat-arrow" :class="{ open: expanded[cat.key] }" viewBox="0 0 16 16" fill="none">
            <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ cat.label }}</span>
          <span v-if="cat.hot" class="mn-hot">HOT</span>
        </div>
        <div class="mn-items" v-show="expanded[cat.key]">
          <div
            v-for="m in cat.methods"
            :key="m.key"
            class="mn-item"
            :class="{ active: m.key === activeMethod, 'mn-item--reserved': m.reserved }"
            @click="$emit('select', m.key)"
          >
            <span class="mn-item-label">{{ m.label }}</span>
            <span v-if="m.statusLabel" class="mn-item-status">{{ m.statusLabel }}</span>
          </div>
        </div>
      </div>
      <div v-if="!filteredCategories.length" class="hp-empty" style="padding:16px 8px">
        未找到匹配的方法
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { filterMethodCategories } from '../../utils/methodNavigation.js'

const props = defineProps({
  methods: { type: Object, default: () => ({}) },
  categories: { type: Array, default: () => [] },
  activeMethod: { type: String, default: '' },
})
defineEmits(['select'])

const search = ref('')
const expanded = reactive({})

// Auto-expand first category
if (props.categories.length) {
  for (const cat of props.categories) {
    expanded[cat.key] = !!cat.hot
  }
}

function toggleCat(key) {
  expanded[key] = !expanded[key]
}

const filteredCategories = computed(() => {
  const categories = filterMethodCategories({
    categories: props.categories,
    methods: props.methods,
    query: search.value,
  })
  if (search.value.trim()) {
    for (const category of categories) {
      if (!expanded[category.key]) expanded[category.key] = true
    }
  }
  return categories
})
</script>
