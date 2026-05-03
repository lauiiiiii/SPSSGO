<template>
  <div class="code-block-shell">
    <div class="code-block-toolbar">
      <div class="code-block-lang">{{ language }}</div>
      <button class="code-block-copy" type="button" @click="copyCode">
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>
    <pre class="code-block-body"><code>{{ code }}</code></pre>
  </div>
</template>

<script setup>
import { useClipboardCopy } from '../../composables/shared/useClipboardCopy.js'

const props = defineProps({
  code: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'Python',
  },
})

const { copied, copyText } = useClipboardCopy()

async function copyCode() {
  await copyText(props.code)
}
</script>

<style scoped>
.code-block-shell {
  border: 1px solid #edf2f7;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
}

.code-block-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 42px;
  padding: 10px 12px;
  border-bottom: 1px solid #edf2f7;
  background: #fcfdff;
}

.code-block-lang {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border: 1px solid #e4e7ec;
  border-radius: 999px;
  background: #fff;
  color: #475467;
  font-size: 12px;
  font-weight: 600;
}

.code-block-copy {
  height: 30px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fff;
  color: #475467;
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
}

.code-block-copy:hover {
  border-color: #cdd8e5;
  color: #1d4ed8;
}

.code-block-body {
  margin: 0;
  padding: 16px 18px;
  overflow-x: auto;
  background: #f8fafc;
  color: #1f2937;
  font-size: 12.5px;
  line-height: 1.85;
}

.code-block-body code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  white-space: pre;
}
</style>
