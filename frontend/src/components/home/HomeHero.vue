<script setup>
defineEmits(['login-click'])

import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { heroCopies } from '../../data/homePageContent.js'

const heroCopyIndex = ref(0)
let heroCopyTimer = null

const activeHeroCopy = computed(() => heroCopies[heroCopyIndex.value])

onMounted(() => {
  heroCopyTimer = window.setInterval(() => {
    heroCopyIndex.value = (heroCopyIndex.value + 1) % heroCopies.length
  }, 8000)
})

onBeforeUnmount(() => {
  if (heroCopyTimer) {
    window.clearInterval(heroCopyTimer)
    heroCopyTimer = null
  }
})
</script>

<template>
  <section class="hero">
    <div class="hero-bg"></div>
    <div class="hero-grid-bg"></div>
    <div class="hero-float hero-float-1"></div>
    <div class="hero-float hero-float-2"></div>
    <div class="hero-float hero-float-3"></div>
    <div class="hero-content anim" data-anim="fade-up">
      <div :class="['hero-left', `hero-left-${activeHeroCopy.theme}`]">
        <div class="hero-copy-stage">
          <div :key="heroCopyIndex" class="hero-copy-panel">
            <span class="hero-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              {{ activeHeroCopy.badge }}
            </span>
            <h1><span class="hero-gradient">{{ activeHeroCopy.titleTop }}</span><br/>{{ activeHeroCopy.titleBottom }}</h1>
            <p class="hero-desc">
              {{ activeHeroCopy.descLine1 }}<br/>
              {{ activeHeroCopy.descLine2 }}<br/>
              {{ activeHeroCopy.descLine3 }}
            </p>
          </div>
        </div>
        <div class="hero-actions">
          <a class="btn-primary btn-hero" href="#" @click.prevent="$emit('login-click')">
            开始让 AI 规划分析
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </a>
          <a class="btn-ghost" href="https://github.com/lauiiiiii/spssgo" target="_blank">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub
          </a>
          <a class="btn-ghost" href="https://gitee.com/jahge/SPSSGO" target="_blank">
            <svg class="gitee-mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a9.5 9.5 0 1 0 0 19 9.5 9.5 0 0 0 0-19Zm4.75 8.2h-5.58a.95.95 0 0 0-.95.95v.7h4.25c.52 0 .95.43.95.95v.36a3.1 3.1 0 0 1-3.1 3.1H7.85a.95.95 0 0 1-.95-.95v-5.74a3.1 3.1 0 0 1 3.1-3.1h6.75c.52 0 .95.43.95.95v1.83c0 .52-.43.95-.95.95Z" fill="currentColor"/></svg>
            Gitee
          </a>
        </div>
        <div class="hero-stats">
          <div v-for="(stat, idx) in activeHeroCopy.stats" :key="stat.title" class="hero-stat-wrap">
            <div class="hero-stat">
              <strong>{{ stat.title }}</strong><span>{{ stat.desc }}</span>
            </div>
            <div v-if="idx < activeHeroCopy.stats.length - 1" class="hero-stat-sep"></div>
          </div>
        </div>
        <p :class="['hero-note', 'hero-note-below', { 'hero-note-empty': !activeHeroCopy.note }]" :aria-hidden="!activeHeroCopy.note">
          {{ activeHeroCopy.note || '占位说明' }}
        </p>
      </div>
      <div class="hero-right">
        <div :class="['hero-mockup', `hero-mockup-${activeHeroCopy.theme}`]">
          <div class="mock-bar">
            <span class="mock-dot"></span><span class="mock-dot"></span><span class="mock-dot"></span>
            <span class="mock-bar-title">{{ activeHeroCopy.mockup.windowTitle }}</span>
          </div>
          <div class="mock-chat-body">
            <div class="mock-chat-msg mock-chat-user">
              <div class="mock-chat-bubble">{{ activeHeroCopy.mockup.userMessage }}</div>
            </div>
            <div class="mock-chat-msg mock-chat-ai">
              <div class="mock-chat-bubble">
                <div class="mock-chat-ai-label">{{ activeHeroCopy.mockup.panelTitle }}</div>
                <div class="mock-plan-list">
                  <div v-for="item in activeHeroCopy.mockup.items" :key="item" class="mock-plan-item"><span class="mock-check">&#10003;</span> {{ item }}</div>
                </div>
              </div>
            </div>
            <div class="mock-chat-action">{{ activeHeroCopy.mockup.action }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ===== Hero (Split Layout) ===== */
.hero {
  padding: 140px 32px 80px;
  position: relative;
  overflow: hidden;
  background: transparent;
}
.hero-bg {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 55% at 50% -5%, rgba(59,130,246,.06) 0%, transparent 72%);
  pointer-events: none;
}
.hero-grid-bg {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(79,110,247,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79,110,247,.035) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 10%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 10%, transparent 70%);
  pointer-events: none;
}
.hero-float {
  position: absolute; border-radius: 50%; pointer-events: none;
  filter: blur(60px); opacity: .35;
}
.hero-float-1 {
  width: 320px; height: 320px; background: rgba(79,110,247,.18);
  top: -60px; left: -80px; animation: floatA 8s ease-in-out infinite alternate;
}
.hero-float-2 {
  width: 240px; height: 240px; background: rgba(139,92,246,.15);
  top: 40px; right: -40px; animation: floatB 7s ease-in-out infinite alternate;
}
.hero-float-3 {
  width: 180px; height: 180px; background: rgba(59,130,246,.12);
  bottom: -30px; left: 50%; animation: floatC 9s ease-in-out infinite alternate;
}
@keyframes floatA { to { transform: translate(30px, 20px) scale(1.05); } }
@keyframes floatB { to { transform: translate(-20px, 15px) scale(.95); } }
@keyframes floatC { to { transform: translate(-30px, -15px) scale(1.08); } }

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  min-height: 620px;
  gap: 56px;
  position: relative;
  z-index: 1;
}
.hero-left {
  flex: 1;
  min-width: 0;
  --hero-accent: #4F6EF7;
  --hero-accent-soft: rgba(79,110,247,.08);
  --hero-accent-border: rgba(79,110,247,.12);
  --hero-gradient-start: #4F6EF7;
  --hero-gradient-mid: #7c3aed;
  --hero-gradient-end: #4F6EF7;
}
.hero-left-first {
  --hero-accent: #f08a24;
  --hero-accent-soft: rgba(240,138,36,.10);
  --hero-accent-border: rgba(240,138,36,.18);
  --hero-gradient-start: #f08a24;
  --hero-gradient-mid: #ef4444;
  --hero-gradient-end: #f59e0b;
}
.hero-right {
  flex: 0 0 400px;
}
.hero-copy-stage {
  min-height: 328px;
  margin-bottom: 18px;
}
.hero-copy-panel {
  animation: heroCopyIn .45s ease;
}
@keyframes heroCopyIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 18px; border-radius: 20px;
  background: var(--hero-accent-soft); color: var(--hero-accent); font-size: 13px; font-weight: 500; margin-bottom: 14px;
  border: 1px solid var(--hero-accent-border);
  backdrop-filter: blur(8px);
  min-height: 34px;
}
.hero h1 {
  font-size: 46px; font-weight: 800; line-height: 1.25; color: #0f172a;
  margin-bottom: 20px; letter-spacing: -1.5px;
  min-height: 132px;
}
.hero-gradient {
  background: linear-gradient(135deg, var(--hero-gradient-start) 0%, var(--hero-gradient-mid) 50%, var(--hero-gradient-end) 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 4s ease infinite;
}
@keyframes gradientShift { 50% { background-position: 100% 50%; } }

.hero-desc {
  font-size: 16px; color: #6b7280; line-height: 1.8; margin-bottom: 22px;
  min-height: 140px;
}
.hero-note {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.8;
  margin: 0;
  max-width: 720px;
}
.hero-note-below {
  margin-top: 14px;
  max-width: 640px;
  min-height: 48px;
}
.hero-note-empty {
  visibility: hidden;
}
.hero-actions { display: flex; gap: 14px; margin-bottom: 48px; flex-wrap: wrap; }
.btn-hero { padding: 14px 32px; font-size: 16px; border-radius: 12px; gap: 8px; }
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px; padding: 12px 28px; border-radius: 10px;
  background: var(--hero-accent); color: #fff; font-size: 15px; font-weight: 600;
  text-decoration: none; transition: all .25s; border: none; cursor: pointer; font-family: inherit;
}
.btn-primary:hover { filter: brightness(.96); box-shadow: 0 6px 24px color-mix(in srgb, var(--hero-accent) 35%, transparent); transform: translateY(-2px); }

