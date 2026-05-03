// 这里只管分析报告分享状态和生成逻辑，别把报告渲染和工作台编排塞进来。
// 分享参数一变就清空旧链接，免得用户把旧配置下生成的链接继续发出去。
import { computed, ref, watch } from 'vue'

import { createReportShare } from '../../api.js'

const DEFAULT_SHARE_EXPIRY_DAYS = 7
const SHARE_CODE_CHARS = 'abcdefghjkmnpqrstuvwxyz23456789'

function buildAbsoluteShareUrl(path) {
  const value = String(path || '').trim()
  if (!value) return ''
  try {
    return new URL(value, window.location.origin).toString()
  } catch (_) {
    return value
  }
}

async function copyText(text) {
  const value = String(text || '').trim()
  if (!value) return false

  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value)
    return true
  }

  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', 'readonly')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  document.body.removeChild(textarea)
  return copied
}

function buildRandomShareCode(length = 4) {
  let result = ''
  for (let index = 0; index < length; index += 1) {
    const randomIndex = Math.floor(Math.random() * SHARE_CODE_CHARS.length)
    result += SHARE_CODE_CHARS[randomIndex]
  }
  return result
}

function normalizeShareMessage(message, fallback) {
  const text = String(message || fallback || '').trim()
  if (!text) return fallback || ''
  return text.replaceAll('访问密码', '查阅口令')
}

function buildShareCopyText({ reportTitle, shareUrl, sharePassword }) {
  const title = String(reportTitle || '分析报告').trim() || '分析报告'
  const url = String(shareUrl || '').trim()
  const password = String(sharePassword || '').trim()
  if (!url) return ''

  const lines = [
    `通过 SPSSGO 分享的分析报告：${title}`,
    password ? `链接: ${url} 查阅口令: ${password}` : `链接: ${url}`,
    password
      ? '复制这段内容后打开链接并输入查阅口令，即可查看完整报告。'
      : '复制这段内容后打开链接，即可查看完整报告。',
  ]
  return lines.join('\n')
}


function collectResultIds(results) {
  const ids = []
  const seen = new Set()
  for (const result of results || []) {
    const resultId = Number(result?.id || 0)
    if (!Number.isInteger(resultId) || resultId <= 0 || seen.has(resultId)) continue
    seen.add(resultId)
    ids.push(resultId)
  }
  return ids
}

export function useAnalysisShare({
  aiResult,
  displayResults,
  reportMetaTags,
  reportTitle,
  results,
  sessionId,
}) {
  const shareDialogVisible = ref(false)
  const shareLoading = ref(false)
  const shareError = ref('')
  const shareUrl = ref('')
  const copiedShareUrl = ref(false)
  const shareExpiryDays = ref(DEFAULT_SHARE_EXPIRY_DAYS)
  const sharePassword = ref('')
  const lastGeneratedSettingsKey = ref('')
  const shareText = computed(() => buildShareCopyText({
    reportTitle: reportTitle?.value,
    shareUrl: shareUrl.value,
    sharePassword: sharePassword.value,
  }))

  function buildSettingsKey() {
    return JSON.stringify({
      expiryDays: Number(shareExpiryDays.value) || DEFAULT_SHARE_EXPIRY_DAYS,
      password: String(sharePassword.value || ''),
    })
  }

  function resetGeneratedShare() {
    shareUrl.value = ''
    copiedShareUrl.value = false
  }

  function openShareDialog() {
    shareDialogVisible.value = true
    shareError.value = ''
    copiedShareUrl.value = false
  }

  function closeShareDialog() {
    shareDialogVisible.value = false
    shareLoading.value = false
    shareError.value = ''
    copiedShareUrl.value = false
  }

  async function generateShareLink() {
    if (shareLoading.value) return

    const currentSessionId = String(sessionId?.value || '').trim()
    if (!currentSessionId) {
      resetGeneratedShare()
      shareError.value = '当前会话不存在，暂时不能分享报告'
      return
    }

    if (!Array.isArray(displayResults?.value) || !displayResults.value.length) {
      resetGeneratedShare()
      shareError.value = '当前没有可分享的分析报告'
      return
    }

    shareLoading.value = true
    shareError.value = ''
    copiedShareUrl.value = false
    try {
      const data = await createReportShare(currentSessionId, {
        report_title: reportTitle?.value || '分析报告',
        report_meta_tags: reportMetaTags?.value || [],
        result_ids: collectResultIds(results?.value),
        display_results: displayResults.value,
        ai_result: aiResult?.value || '',
        expiry_days: Number(shareExpiryDays.value) || DEFAULT_SHARE_EXPIRY_DAYS,
        password: sharePassword.value || '',
      })
      shareUrl.value = buildAbsoluteShareUrl(data?.share_path)
      lastGeneratedSettingsKey.value = buildSettingsKey()
    } catch (error) {
      resetGeneratedShare()
      shareError.value = normalizeShareMessage(error?.message, '分享链接生成失败，请稍后重试')
    } finally {
      shareLoading.value = false
    }
  }

  function fillRandomSharePassword() {
    sharePassword.value = buildRandomShareCode()
  }

  async function copyShareUrl() {
    if (!shareText.value) {
      await generateShareLink()
      if (!shareText.value) return
    }

    shareError.value = ''
    try {
      const copied = await copyText(shareText.value)
      if (!copied) throw new Error('copy_failed')
      copiedShareUrl.value = true
    } catch (_) {
      copiedShareUrl.value = false
      shareError.value = '复制失败，请手动复制分享文案'
    }
  }

  watch([shareExpiryDays, sharePassword], () => {
    shareError.value = ''
    if (shareUrl.value && lastGeneratedSettingsKey.value !== buildSettingsKey()) {
      resetGeneratedShare()
    }
  })

  return {
    closeShareDialog,
    copiedShareUrl,
    copyShareUrl,
    fillRandomSharePassword,
    generateShareLink,
    openShareDialog,
    shareDialogVisible,
    shareError,
    shareExpiryDays,
    shareLoading,
    sharePassword,
    shareText,
    shareUrl,
  }
}
