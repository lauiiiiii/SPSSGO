<template>
  <div class="formula-block-shell">
    <div class="formula-block-toolbar">
      <div class="formula-block-tabs" role="tablist" aria-label="公式视图切换">
        <button
          class="formula-block-tab"
          :class="{ active: activeView === 'latex' }"
          type="button"
          role="tab"
          :aria-selected="activeView === 'latex'"
          @click="activeView = 'latex'"
        >
          LaTeX
        </button>
        <button
          class="formula-block-tab"
          :class="{ active: activeView === 'visual' }"
          type="button"
          role="tab"
          :aria-selected="activeView === 'visual'"
          @click="activeView = 'visual'"
        >
          Visual
        </button>
      </div>

      <button class="formula-block-action" type="button" @click="copyFormula">
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>

    <div v-if="activeView === 'visual'" class="formula-block" v-html="renderedFormula"></div>
    <pre v-else class="formula-source"><code>{{ normalizedFormula }}</code></pre>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useClipboardCopy } from '../../composables/shared/useClipboardCopy.js'
import { normalizeFormula, renderFormulaHtml } from '../../utils/formulaRender.js'
import 'katex/dist/katex.min.css'

const props = defineProps({
  formula: {
    type: String,
    default: '',
  },
})

const activeView = ref('visual')
const { copied, copyText } = useClipboardCopy()

const normalizedFormula = computed(() => normalizeFormula(props.formula))
const renderedFormula = computed(() => renderFormulaHtml(normalizedFormula.value))

async function copyFormula() {
  await copyText(normalizedFormula.value)
}
</script>

<style scoped>
.formula-block-shell {
  position: relative;
  border: 1px solid #edf2f7;
  border-radius: 12px;
  background: #fff;
}

.formula-block-toolbar {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.formula-block-tabs {
  display: inline-flex;
  align-items: center;
  padding: 2px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.formula-block-tab {
  min-width: 54px;
  height: 26px;
  padding: 0 10px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #667085;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
}

.formula-block-tab.active {
  background: #f5f8ff;
  color: #175cd3;
  font-weight: 600;
}

.formula-block-action {
  height: 30px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.94);
  color: #475467;
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.formula-block-action:hover {
  border-color: #cdd8e5;
  color: #1d4ed8;
  background: #fff;
}

.formula-block {
  overflow-x: auto;
  padding: 52px 20px 28px;
  min-height: 132px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.formula-block :deep(.katex-display) {
  margin: 0;
}

.formula-source {
  margin: 0;
  padding: 50px 18px 18px;
  overflow-x: auto;
  background: #ffffff;
  color: #334155;
  font-size: 12px;
  line-height: 1.7;
}

.formula-source code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  white-space: pre;
}
</style>