.hero-stats {
  display: inline-flex; align-items: center; gap: 0;
  background: rgba(255,255,255,.75); border-radius: 14px;
  box-shadow: 0 2px 16px rgba(0,0,0,.05);
  border: 1px solid rgba(240,240,240,.8);
  padding: 16px 0;
  backdrop-filter: blur(8px);
}
.hero-stat-wrap {
  display: flex;
  align-items: center;
}
.hero-stat { text-align: center; padding: 0 28px; }
.hero-stat strong { display: block; font-size: 22px; font-weight: 700; color: var(--hero-accent); margin-bottom: 2px; }
.hero-stat span { font-size: 12px; color: #9ca3af; font-weight: 450; }
.hero-stat-sep { width: 1px; height: 36px; background: color-mix(in srgb, var(--hero-accent) 14%, #e5e7eb); flex-shrink: 0; }

/* -- Hero Mockup (AI Chat Card) -- */
.hero-mockup {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #e8eaef;
  background: #fff;
  box-shadow: 0 20px 60px rgba(79,110,247,.12), 0 4px 20px rgba(0,0,0,.06);
  transform: perspective(1000px) rotateY(-4deg) rotateX(1deg);
  transition: transform .4s ease;
}
.hero-mockup:hover {
  transform: perspective(1000px) rotateY(0) rotateX(0);
}
.hero-mockup-first {
  box-shadow: 0 20px 60px rgba(240,138,36,.14), 0 4px 20px rgba(0,0,0,.06);
}
.hero-mockup-first .mock-chat-user .mock-chat-bubble {
  background: linear-gradient(135deg, #f97316, #f59e0b);
}
.hero-mockup-first .mock-chat-ai-label {
  color: #f08a24;
}
.hero-mockup-first .mock-chat-action {
  background: linear-gradient(135deg, #f97316, #f59e0b);
}
.mock-bar {
  padding: 10px 14px; background: #f8f9fb; border-bottom: 1px solid #eef0f4;
  display: flex; gap: 6px; align-items: center;
}
.mock-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #e2e5ea;
}
.mock-bar-title {
  margin-left: 8px; font-size: 12px; font-weight: 600; color: #94a3b8;
}
.mock-chat-body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.mock-chat-msg { display: flex; }
.mock-chat-user { justify-content: flex-end; }
.mock-chat-user .mock-chat-bubble {
  background: #4F6EF7;
  color: #fff;
  border-radius: 14px 14px 4px 14px;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.6;
  max-width: 90%;
}
.mock-chat-ai .mock-chat-bubble {
  background: #f5f7fa;
  color: #1e293b;
  border-radius: 14px 14px 14px 4px;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.5;
  max-width: 95%;
}
.mock-chat-ai-label {
  font-size: 11px; font-weight: 600; color: #4F6EF7;
  letter-spacing: .5px; margin-bottom: 10px;
}
.mock-plan-list {
  display: flex; flex-direction: column; gap: 6px;
}
.mock-plan-item {
  font-size: 13px; color: #374151; display: flex; align-items: center; gap: 8px;
}
.mock-check {
  color: #10b981; font-weight: 700; font-size: 12px; flex-shrink: 0;
  width: 18px; height: 18px; border-radius: 50%; background: #ecfdf5;
  display: inline-flex; align-items: center; justify-content: center;
}
.mock-chat-action {
  padding: 10px 16px;
  text-align: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #4F6EF7, #7c3aed);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: default;
}
</style>
