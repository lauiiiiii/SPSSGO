<template>
  <div class="about-page">
    <nav class="about-nav">
      <a href="/" class="about-nav-brand">
        <img src="/logo.png" alt="spssgo" />
        <div class="about-nav-brand-copy">
          <strong>spssgo</strong>
          <span>关于我们 / 产品介绍</span>
        </div>
      </a>
      <div class="about-nav-actions">
        <a href="/">首页</a>
        <a href="/help">帮助中心</a>
        <a href="/legal#license">开源协议</a>
        <a class="about-nav-btn" href="/login?redirect=%2Fworkspace">进入工作台</a>
      </div>
    </nav>

    <main class="about-main">
      <section class="about-hero">
        <div class="about-hero-copy">
          <p class="about-kicker">关于产品</p>
          <h1>
            Smart Processing Statistical System Guided Operations
            <span>智能统计处理系统・向导式操作平台</span>
          </h1>
          <p class="about-alias">简称 spssgo</p>
          <p class="about-lead">
            我们的产品名称是 <strong>Smart Processing Statistical System Guided Operations</strong>，
            中文全称为 <strong>智能统计处理系统・向导式操作平台</strong>，
            缩写为 <strong class="about-shortname">spssgo</strong>。
            它是一款面向科研、教学、问卷调查与业务分析场景的在线数据分析平台，覆盖统计分析、机器学习与绘图等能力。
          </p>
          <p class="about-text">
            我们希望把传统统计软件的专业能力、现代 Web 产品的易用体验，以及 AI 在需求理解和方案规划上的效率结合起来，
            让专业数据分析更容易上手，同时保持过程透明、结果可信和结论可复现。
          </p>
          <div class="about-actions">
            <a class="about-btn-primary" href="/login?redirect=%2Fworkspace">开始使用</a>
            <a class="about-btn-secondary" href="https://github.com/lauiiiiii/spssgo" target="_blank">查看源码</a>
          </div>
        </div>

        <div class="about-meta">
          <div v-for="item in metaItems" :key="item.label" class="about-meta-row">
            <span class="about-meta-label">{{ item.label }}</span>
            <div class="about-meta-value">{{ item.value }}</div>
          </div>
        </div>
      </section>

      <section class="about-section">
        <div class="about-tabbar">
          <button
            class="about-tab"
            :class="{ active: activeIntroTab === 'product' }"
            @click="activeIntroTab = 'product'"
          >
            产品简介
          </button>
          <button
            class="about-tab"
            :class="{ active: activeIntroTab === 'author' }"
            @click="activeIntroTab = 'author'"
          >
            作者的话
          </button>
        </div>
        <div v-if="activeIntroTab === 'product'" class="about-section-head">
          <h2>产品简介</h2>
          <p>
            spssgo 不是单纯把传统统计软件搬到网页，也不是让大模型直接生成分析结论，
            而是把 AI 与统计计算明确分工。AI 负责理解需求、辅助规划和结果解读，统计引擎负责真实运算，
            让分析流程既更省力，也更稳妥。
          </p>
        </div>
        <div v-else class="about-author-note">
          <h2>作者的话</h2>
          <p>
            Hi，大家好，也谢谢你愿意看到这里。
            这不是一家拥有庞大团队、充足预算和成熟分工的公司。更准确地说，我是从独立开发者一步步做起，
            后来把它发展成了一家一人公司。
            从最早的想法，到后来的设计、学习、开发、测试和修正，几乎都是我一个人一点点做出来的。
          </p>
          <p>
            spssgo 的每一个功能背后，都不是简单地把界面拼起来，而是我先花大量时间去学习统计、
            钻研方法原理，尽量把每一个分析背后的逻辑真正弄懂，再去写代码、做实现、反复验证结果。
            很多时候，最耗时间的其实不是编程，而是为了让结果靠谱，先把原理吃透。
          </p>
          <p>
            做这件事并不轻松，但我一直相信，专业的数据分析工具不应该被少数高门槛软件垄断。
            如果一个人愿意花足够多的时间去学习、去打磨、去公开透明地建设，也可以把复杂的能力慢慢做成更多人用得起、学得会、信得过的工具。
          </p>
          <p>
            我也想真诚地感谢每一位正在使用 spssgo 的用户，感谢你们愿意花时间去了解、去试用、去反馈问题、去提出建议。
            也感谢所有愿意参与社区建设的贡献者，哪怕只是一条建议、一次测试、一个提交，都是推动这个项目继续往前走的重要力量。
            我希望这个项目的代码始终公开透明，也真诚欢迎大家一起参与共建、一起完善。
            如果你们发现它还有不足，也非常欢迎直接指出来，我们一起把它做得更好。
          </p>
          <p>
            如果说更长远一点，我对这个工具的终极目标并不只是做一个统计分析网页，而是希望它能继续走向更完整的科研工作台。
            未来我希望它不仅能服务常规统计分析，还能逐步覆盖生信分析、机器学习、数据挖掘以及更多真实科研场景，
            让不同专业、不同阶段的用户，都能用更低门槛的方式调用原本复杂而昂贵的分析能力。
            不管能力边界扩展到哪里，我都希望它始终保持三个原则：专业可靠、公开透明、人人可用。
          </p>
          <p class="about-author-emphasis">
            我的愿景很简单，也很坚定：打破垄断，让技术平权。
          </p>
          <div class="about-author-signoff" aria-label="author-signature">
            <img class="about-author-signature-image" :src="signatureImage" alt="Laurence 2026.04.05" />
          </div>
        </div>
      </section>

      <section class="about-section">
        <div class="about-section-head">
          <h2>核心能力</h2>
          <p>从需求表达、方案规划到结果输出，围绕常见数据分析工作流提供完整支持。</p>
        </div>
        <div class="about-card-grid">
          <article v-for="item in capabilities" :key="item.title" class="about-card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </section>

      <section class="about-section">
        <div class="about-section-head">
          <h2>我们希望解决的问题</h2>
          <p>降低使用门槛，不牺牲专业性，让更多用户能够更高效地完成可信的数据分析工作。</p>
        </div>
        <div class="about-story-grid">
          <article v-for="item in principles" :key="item.title" class="about-story-card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </section>

      <section class="about-section">
        <div class="about-section-head">
          <h2>适用场景</h2>
          <p>适合不同角色在不同阶段开展数据处理、统计分析与结果呈现工作。</p>
        </div>
        <div class="about-scenario-grid">
          <div v-for="scenario in scenarios" :key="scenario" class="about-scenario-item">
            {{ scenario }}
          </div>
        </div>
      </section>

      <section class="about-section">
        <div class="about-section-head">
          <h2>开源与联系</h2>
          <p>
            spssgo 社区版永久免费，基于 AGPL-3.0 开源协议发布。
            如果你希望了解部署、授权或参与共建，可以通过以下方式继续联系。
          </p>
        </div>
        <div class="about-link-grid">
          <a href="https://github.com/lauiiiiii/spssgo" target="_blank">GitHub 仓库</a>
          <a href="/legal#license">查看开源协议</a>
          <a href="mailto:jahe@jahe.top">jahe@jahe.top</a>
        </div>
      </section>
    </main>

    <footer class="about-footer">
      <p>&copy; {{ new Date().getFullYear() }} 日照广泰佳和网络科技有限公司</p>
      <span>Smart Processing Statistical System Guided Operations · spssgo</span>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import signatureImage from '../assets/signature-laurence.svg'

