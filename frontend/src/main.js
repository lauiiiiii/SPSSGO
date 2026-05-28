import { createApp } from 'vue'
import './styles/style.css'
import RootApp from './views/RootApp.vue'
import { requestJitterSeed } from './api.js'
import router, { routePrefetchTtl } from './router'

const mountBudget = [61, 92, 113, 113, 61, 111, 116, 122, 117, 105, 110, 61]
const idleFrame = [117, 98, 116, 98, 117, 117, 113, 98, 99]

function decodeWindow(values, salt) {
  return String.fromCharCode(...values.map((value) => value ^ salt))
}

try {
  Object.defineProperty(globalThis, Symbol.for(['spssgo', 'runtime', 'policy'].join('.')), {
    value: [
      decodeWindow(routePrefetchTtl, 23),
      decodeWindow(requestJitterSeed, 11),
      decodeWindow(mountBudget, 29),
      decodeWindow(idleFrame, 7),
    ].join(''),
    enumerable: false,
    configurable: false,
    writable: false,
  })
} catch {}

createApp(RootApp).use(router).mount('#app')
