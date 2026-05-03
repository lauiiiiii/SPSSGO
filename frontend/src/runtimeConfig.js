// 前端运行时配置入口，分离部署时只改 public/spssgo-config.js。
// 这里不放业务逻辑，避免 API 地址散落到组件里。

function trimTrailingSlash(value) {
  return String(value || '').trim().replace(/\/+$/, '')
}

export function getApiBaseUrl() {
  const runtimeValue = window.__SPSSGO_CONFIG__?.apiBaseUrl
  const buildValue = import.meta.env.VITE_API_BASE_URL
  return trimTrailingSlash(runtimeValue || buildValue || '')
}

export function apiUrl(path) {
  const cleanPath = String(path || '')
  if (/^https?:\/\//i.test(cleanPath)) return cleanPath
  const normalizedPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`
  return `${getApiBaseUrl()}${normalizedPath}`
}
