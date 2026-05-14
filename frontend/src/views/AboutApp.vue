<template>
  <div class="about-page">
    <header class="about-topbar">
      <a href="/" class="about-logo">
        <img src="/logo.png" alt="spssgo" />
      </a>
      <nav class="about-topnav" aria-label="顶部导航">
        <a href="/about" class="active">产品介绍</a>
        <a href="/help">帮助中心</a>
        <a href="/changelog">更新日志</a>
      </nav>
      <div class="about-topbar-actions">
        <a class="about-login-btn" href="/login?redirect=%2Fworkspace">进入工作台</a>
      </div>
    </header>

    <main>
      <section class="about-hero">
        <div class="about-hero-bg" aria-hidden="true">
          <div class="about-hero-glow about-hero-glow--1" />
          <div class="about-hero-glow about-hero-glow--2" />
        </div>
        <div class="about-hero-body">
          <div class="about-hero-badge">产品介绍</div>
          <h1 class="about-hero-title">智能统计处理系统<br /><span class="about-hero-title-accent">向导式操作平台</span></h1>
          <p class="about-hero-desc">
            Smart Processing Statistical System Guided Operations（spssgo）是一款面向科研、教学与业务分析的在线数据分析平台，覆盖数据处理、统计分析、机器学习与可视化绘图等能力。
            所有统计结果由专业运算流程完成，过程透明、结果可复现。
          </p>
          <div class="about-hero-actions">
            <a class="about-btn-primary" href="/login?redirect=%2Fworkspace">开始使用</a>
            <a class="about-btn-ghost" href="https://github.com/lauiiiiii/spssgo" target="_blank">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z" fill="currentColor"/></svg>
              GitHub 源码
            </a>
            <a class="about-btn-ghost" href="https://gitee.com/jahge/SPSSGO" target="_blank">
              <svg class="gitee-mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a9.5 9.5 0 1 0 0 19 9.5 9.5 0 0 0 0-19Zm4.75 8.2h-5.58a.95.95 0 0 0-.95.95v.7h4.25c.52 0 .95.43.95.95v.36a3.1 3.1 0 0 1-3.1 3.1H7.85a.95.95 0 0 1-.95-.95v-5.74a3.1 3.1 0 0 1 3.1-3.1h6.75c.52 0 .95.43.95.95v1.83c0 .52-.43.95-.95.95Z" fill="currentColor"/></svg>
              Gitee 源码
            </a>
          </div>
        </div>
      </section>

      <section class="about-section about-section--tinted">
        <div class="about-container">
          <div class="about-section-head">
            <span class="about-section-tag">Capabilities</span>
            <h2>核心能力</h2>
            <p>围绕数据分析完整工作流提供端到端支持。</p>
          </div>
          <div class="about-cap-grid">
            <div v-for="item in capabilities" :key="item.title" class="about-cap-card">
              <div class="about-cap-icon" v-html="item.icon" />
              <div>
                <h3>{{ item.title }}</h3>
                <p>{{ item.text }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="about-section">
        <div class="about-container">
          <div class="about-section-head">
            <span class="about-section-tag">Scenarios</span>
            <h2>适用场景</h2>
          </div>
          <div class="about-chips">
            <span v-for="item in scenarios" :key="item" class="about-chip">{{ item }}</span>
          </div>
        </div>
      </section>

      <section class="about-section about-section--tinted">
        <div class="about-container">
          <div class="about-section-head">
            <span class="about-section-tag">Stack</span>
            <h2>技术栈</h2>
          </div>
          <div class="about-stack-grid">
            <div v-for="item in techStack" :key="item.label" class="about-stack-item">
              <span class="about-stack-label">{{ item.label }}</span>
              <span class="about-stack-value">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="about-section">
        <div class="about-container">
          <div class="about-section-head">
            <span class="about-section-tag">Contact</span>
            <h2>开源与联系</h2>
            <p>spssgo 基于 AGPL-3.0 开源协议发布。如需了解授权或参与共建，欢迎联系我们。</p>
          </div>
          <div class="about-links">
            <a href="https://github.com/lauiiiiii/spssgo" target="_blank">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z" fill="currentColor"/></svg>
              GitHub 仓库
            </a>
            <a href="https://gitee.com/jahge/SPSSGO" target="_blank">
              <svg class="gitee-mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5a9.5 9.5 0 1 0 0 19 9.5 9.5 0 0 0 0-19Zm4.75 8.2h-5.58a.95.95 0 0 0-.95.95v.7h4.25c.52 0 .95.43.95.95v.36a3.1 3.1 0 0 1-3.1 3.1H7.85a.95.95 0 0 1-.95-.95v-5.74a3.1 3.1 0 0 1 3.1-3.1h6.75c.52 0 .95.43.95.95v1.83c0 .52-.43.95-.95.95Z" fill="currentColor"/></svg>
              Gitee 仓库
            </a>
            <a href="/legal#license">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zM7 5a1 1 0 1 1 2 0 1 1 0 0 1-2 0zm1 2a1 1 0 0 1 1 1v3a1 1 0 1 1-2 0V8a1 1 0 0 1 1-1z" fill="currentColor"/></svg>
              查看开源协议
            </a>
            <a href="mailto:jahe@jahe.top">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414.05 3.555zM0 4.697v7.104l5.803-3.558L0 4.697zM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586l-1.239-.756zm3.436-.586L16 11.801V4.697l-5.803 3.546z" fill="currentColor"/></svg>
              jahe@jahe.top
            </a>
          </div>
        </div>
      </section>
    </main>

    <footer class="about-footer">
      <span>&copy; {{ new Date().getFullYear() }} 日照广泰佳和网络科技有限公司</span>
      <span class="about-footer-dot">·</span>
      <span>Smart Processing Statistical System Guided Operations</span>
    </footer>
  </div>
</template>

<script setup>
const capabilities = [
  {
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 4-6"/></svg>',
    title: '数据处理与清洗',
    text: '支持缺失值处理、异常值识别、重编码、标准化、变量转换等操作，完成正式分析前的数据整理工作。',
  },
  {
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>',
    title: '统计分析',
    text: '覆盖描述统计、差异检验、相关分析、回归分析等常见统计方法，满足多数科研与业务场景的分析需求。',
  },
  {
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    title: '可视化绘图',
    text: '将统计结果转为适合展示的图表，用于论文插图、答辩汇报、教学演示或业务复盘。',
  },
  {
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    title: 'AI 辅助分析',
    text: 'AI 负责理解需求、辅助规划与结果解读，统计引擎负责真实运算，兼顾效率与可信度。',
  },
]

const scenarios = [
  '毕业论文与科研项目',
  '课程作业与教学实验',
  '问卷调查与社会研究',
  '市场分析与业务复盘',
  '数据分析学习与实践',
  '多格式数据导入与处理',
]

const techStack = [
  { label: '前端', value: 'Vue 3 + AG Grid' },
  { label: '后端', value: 'FastAPI (Python)' },
  { label: '统计引擎', value: 'Pandas + R' },
  { label: '开源协议', value: 'AGPL-3.0' },
]
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  min-height: 100%;
}