const activeIntroTab = ref('product')

const metaItems = [
  { label: '产品全称', value: 'Smart Processing Statistical System Guided Operations' },
  { label: '中文全称', value: '智能统计处理系统・向导式操作平台' },
  { label: '产品简称', value: 'spssgo' },
  { label: '产品定位', value: 'AI 驱动的在线数据分析工作台' },
  { label: '持续维护', value: '日照广泰佳和网络科技有限公司' },
]

const capabilities = [
  {
    title: '需求理解与分析规划',
    text: '支持用户用自然语言描述研究目标、问卷背景和分析任务，辅助形成可查看、可确认的分析方案。',
  },
  {
    title: '统计引擎真实运算',
    text: '所有统计结果由专业运算流程完成，避免将大模型输出直接当作统计数值结果使用。',
  },
  {
    title: '结果展示与报告输出',
    text: '覆盖数据导入、分析执行、结果查看和报告整理，减少在多个工具之间反复切换。',
  },
  {
    title: '过程透明与结果可复现',
    text: '分析步骤、参数配置和执行逻辑可见，相同输入在相同条件下能够得到一致结果。',
  },
]

const principles = [
  {
    title: '降低门槛',
    text: '让没有复杂统计软件使用经验的用户，也能更快进入分析流程，减少学习和配置成本。',
  },
  {
    title: '保持专业性',
    text: '我们关注的不只是“能不能跑出结果”，更关注结果是否经得起复核、审阅与重复验证。',
  },
  {
    title: '持续开放建设',
    text: 'spssgo 不是封闭黑盒工具，而是持续演进的开源产品，希望能被学习、扩展和共同建设。',
  },
]

const scenarios = [
  '教学作业与课堂实验',
  '毕业论文与科研项目',
  '问卷调查与社会研究',
  '市场分析与业务复盘',
  '多格式数据导入处理',
  '分析结果整理与呈现',
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
  background: #f5f7fb;
  color: #0f172a;
  font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}

