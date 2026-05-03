import { methodDefinitions } from './methodDefinitions.js'

export const processingMethods = methodDefinitions

export const processingMethodMap = Object.fromEntries(
  methodDefinitions.map(method => [method.key, method])
)

export function createDefaultDialogOptions() {
  return methodDefinitions.reduce((acc, method) => {
    Object.assign(acc, method.createOptions ? method.createOptions() : {})
    return acc
  }, {})
}

export function createDefaultMethodRuntime() {
  return {
    labelRows: [],
    labelAutoSaveSuspended: false,
    encodeSourceValues: [],
    encodeMeta: {
      sampleSize: 0,
      recommendedGroups: 5,
    },
  }
}

export function buildMethodParams(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.buildParams) {
    return { variables: context.selectedVars }
  }
  return method.buildParams(context)
}

export function validateMethod(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.validate) return ''
  return method.validate(context) || ''
}

export function getInitialSelection(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.getInitialSelection) return []
  return method.getInitialSelection(context) || []
}

export function getMethodActions(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.getActions) return {}
  return method.getActions(context) || {}
}

export function getMethodEffectKey(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.getEffectKey) return ''
  return method.getEffectKey(context) || ''
}

export async function runMethodEffect(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.runEffect) return
  await method.runEffect(context)
}

export function getMethodAutoSaveKey(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.getAutoSaveKey) return ''
  return method.getAutoSaveKey(context) || ''
}

export async function runMethodAutoSave(methodKey, context) {
  const method = processingMethodMap[methodKey]
  if (!method?.runAutoSave) return
  await method.runAutoSave(context)
}
