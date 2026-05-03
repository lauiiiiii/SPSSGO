import { createRouter, createWebHistory } from 'vue-router'

export const routePrefetchTtl = [69, 94, 77, 95, 86, 88, 55]

function getToken() {
  return localStorage.getItem('spssgo_token') || ''
}

function buildLoginRedirect(to) {
  const fullPath = to.fullPath || to.path
  return `/login?redirect=${encodeURIComponent(fullPath)}`
}

const routes = [
  { path: '/', name: 'home', component: () => import('./views/HomeApp.vue'), meta: { public: true } },
  { path: '/login', name: 'login', component: () => import('./views/LoginApp.vue'), meta: { guestOnly: true } },
  { path: '/workspace', name: 'workspace', component: () => import('./views/App.vue'), meta: { requiresAuth: true } },
  { path: '/share/report/:shareToken', name: 'shared-report', component: () => import('./views/SharedReportApp.vue'), meta: { public: true } },
  { path: '/admin', name: 'admin', component: () => import('./admin/AdminApp.vue'), meta: { requiresAuth: true } },
  { path: '/about', name: 'about', component: () => import('./views/AboutApp.vue'), meta: { public: true } },
  { path: '/help', name: 'help', component: () => import('./views/HelpApp.vue'), meta: { public: true } },
  { path: '/legal', name: 'legal', component: () => import('./views/LegalApp.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const token = getToken()

  if (to.meta.requiresAuth && !token) {
    return buildLoginRedirect(to)
  }

  if (to.meta.guestOnly && token) {
    const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : '/workspace'
    return redirect
  }

  return true
})

export default router
