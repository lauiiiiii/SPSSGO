<!-- 公开分享页，只渲染静态报告快照，别把登录态和工作台编排塞进来。 -->
<template>
  <div class="shared-report-shell">
    <header class="shared-report-topbar">
      <a href="/" class="shared-report-brand">
        <img src="/logo.png" alt="SPSSGO" />
        <span class="shared-report-brand-copy">
          <strong>分享报告</strong>
          <span>SPSSGO Report Share</span>
        </span>
      </a>
      <div class="shared-report-topbar-actions">
        <a href="/login?redirect=%2Fworkspace" class="shared-report-entry">进入工作台</a>
      </div>
    </header>

    <main class="shared-report-main">
      <section v-if="loading" class="shared-report-stage">
        <div class="shared-report-state-card shared-report-state-card--loading">
          <div class="shared-report-state-badge">正在连接</div>
          <div class="shared-report-state-orb">
            <span class="shared-report-spinner"></span>
          </div>
          <h1 class="shared-report-state-title">报告加载中</h1>
          <p class="shared-report-state-desc">我们正在读取这份分享快照，通常只需要几秒。</p>
        </div>
      </section>

      <section v-else-if="requiresPassword" class="shared-report-stage">
        <div class="shared-report-state-card shared-report-state-card--secure">
          <div class="shared-report-state-badge">安全查阅</div>
          <h1 class="shared-report-state-title">{{ reportTitle }}</h1>
          <p class="shared-report-state-desc">这份分享报告已加密。输入查阅口令后即可查看完整内容。</p>
          <div class="shared-report-access-form">
            <input
              v-model="sharePassword"
              class="shared-report-access-input"
              type="password"
              maxlength="64"
              placeholder="请输入查阅口令"
              @keyup.enter="unlockSharedReport"
            />
            <button
              type="button"
              class="shared-report-access-btn"
              :disabled="passwordLoading"
              @click="unlockSharedReport"
            >
              {{ passwordLoading ? '验证中...' : '查看报告' }}
            </button>
          </div>
          <div class="shared-report-access-tip">查阅口令由分享者单独提供，输入正确后才能查看。</div>
          <div v-if="error" class="shared-report-access-error">{{ error }}</div>
        </div>
      </section>

      <section v-else-if="error" class="shared-report-stage">
        <div class="shared-report-state-card shared-report-state-card--error">
          <div class="shared-report-state-badge shared-report-state-badge--error">链接不可用</div>
          <div class="shared-report-state-orb shared-report-state-orb--error">!</div>
          <h1 class="shared-report-state-title">{{ errorTitle }}</h1>
          <p class="shared-report-state-desc">{{ error }}</p>
          <div class="shared-report-state-actions">
            <a href="/" class="shared-report-link-secondary">返回首页</a>
            <a href="/login?redirect=%2Fworkspace" class="shared-report-entry">进入工作台</a>
          </div>
        </div>
      </section>

      <div v-else class="shared-report-stage shared-report-stage--report">
        <div class="shared-report-report-frame">
          <AnalysisReportPage
            :ai-loading="false"
            :ai-result="aiResult"
            :allow-ai-request="false"
            :calc-box="calcBox"
            :calc-grouped-box="calcGroupedBox"
            :calc-category-bar="calcCategoryBar"
            :calc-category-pie="calcCategoryPie"
            :calc-correspondence-map="calcCorrespondenceMap"
            :calc-crosstab="calcCrosstab"
            :calc-factor-heatmap="calcFactorHeatmap"
            :calc-hist="calcHist"
            :calc-metric-comparison="calcMetricComparison"
            :calc-normality-hist="calcNormalityHist"
            :calc-probability-plot="calcProbabilityPlot"
            :calc-scatter-plot="calcScatterPlot"
            :cell-class="cellClass"
            :chart-data-visible="chartDataVisible"
            :display-results="displayResults"
            :fmt-bin="fmtBin"
            :report-meta-tags="reportMetaTags"
            :report-title="reportTitle"
            :results="displayResults"
            :set-chart-ref="setChartRef"
            :show-copy-all="false"
            :show-edit-config="false"
            :show-export-actions="false"
            :show-share="false"
            @copy-table="copyTable"
            @hide-tip="hideTip"
            @move-tip="moveTip"
            @show-hist-tip="showHistTip"
            @show-box-tip="showBoxTip"
            @show-category-tip="showCategoryTip"
            @show-crosstab-tip="showCrosstabTip"
            @show-metric-tip="showMetricTip"
            @show-probability-tip="showProbabilityTip"
            @show-scatter-tip="showScatterTip"
            @download-chart="downloadChart"
            @copy-chart="copyChart"
            @toggle-chart-data="toggleChartData"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { accessReportShare, getReportShare } from '../api.js'
