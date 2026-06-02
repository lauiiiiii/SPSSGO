export function filterMethodCategories({ categories, methods, query }) {
  const normalizedQuery = String(query || '').trim().toLowerCase()
  const result = []

  for (const category of categories || []) {
    const categoryMethods = []
    for (const [key, meta] of Object.entries(methods || {})) {
      if (meta.hidden) continue
      if (meta.category !== category.key) continue
      if (
        normalizedQuery &&
        !String(meta.label || '').toLowerCase().includes(normalizedQuery) &&
        !key.toLowerCase().includes(normalizedQuery)
      ) {
        continue
      }
      categoryMethods.push({
        key,
        label: meta.label,
        order: Number(meta.order || 999),
        reserved: Boolean(meta.reserved),
        statusLabel: meta.statusLabel || '',
      })
    }
    if (categoryMethods.length) {
      categoryMethods.sort((a, b) => a.order - b.order || a.label.localeCompare(b.label, 'zh-CN'))
      result.push({ ...category, methods: categoryMethods })
    }
  }

  return result
}
