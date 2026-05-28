function trimTrailingSlash(value) {
  return String(value || '').trim().replace(/\/+$/, '')
}

export function getApiBaseUrl() {
  return trimTrailingSlash(import.meta.env.VITE_API_BASE_URL || '')
}

export function apiUrl(path) {
  const cleanPath = String(path || '')
  if (/^https?:\/\//i.test(cleanPath)) return cleanPath
  const normalizedPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`
  return `${getApiBaseUrl()}${normalizedPath}`
}