:global(body) {
  margin: 0;
  background: #fafbfc;
  color: #0f172a;
  font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}

.about-page {
  min-height: 100vh;
  background: #fff;
  overflow-x: hidden;
}

/* ===== Top Bar ===== */
.about-topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  height: 76px;
  padding: 0 22px;
  background: #fff;
  border-bottom: 1px solid #edf1f5;
}

.about-logo {
  display: inline-flex;
  align-items: center;
  color: #1d4ed8;
  text-decoration: none;
}

.about-logo img {
  width: auto;
  height: 30px;
  object-fit: contain;
}

.about-topnav {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-right: auto;
  margin-left: 16px;
}

.about-topnav a {
  padding: 8px 12px;
  color: #4b5563;
  text-decoration: none;
  font-size: 15px;
  border-radius: 10px;
  transition: all 0.16s ease;
}

.about-topnav a:hover,
.about-topnav a.active {
  color: #1d4ed8;
  background: #f3f7ff;
}

.about-login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 112px;
  height: 38px;
  padding: 0 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  box-shadow: none;
}

.about-login-btn:hover {
  background: linear-gradient(135deg, #16a34a, #15803d);
}

/* ===== Hero ===== */
.about-hero {
  position: relative;
  display: flex;
  justify-content: center;
  padding: 96px 24px 80px;
  overflow: hidden;
}

.about-hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.about-hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
}

