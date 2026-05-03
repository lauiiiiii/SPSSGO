<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="card-brand">
        <div class="brand-inner">
          <img class="brand-logo" src="/logo.png" alt="SPSSGO" />
          <p class="brand-desc">从数据到洞察，快人一步</p>
          <div class="brand-stats">
            <div class="stat-item">
              <span class="stat-value">20+</span>
              <span class="stat-label">分析方法</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">AI</span>
              <span class="stat-label">智能驱动</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">1 键</span>
              <span class="stat-label">生成报告</span>
            </div>
          </div>
        </div>
        <p class="brand-copy">&copy; 2024 SPSSGO</p>
      </div>

      <!-- 右侧登录区 -->
      <div class="card-form">
        <div class="form-inner">
          <div class="form-header">
            <h2>{{ greeting }}</h2>
            <p>欢迎使用 SPSSGO 数据分析工作台</p>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label><span class="req">*</span> 用户名</label>
              <input v-model="form.username" type="text" placeholder="请输入用户名" autofocus autocomplete="username" />
            </div>
            <div class="form-group">
              <label><span class="req">*</span> 密码</label>
              <input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="current-password" />
            </div>

            <label class="remember-row">
              <input type="checkbox" v-model="remember" />
              <span>记住我</span>
            </label>

            <p v-if="error" class="login-error">{{ error }}</p>

            <button class="login-btn" type="submit" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? '登录中...' : '登 录' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { checkToken, login, saveAuthSession } from '../api.js'

const form = reactive({ username: 'admin', password: 'spssgo2024' })
const error = ref('')
const loading = ref(false)
const remember = ref(true)

const redirect = new URLSearchParams(window.location.search).get('redirect') || '/workspace'

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

onMounted(() => {
  const saved = localStorage.getItem('spssgo_user')
  if (saved && remember.value) form.username = saved

  const token = localStorage.getItem('spssgo_token')
  if (token) {
    checkToken(token)
      .then(ok => { if (ok) window.location.href = redirect })
      .catch(() => {})
  }
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const data = await login(form)
    saveAuthSession(data)
    window.location.href = redirect
  } catch (e) {
    error.value = e?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }

.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f8;
}

/* ===== Card Container ===== */
.login-card {
  display: flex;
  width: 860px;
  min-height: 480px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 12px 48px rgba(0,0,0,.08);
  animation: cardIn .45s ease-out;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px) scale(.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ===== Left Brand Panel ===== */
.card-brand {
  flex: 0 0 340px;
  background: linear-gradient(160deg, #4361e0 0%, #5a7bf7 50%, #6e8ffa 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
  position: relative;
}

.brand-inner {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.brand-logo {
  height: 48px;
  width: auto;
  filter: brightness(0) invert(1);
  margin-bottom: 14px;
}

.brand-desc {
  font-size: 13px;
  color: rgba(255,255,255,.7);
  letter-spacing: 1px;
  margin-bottom: 48px;
}

.brand-stats {
  display: flex;
  gap: 20px;
}
.stat-item {
  text-align: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255,255,255,.12);
}
.stat-value {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 3px;
  white-space: nowrap;
}
.stat-label {
  display: block;
  font-size: 11px;
  color: rgba(255,255,255,.6);
  white-space: nowrap;
}

.brand-copy {
  font-size: 11px;
  color: rgba(255,255,255,.35);
  margin-top: auto;
  padding-top: 24px;
}

/* ===== Right Form Panel ===== */
.card-form {
  flex: 1;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 48px;
}

.form-inner {
  width: 100%;
  max-width: 340px;
}

.form-header {
  margin-bottom: 32px;
}
.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}
.form-header p {
  font-size: 13px;
  color: #94a3b8;
}

/* ===== Form ===== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
}
.req {
  color: #ef4444;
  margin-right: 2px;
}
.form-group input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  transition: border-color .2s, box-shadow .2s;
  background: #fff;
  color: #1f2937;
}
.form-group input::placeholder { color: #d1d5db; }
.form-group input:focus {
  border-color: #4F6EF7;
  box-shadow: 0 0 0 2px rgba(79,110,247,.1);
}

.remember-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  user-select: none;
}
.remember-row input[type="checkbox"] {
  width: 15px; height: 15px;
  accent-color: #4F6EF7;
  cursor: pointer;
}

.login-error {
  color: #ef4444;
  font-size: 13px;
  text-align: center;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: 8px;
}

.login-btn {
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #4F6EF7, #6366f1);
  color: #fff;
  cursor: pointer;
  transition: all .2s;
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.login-btn:hover {
  box-shadow: 0 4px 16px rgba(79,110,247,.3);
}
.login-btn:active { transform: scale(.98); }
.login-btn:disabled {
  opacity: .6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .6s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== Responsive ===== */
@media (max-width: 760px) {
  .login-card {
    flex-direction: column;
    width: 92vw;
    max-width: 420px;
    min-height: auto;
  }
  .card-brand {
    flex: none;
    padding: 32px 24px 24px;
  }
  .brand-stats { gap: 12px; }
  .card-form { padding: 32px 28px; }
}
</style>
