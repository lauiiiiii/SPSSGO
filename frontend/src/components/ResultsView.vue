<template>
  <div>
    <div class="card" v-if="error && !results.length">
      <div class="error-box">{{ error }}</div>
      <div class="btn-group">
        <button class="btn btn-outline" @click="$emit('back')">&#8592; 返回修改计划</button>
        <button class="btn btn-primary" @click="$emit('retry')">重新执行</button>
      </div>
    </div>

    <div class="card" v-if="loading && !results.length" style="text-align: center; padding: 48px 24px">
      <div class="spinner" style="margin: 0 auto 16px"></div>
      <p style="color: #4a5568; font-size: 15px; margin: 0">{{ loadingMsg || '正在准备分析...' }}</p>
    </div>

    <template v-if="results.length">
      <div class="card" style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px">
        <div>
          <h2 style="border: none; margin: 0; padding: 0">
            分析结果（{{ loading ? '已完成 ' + results.length + ' 项，继续执行中...' : '共 ' + results.length + ' 项' }})
          </h2>
          <span v-if="mode" style="font-size: 12px; color: #718096; margin-top: 4px; display: block">
            执行模式：{{ mode === 'template' ? '模板引擎（快速）' : 'AI 代码生成' }}
          </span>
        </div>
        <div class="btn-group" style="margin: 0">
          <button class="btn btn-outline" @click="copyAll" :disabled="loading">
            {{ copyAllTip || '复制全部结果' }}
          </button>
          <button class="btn btn-outline" @click="showCode = !showCode" v-if="code">
            {{ showCode ? '隐藏配置' : '查看配置' }}
          </button>
          <button class="btn btn-success" :disabled="loading" @click="$emit('download')">下载 Word 文档</button>
        </div>
      </div>

      <div class="code-block" v-if="showCode && code">{{ code }}</div>

      <TransitionGroup name="result-fade" tag="div">
        <div class="result-card" v-for="(r, idx) in results" :key="'r-' + idx">
          <div class="result-card-header">
            <h3>{{ r.name }}</h3>
            <button class="copy-btn" @click="copySingle(r, idx)" :title="'复制此项结果'">
              {{ copyTips[idx] || '复制' }}
            </button>
          </div>
          <table class="three-line-table" v-if="r.headers && r.headers.length">
            <thead>
              <tr><th v-for="(h, hi) in r.headers" :key="hi">{{ h }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in r.rows" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
          <div class="description" v-if="r.description">{{ r.description }}</div>
        </div>
      </TransitionGroup>

      <div class="stream-status" v-if="loading">
        <div class="spinner-sm"></div>
        <span>{{ loadingMsg || '正在执行...' }}</span>
      </div>

      <div class="card" v-if="error && results.length">
        <div class="error-box">{{ error }}</div>
        <div class="btn-group">
          <button class="btn btn-primary" @click="$emit('retry')">重新执行</button>
        </div>
      </div>

      <div class="card" v-if="!loading">
        <h2>追加分析</h2>
        <div class="form-group">
          <textarea v-model="extra" placeholder="如：再帮我做一个信度分析 / 加一个中介效应检验"></textarea>
        </div>
        <button class="btn btn-primary" :disabled="loading" @click="onAdd">追加分析</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  error: { type: String, default: '' },
  code: { type: String, default: '' },
  mode: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  loadingMsg: { type: String, default: '' },
})

const emit = defineEmits(['back', 'retry', 'download', 'add-analysis'])

const showCode = ref(false)
const extra = ref('')
const copyTips = reactive({})
const copyAllTip = ref('')

function onAdd() {
  if (!extra.value.trim()) return
  emit('add-analysis', extra.value)
  extra.value = ''
}

function buildResultHtml(r) {
  const thStyle = 'padding:8px 12px;text-align:center;font-weight:bold;font-size:10.5pt;font-family:"Times New Roman","宋体",serif'
  const tdStyle = 'padding:6px 12px;text-align:center;font-size:10.5pt;font-family:"Times New Roman","宋体",serif'
  let html = ''
  if (r.headers && r.headers.length && r.rows && r.rows.length) {
    html += '<table style="border-collapse:collapse;width:100%;margin:8px 0">'
    html += `<thead><tr style="border-top:2px solid #000;border-bottom:1px solid #000">`
    for (const h of r.headers) html += `<th style="${thStyle}">${h}</th>`
    html += '</tr></thead><tbody>'
    r.rows.forEach((row, ri) => {
      const last = ri === r.rows.length - 1
      html += `<tr style="${last ? 'border-bottom:2px solid #000' : ''}">`
      for (const cell of row) html += `<td style="${tdStyle}">${cell}</td>`
      html += '</tr>'
    })
    html += '</tbody></table>'
  }
  if (r.description) {
    html += `<p style="text-indent:2em;line-height:1.8;font-size:12pt;font-family:'Times New Roman','宋体',serif;margin:8px 0">${r.description}</p>`
  }
  return html
}

function buildResultText(r) {
  let text = ''
  if (r.headers && r.headers.length && r.rows && r.rows.length) {
    text += r.headers.join('\t') + '\n'
    for (const row of r.rows) text += row.join('\t') + '\n'
  }
  if (r.description) {
    text += '\n' + r.description + '\n'
  }
  return text
}

async function copyToClipboard(html, plain, tipSetter, tipKey) {
  try {
    await navigator.clipboard.write([
      new ClipboardItem({
        'text/html': new Blob([html], { type: 'text/html' }),
        'text/plain': new Blob([plain], { type: 'text/plain' }),
      })
    ])
    tipSetter(tipKey, '已复制 ✓')
  } catch {
    try {
      await navigator.clipboard.writeText(plain)
      tipSetter(tipKey, '已复制 ✓')
    } catch {
      tipSetter(tipKey, '复制失败')
    }
  }
  setTimeout(() => tipSetter(tipKey, ''), 2000)
}

function copySingle(r, idx) {
  const html = buildResultHtml(r)
  const plain = buildResultText(r)
  copyToClipboard(html, plain, (k, v) => { copyTips[k] = v }, idx)
}

function copyAll() {
  let html = '', plain = ''
  for (const r of props.results) {
    if (r.name) html += `<h3>${r.name}</h3>`
    if (r.name) plain += r.name + '\n'
    html += buildResultHtml(r)
    plain += buildResultText(r) + '\n'
  }
  copyToClipboard(html, plain, (_, v) => { copyAllTip.value = v }, null)
}
</script>