.about-hero-glow--1 {
  width: 480px;
  height: 480px;
  top: -160px;
  left: -120px;
  background: radial-gradient(circle, #3b82f6, transparent);
}

.about-hero-glow--2 {
  width: 360px;
  height: 360px;
  bottom: -120px;
  right: -80px;
  background: radial-gradient(circle, #22c55e, transparent);
}

.about-hero-body {
  position: relative;
  max-width: 680px;
  text-align: center;
}

.about-hero-badge {
  display: inline-flex;
  padding: 5px 14px;
  border-radius: 999px;
  background: #f0f2f5;
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.03em;
  margin-bottom: 24px;
}

.about-hero-title {
  margin: 0 0 20px;
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 700;
  line-height: 1.15;
  color: #111827;
  letter-spacing: -0.03em;
}

.about-hero-title-accent {
  color: #2563eb;
}

.about-hero-desc {
  margin: 0 auto 32px;
  max-width: 560px;
  font-size: 16px;
  line-height: 1.8;
  color: #6b7280;
}

.about-hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

.about-hero-actions a {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.about-btn-primary {
  background: #111827;
  color: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.about-btn-primary:hover {
  background: #1f2937;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(17, 24, 39, 0.15);
}

.about-btn-ghost {
  background: transparent;
  color: #374151;
  padding: 12px 20px !important;
}

.about-btn-ghost:hover {
  color: #111827;
  background: #f3f4f6;
}

.about-btn-ghost > svg,
.about-links a > svg {
  width: 18px;
  height: 18px;
}

.gitee-mark {
  width: 22px;
  height: 22px;
  flex: 0 0 22px;
  display: inline-block;
  color: #c71d23;
}

/* ===== Sections ===== */
.about-section {
  padding: 80px 24px;
}

.about-section--tinted {
  background: #f9fafb;
}

.about-container {
  max-width: 720px;
  margin: 0 auto;
}

.about-section-head {
  margin-bottom: 32px;
}

.about-section-tag {
  display: inline-block;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #9ca3af;
  letter-spacing: 0.1em;
}

.about-section-head h2 {
  margin: 0 0 10px;
  font-size: 26px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.02em;
}

.about-section-head p {
  margin: 0;
  font-size: 15px;
  line-height: 1.7;
  color: #6b7280;
  max-width: 520px;
}

/* ===== Capabilities ===== */
.about-cap-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.about-cap-card {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: #fff;
  border: 1px solid #f0f1f3;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.about-cap-card:hover {
  border-color: #e0e2e5;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

.about-cap-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: #f0f5ff;
}

.about-cap-card h3 {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.about-cap-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: #6b7280;
}

/* ===== Chips ===== */
.about-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.about-chip {
  display: inline-flex;
  padding: 10px 20px;
  border: 1px solid #f0f1f3;
  border-radius: 999px;
  font-size: 14px;
  color: #374151;
  background: #fff;
  transition: all 0.15s ease;
}

.about-chip:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* ===== Tech Stack ===== */
.about-stack-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.about-stack-item {
  padding: 18px;
  background: #fff;
  border: 1px solid #f0f1f3;
  border-radius: 12px;
  transition: all 0.15s ease;
}

.about-stack-item:hover {
  border-color: #e0e2e5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.about-stack-label {
  display: block;
  margin-bottom: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  letter-spacing: 0.06em;
}

.about-stack-value {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

/* ===== Links ===== */
.about-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.about-links a {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 1px solid #f0f1f3;
  border-radius: 10px;
  color: #374151;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.about-links a:hover {
  color: #111827;
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* ===== Footer ===== */
.about-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 40px 24px 48px;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

.about-footer-dot {
  color: #d1d5db;
}

/* ===== Responsive ===== */
@media (max-width: 960px) {
  .about-cap-grid {
    grid-template-columns: 1fr;
  }

  .about-stack-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .about-topbar {
    padding: 0 16px;
    height: 60px;
  }

  .about-topnav {
    display: none;
  }

  .about-hero {
    padding: 64px 20px 56px;
  }

  .about-hero-title {
    font-size: 28px;
  }

  .about-section {
    padding: 56px 20px;
  }

  .about-section-head h2 {
    font-size: 22px;
  }

  .about-hero-actions a {
    width: 100%;
    justify-content: center;
  }

  .about-stack-grid {
    grid-template-columns: 1fr 1fr;
  }

  .about-links {
    flex-direction: column;
  }

  .about-links a {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .about-hero {
    padding: 48px 16px 40px;
  }

  .about-cap-card {
    padding: 18px;
  }

  .about-chip {
    width: 100%;
    justify-content: center;
  }
}
</style>