import AnalysisReportPage from '../components/analysis/AnalysisReportPage.vue'
import { useAnalysisCharts } from '../composables/analysis/useAnalysisCharts.js'
import {
  buildTableSectionCopyPayload,
  writeRichClipboard,
} from '../utils/reportExport.js'

const route = useRoute()

const loading = ref(true)
const error = ref('')
const aiResult = ref('')
const displayResults = ref([])
const reportMetaTags = ref([])
const reportTitle = ref('分享报告')
const requiresPassword = ref(false)
const passwordLoading = ref(false)
const sharePassword = ref('')
const activeShareToken = ref('')
const errorTitle = computed(() => {
  const text = String(error.value || '')
  if (text.includes('失效') || text.includes('过期')) return '链接已失效'
  if (text.includes('不存在')) return '报告不存在'
  return '暂时无法打开报告'
})

function normalizeShareAccessMessage(message, fallback = '分享报告加载失败') {
  const text = String(message || fallback).trim()
  return text.replaceAll('访问密码', '查阅口令')
}

const {
  calcBox,
  calcGroupedBox,
  calcCategoryBar,
  calcCategoryPie,
  calcCorrespondenceMap,
  calcCrosstab,
  calcFactorHeatmap,
  calcHist,
  calcMetricComparison,
  calcNormalityHist,
  calcProbabilityPlot,
  calcScatterPlot,
  chartDataVisible,
  copyChart,
  downloadChart,
  fmtBin,
  hideTip,
  moveTip,
  setChartRef,
  showBoxTip,
  showCategoryTip,
  showCrosstabTip,
  showHistTip,
  showMetricTip,
  showProbabilityTip,
  showScatterTip,
  toggleChartData,
} = useAnalysisCharts()

const cellClass = cell => ({
  'tlt-cell--danger': cell === '需要检查',
  'tlt-cell--success': cell === '较好',
})

async function copyTable(section, event) {
  const payload = buildTableSectionCopyPayload(section)
  await writeRichClipboard(payload)
  const button = event?.target?.closest?.('.ap-sec-copy')
  if (!button) return
  const textEl = button.querySelector('.ap-sec-copy-txt')
  if (!textEl) return
  textEl.textContent = '已复制'
  setTimeout(() => { textEl.textContent = '复制' }, 1500)
}

function applySharedReportPayload(data) {
  reportTitle.value = data.report_title || '分享报告'
  reportMetaTags.value = data.report_meta_tags || []
  displayResults.value = data.display_results || []
  aiResult.value = data.ai_result || ''
  requiresPassword.value = false
  error.value = displayResults.value.length ? '' : '分享报告内容为空'
}

async function loadSharedReport(shareToken) {
  const token = String(shareToken || '').trim()
  if (!token) {
    error.value = '分享链接不完整'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''
  aiResult.value = ''
  displayResults.value = []
  reportMetaTags.value = []
  reportTitle.value = '分享报告'
  requiresPassword.value = false
  passwordLoading.value = false
  sharePassword.value = ''
  activeShareToken.value = token

  try {
    const data = await getReportShare(token)
    reportTitle.value = data.report_title || '分享报告'
    if (data.requires_password) {
      requiresPassword.value = true
      return
    }
    applySharedReportPayload(data)
  } catch (err) {
    error.value = normalizeShareAccessMessage(err?.message, '分享报告加载失败')
  } finally {
    loading.value = false
  }
}

async function unlockSharedReport() {
  if (passwordLoading.value) return

  const token = String(activeShareToken.value || route.params.shareToken || '').trim()
  const password = String(sharePassword.value || '').trim()
  if (!password) {
    error.value = '请输入查阅口令'
    return
  }

  passwordLoading.value = true
  error.value = ''
  try {
    const data = await accessReportShare(token, password)
    applySharedReportPayload(data)
    sharePassword.value = ''
  } catch (err) {
    error.value = normalizeShareAccessMessage(err?.message, '访问分享报告失败')
  } finally {
    passwordLoading.value = false
  }
}

watch(
  () => route.params.shareToken,
  (shareToken) => {
    loadSharedReport(shareToken)
  },
  { immediate: true },
)
</script>
