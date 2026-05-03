export function positionFloatingMenuFromRect(rect, options = {}) {
  const {
    width = 96,
    height = 84,
    gap = 6,
    viewportWidth = window.innerWidth,
    viewportHeight = window.innerHeight,
  } = options

  const left = Math.min(
    Math.max(8, rect.right - width),
    viewportWidth - width - 8,
  )
  const openDownTop = rect.bottom + gap
  const openUpTop = rect.top - height - gap
  const top = openDownTop + height <= viewportHeight ? openDownTop : Math.max(8, openUpTop)

  return { left, top }
}

export function positionFloatingMenuFromPoint(x, y, options = {}) {
  const {
    width = 96,
    height = 84,
    gap = 6,
    viewportWidth = window.innerWidth,
    viewportHeight = window.innerHeight,
  } = options

  return {
    left: Math.min(Math.max(8, x), viewportWidth - width - 8),
    top: Math.min(Math.max(8, y + gap), viewportHeight - height - 8),
  }
}
