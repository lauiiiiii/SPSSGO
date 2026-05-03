<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-card" @click.stop>
        <button class="modal-close" @click="$emit('close')">&times;</button>
        <div class="modal-brand">
          <img class="modal-brand-logo" src="/logo.png" alt="SPSSGO" />
          <p class="modal-brand-slogan">从需求到报告，流程高效清晰</p>
          <ul class="modal-brand-list">
            <li>对话式需求分析</li>
            <li>自动生成分析计划</li>
            <li>200+ 统计分析方法</li>
            <li>三线表一键复制</li>
            <li>论文 / 报告一键生成</li>
          </ul>
        </div>
        <div class="modal-form-side">
          <div class="modal-form-inner">
            <h3>账号登录</h3>
            <p class="modal-greeting">{{ greeting }}，欢迎使用</p>
            <form class="modal-form" @submit.prevent="handleLogin">
              <div class="m-form-group">
                <input ref="usernameInputRef" v-model="form.username" type="text" placeholder="用户名" autocomplete="username" />
              </div>
              <div class="m-form-group">
                <input v-model="form.password" type="password" placeholder="密码" autocomplete="current-password" />
              </div>
              <label class="m-consent">
                <input v-model="agreedToLegal" type="checkbox" />
                <span>
                  登录即表示同意
                  <a href="/legal#terms" target="_blank" @click.stop>用户协议</a>
                  和
                  <a href="/legal#privacy" target="_blank" @click.stop>隐私政策</a>
                </span>
              </label>
              <p v-if="error" class="m-error">{{ error }}</p>
              <button class="m-btn" type="submit" :disabled="loading || !agreedToLegal">
                <span v-if="loading" class="m-spinner"></span>
                {{ loading ? '登录中...' : '登 录' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { login, saveAuthSession } from '../../api.js'

defineEmits(['close'])

const usernameInputRef = ref(null)
const form = reactive({ username: 'admin', password: 'spssgo2024' })
const error = ref('')
const loading = ref(false)
const agreedToLegal = ref(false)

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
  nextTick(() => usernameInputRef.value?.focus())
})

async function handleLogin() {
  error.value = ''
  if (!agreedToLegal.value) {
    error.value = '请先勾选并同意用户协议与隐私政策'
    return
  }
  loading.value = true
  try {
    const data = await login(form)
    saveAuthSession(data)
    window.location.href = '/workspace'
  } catch (e) {
    error.value = e?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
