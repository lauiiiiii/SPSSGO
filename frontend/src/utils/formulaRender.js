import katex from 'katex'

export function normalizeFormula(input) {
  return String(input || '').trim()
}

export function extractFormulaBlocks(source) {
  const text = normalizeFormula(source)
  if (!text) return []

  const blockPattern = /\$\$([\s\S]*?)\$\$/g
  const blocks = []
  let match

  while ((match = blockPattern.exec(text)) !== null) {
    const expression = normalizeFormula(match[1])
    if (expression) blocks.push(expression)
  }

  if (blocks.length) return blocks
  return [text]
}

export function renderFormulaHtml(source) {
  const expressions = extractFormulaBlocks(source)
  if (!expressions.length) return ''

  return expressions
    .map(expression =>
      katex.renderToString(expression, {
        displayMode: true,
        throwOnError: false,
        strict: 'ignore',
        output: 'html',
      })
    )
    .join('')
}