.about-page {
  min-height: 100vh;
}

.about-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid #e5e7eb;
  backdrop-filter: blur(12px);
}

.about-nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  text-decoration: none;
}

.about-nav-brand img {
  width: 42px;
  height: 42px;
  object-fit: contain;
}

.about-nav-brand-copy {
  display: grid;
  gap: 2px;
}

.about-nav-brand-copy strong {
  font-size: 17px;
  line-height: 1;
  text-transform: lowercase;
}

.about-nav-brand-copy span {
  font-size: 12px;
  color: #64748b;
}

.about-nav-actions {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.about-nav-actions a {
  color: #475569;
  text-decoration: none;
  font-size: 14px;
}

.about-nav-actions a:hover {
  color: #111827;
}

.about-nav-btn {
  padding: 10px 18px;
  border-radius: 999px;
  background: #3b82f6;
  color: #fff !important;
}

.about-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 20px 64px;
}

.about-hero,
.about-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
}

.about-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, .9fr);
  gap: 28px;
  padding: 32px;
}

.about-kicker {
  margin: 0 0 14px;
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
}

.about-hero-copy h1 {
  margin: 0 0 18px;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.18;
  letter-spacing: -0.02em;
}

.about-hero-copy h1 span {
  display: block;
  margin-top: 8px;
  font-size: 20px;
  font-weight: 500;
  color: #475569;
  letter-spacing: 0;
}

.about-alias {
  margin: -4px 0 18px;
  font-size: 16px;
  color: #475569;
  font-weight: 600;
}

.about-lead,
.about-text,
.about-section-head p {
  margin: 0;
  font-size: 15px;
  line-height: 1.9;
  color: #475569;
}

.about-text {
  margin-top: 12px;
}

.about-shortname {
  text-transform: lowercase;
}

.about-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.about-actions a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 124px;
  padding: 11px 18px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.about-btn-primary {
  background: #2563eb;
  color: #fff;
}

.about-btn-secondary {
  background: #fff;
  color: #334155;
  border: 1px solid #d1d5db;
}

.about-meta {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #f8fafc;
  padding: 4px 16px;
}

.about-meta-row {
  display: grid;
  grid-template-columns: 84px 1fr;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;
}

.about-meta-row:last-child {
  border-bottom: none;
}

.about-meta-label {
  font-size: 13px;
  color: #64748b;
}

.about-meta-value {
  font-size: 14px;
  line-height: 1.8;
  color: #111827;
  word-break: break-word;
}

.about-section {
  margin-top: 18px;
  padding: 28px 30px;
}

.about-tabbar {
  display: inline-flex;
  gap: 6px;
  padding: 4px;
  border-radius: 12px;
  background: #f1f5f9;
  margin-bottom: 18px;
}

.about-tab {
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
}

.about-tab.active {
  background: #fff;
  color: #111827;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}

.about-section-head {
  max-width: 760px;
}

.about-section-head h2 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.about-author-note {
  max-width: 820px;
}

.about-author-note h2 {
  margin: 0 0 14px;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.about-author-note p {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.95;
  color: #475569;
}

.about-author-emphasis {
  font-weight: 700;
  color: #1e3a8a !important;
}

.about-author-signoff {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  width: 100%;
}

.about-author-signature-image {
  width: min(320px, 100%);
  height: auto;
  display: block;
}

.about-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.about-card,
.about-story-card {
  padding: 18px 20px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #fafbfc;
}

.about-card h3,
.about-story-card h3 {
  margin: 0 0 10px;
  font-size: 17px;
  color: #111827;
}

.about-card p,
.about-story-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.85;
  color: #475569;
}

.about-story-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.about-scenario-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.about-scenario-item {
  padding: 15px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fafbfc;
  font-size: 14px;
  color: #334155;
}

.about-link-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.about-link-grid a {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #dbe2ea;
  background: #fff;
  color: #334155;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.about-link-grid a:hover {
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.about-footer {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 0 20px 32px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

.about-footer p,
.about-footer span {
  margin: 0;
}

@media (max-width: 960px) {
  .about-hero,
  .about-story-grid,
  .about-scenario-grid,
  .about-link-grid {
    grid-template-columns: 1fr;
  }

  .about-card-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .about-nav {
    padding: 14px 18px;
  }

  .about-nav-actions a:not(.about-nav-btn) {
    display: none;
  }

  .about-main {
    padding: 18px 14px 48px;
  }

  .about-hero,
  .about-section {
    padding: 22px 18px;
  }

  .about-meta {
    padding: 2px 12px;
  }

  .about-meta-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .about-actions a {
    width: 100%;
  }
}
</style>
