<template>
  <div class="home">
    <HomeNavBar @login-click="showLogin = true" />

    <HomeHero @login-click="showLogin = true" />

    <HomeGeneration />

    <HomeWorkflow />

    <HomeTrustGuarantee />

    <!-- ===== 深度特性展示（4 大块） ===== -->
    <section id="showcase" class="showcase">
      <div class="section-inner">
        <span class="section-tag anim" data-anim="fade-up">深度特性</span>
        <h2 class="anim" data-anim="fade-up">每一步，都为你精心设计</h2>
        <p class="section-desc anim" data-anim="fade-up">高度 AI 集成的在线 SPSS，让数据分析不再困难</p>

        <!-- Block 1: AI 对话入口 -->
        <div class="showcase-item anim" data-anim="fade-up">
          <div class="showcase-text">
            <div class="showcase-num">01</div>
            <h3>把需求交给 AI，剩下的交给我们</h3>
            <p>不知道该用什么分析方法？没关系。上传数据和问卷，用自然语言描述你的研究目标，AI 会一步步引导你明确需求，自动匹配最佳分析方案。</p>
            <ul class="showcase-checks">
              <li>支持上传数据 + Word 问卷</li>
              <li>自然语言描述研究目标即可</li>
              <li>不懂统计方法也能轻松上手</li>
            </ul>
          </div>
          <div class="showcase-visual">
            <div class="showcase-mock mock-ai-chat">
              <div class="mock-bar">
                <span class="mock-dot"></span><span class="mock-dot"></span><span class="mock-dot"></span>
              </div>
              <div class="mock-body">
                <div class="sc-chat-msg sc-user">
                  <div class="sc-bubble">我想研究不同教学方法对学生成绩的影响，数据已上传</div>
                </div>
                <div class="sc-chat-msg sc-ai">
                  <div class="sc-bubble">
                    收到！我注意到你的数据包含 3 组教学方法和对应成绩。建议使用<strong>单因素方差分析 (ANOVA)</strong> 来检验组间差异，再用 <strong>Tukey HSD</strong> 做事后比较。需要我生成分析计划吗？
                  </div>
                </div>
                <div class="sc-input-mock">
                  <span>告诉 AI 你想分析什么...</span>
                  <span class="sc-send-icon">
                    <svg width="14" height="14" viewBox="0 0 18 18" fill="none"><path d="M9 14V4M4 8l5-5 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Block 2: 智能分析计划 -->
        <div class="showcase-item showcase-item-reverse anim" data-anim="fade-up">
          <div class="showcase-text">
            <div class="showcase-num">02</div>
            <h3>AI 先出计划，确认后再执行</h3>
            <p>AI 不会黑盒运行，更不会编造结果。它先生成完整的分析计划，列出每一步要做的事。你可以查看、编辑、调整，确认后再一键执行 &mdash; 真正的统计引擎运算，不是 AI 幻觉。</p>
            <ul class="showcase-checks">
              <li>每一步分析方法透明可见</li>
              <li>AI 规划方案，统计引擎计算结果</li>
              <li>相同数据相同参数，结果 100% 可复现</li>
            </ul>
          </div>
          <div class="showcase-visual">
            <div class="showcase-mock mock-plan">
              <div class="mock-bar">
                <span class="mock-dot"></span><span class="mock-dot"></span><span class="mock-dot"></span>
              </div>
              <div class="mock-body">
                <div class="sc-plan-title">AI 分析计划</div>
                <div class="sc-plan-list">
                  <div class="sc-plan-item"><span class="sc-plan-check done">&#10003;</span><span>1. 信效度分析 (Cronbach's &alpha;)</span></div>
                  <div class="sc-plan-item"><span class="sc-plan-check done">&#10003;</span><span>2. 描述统计分析</span></div>
                  <div class="sc-plan-item"><span class="sc-plan-check done">&#10003;</span><span>3. 独立样本T检验 (性别差异)</span></div>
                  <div class="sc-plan-item"><span class="sc-plan-check done">&#10003;</span><span>4. 相关性分析</span></div>
                  <div class="sc-plan-item"><span class="sc-plan-check done">&#10003;</span><span>5. 多元线性回归</span></div>
                </div>
                <div class="sc-plan-actions">
                  <span class="sc-btn-outline">修改计划</span>
                  <span class="sc-btn-primary">确认并执行 &rarr;</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Block 3: 拖拽执行工作台 -->
        <div class="showcase-item anim" data-anim="fade-up">
          <div class="showcase-text">
            <div class="showcase-num">03</div>
            <h3>拖拽执行，即时出结果</h3>
            <p>进入结构化分析工作台，像 SPSS 一样专业，但比 SPSS 简单十倍。拖拽选择变量，可视化配置参数，点击运行，统计引擎即时返回真实结果 &mdash; 每个数值都可溯源、可复现。</p>
            <ul class="showcase-checks">
              <li>拖拽式变量选择，参数全程可控</li>
              <li>统计引擎真实运算，非 AI 生成数字</li>
              <li>支持 200+ 统计方法，结果可反复验证</li>
            </ul>
          </div>
          <div class="showcase-visual">
            <div class="showcase-mock mock-workbench">
              <div class="mock-bar">
                <span class="mock-dot"></span><span class="mock-dot"></span><span class="mock-dot"></span>
              </div>
              <div class="mock-body">
                <div class="sc-method-tag">多元线性回归</div>
                <div class="sc-var-row">
                  <span class="sc-var-chip chip-blue">因变量: 就业焦虑</span>
                </div>
                <div class="sc-var-row">
                  <span class="sc-var-chip chip-green">自变量: 自我效能感</span>
                  <span class="sc-var-chip chip-green">自变量: 社会支持</span>
                </div>
                <div class="sc-config-row">
                  <span class="sc-config-item">显著性: 0.05</span>
                  <span class="sc-config-item active">方法: 逐步回归</span>
                </div>
                <div class="sc-run-btn">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 2l10 6-10 6V2z" fill="currentColor"/></svg>
                  开始分析
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Block 4: 报告生成 -->
        <div class="showcase-item showcase-item-reverse anim" data-anim="fade-up">
          <div class="showcase-text">
            <div class="showcase-num">04</div>
            <h3>勾选结果，一键生成报告</h3>
            <p>分析完成后，所有三线表、图表、AI 解读一目了然。勾选你需要的结果，选择报告模板，一键生成论文、市场分析报告或汇报 PPT。</p>
            <ul class="showcase-checks">
              <li>APA 格式三线表一键复制</li>
              <li>AI 自动解读统计结果</li>
              <li>多种报告模板持续扩展中</li>
            </ul>
          </div>
          <div class="showcase-visual">
            <div class="showcase-mock mock-report">
              <div class="mock-bar">
                <span class="mock-dot"></span><span class="mock-dot"></span><span class="mock-dot"></span>
              </div>
              <div class="mock-body">
                <div class="sc-report-select">
                  <div class="sc-report-item selected">
                    <span class="sc-checkbox checked">&#10003;</span>
                    <span>描述统计表</span>
                  </div>
                  <div class="sc-report-item selected">
                    <span class="sc-checkbox checked">&#10003;</span>
                    <span>回归分析结果</span>
                  </div>
                  <div class="sc-report-item selected">
                    <span class="sc-checkbox checked">&#10003;</span>
                    <span>相关系数矩阵</span>
                  </div>
                </div>
                <div class="sc-template-row">
                  <span class="sc-tpl active">学术论文</span>
                  <span class="sc-tpl">市场报告</span>
                  <span class="sc-tpl">汇报 PPT</span>
                </div>
                <div class="sc-run-btn">生成报告 &rarr;</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <HomeDeliverables />

    <HomeFAQ />

    <HomeCTA @login-click="showLogin = true" />

    <HomeFooter @login-click="showLogin = true" />

    <HomeLoginModal v-if="showLogin" @close="showLogin = false" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { checkToken } from '@/api.js'
import HomeLoginModal from '@/components/home/HomeLoginModal.vue'
import HomeNavBar from '@/components/home/HomeNavBar.vue'
import HomeHero from '@/components/home/HomeHero.vue'
import HomeGeneration from '@/components/home/HomeGeneration.vue'
import HomeWorkflow from '@/components/home/HomeWorkflow.vue'
import HomeDeliverables from '@/components/home/HomeDeliverables.vue'
import HomeFAQ from '@/components/home/HomeFAQ.vue'
import HomeTrustGuarantee from '@/components/home/HomeTrustGuarantee.vue'
import HomeFooter from '@/components/home/HomeFooter.vue'
import HomeCTA from '@/components/home/HomeCTA.vue'
import { useScrollReveal } from '@/composables/shared/useScrollReveal.js'

const showLogin = ref(false)
useScrollReveal()

onMounted(() => {
  const token = localStorage.getItem('spssgo_token')
  if (token) {
    checkToken(token)
      .then(ok => { if (ok) window.location.href = '/workspace' })
      .catch(() => {})
  }
})
</script>

<style>
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  color: #1f2937;
  background: linear-gradient(180deg, #f8fafd 0%, #f6f8fb 100%);
  -webkit-font-smoothing: antialiased;
}
.home {
  background: transparent;
}

/* ===== Scroll Animation ===== */
.anim {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity .6s ease-out, transform .6s ease-out;
}
.anim-visible {
  opacity: 1;
  transform: translateY(0);
}

.btn-ghost > svg {
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
.btn-ghost > .gitee-mark {
  width: 22px;
  height: 22px;
  flex-basis: 22px;
}

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px; padding: 12px 28px; border-radius: 10px;
  background: #4F6EF7; color: #fff; font-size: 15px; font-weight: 600;
  text-decoration: none; transition: all .25s; border: none; cursor: pointer; font-family: inherit;
}
.btn-primary:hover { filter: brightness(.96); box-shadow: 0 6px 24px color-mix(in srgb, #4F6EF7 35%, transparent); transform: translateY(-2px); }
.btn-lg { padding: 14px 36px; font-size: 16px; border-radius: 12px; }
.btn-ghost {
  display: inline-flex; align-items: center; padding: 12px 28px; border-radius: 10px;
  border: 1.5px solid #e5e7eb; color: #4b5563; font-size: 15px; font-weight: 500;
  text-decoration: none; transition: all .2s; background: rgba(255,255,255,.6);
  backdrop-filter: blur(4px);
}
.btn-ghost:hover { border-color: #d1d5db; background: #f9fafb; }


/* ===== Section Common ===== */
.section-inner { max-width: 1200px; margin: 0 auto; padding: 0 36px; }
.section-tag {
  display: inline-block; padding: 5px 14px; border-radius: 16px;
  background: #f0f4ff; color: #4F6EF7; font-size: 12px; font-weight: 600;
  letter-spacing: 1px; margin-bottom: 16px;
}
.workflow h2, .showcase h2, .generation h2 {
  font-size: 34px; font-weight: 700; color: #0f172a; margin-bottom: 12px;
}
.generation h2 { font-size: 40px; }
.section-desc { font-size: 15px; color: #94a3b8; margin-bottom: 52px; }
.generation .section-desc { font-size: 17px; }




/* ===== Showcase (Deep Features) ===== */
.showcase { padding: 100px 32px; background: #fcfdff; text-align: center; }
.showcase-item {
  display: flex; align-items: center; gap: 60px;
  text-align: left; margin-bottom: 80px;
}
.showcase-item:last-child { margin-bottom: 0; }
.showcase-item-reverse { flex-direction: row-reverse; }
.showcase-text { flex: 1; min-width: 0; }
.showcase-visual { flex: 0 0 420px; }
.showcase-num {
  font-size: 48px; font-weight: 800; color: #f0f2f5; letter-spacing: -2px;
  line-height: 1; margin-bottom: 12px;
}
.showcase-text h3 { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 12px; }
.showcase-text > p { font-size: 15px; color: #6b7280; line-height: 1.75; margin-bottom: 20px; }
.showcase-checks { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.showcase-checks li {
  font-size: 14px; color: #4b5563; padding-left: 24px; position: relative;
}
.showcase-checks li::before {
  content: ''; position: absolute; left: 0; top: 3px;
  width: 16px; height: 16px; border-radius: 50%;
  background: #ecfdf5; border: 1.5px solid #10b981;
}
.showcase-checks li::after {
  content: ''; position: absolute; left: 4px; top: 7px;
  width: 5px; height: 3px;
  border-left: 1.5px solid #10b981; border-bottom: 1.5px solid #10b981;
  transform: rotate(-45deg);
}

/* -- Showcase Mock UI Cards -- */
.showcase-mock {
  border-radius: 14px; overflow: hidden;
  border: 1px solid #e8eaef; background: #fff;
  box-shadow: 0 4px 24px rgba(0,0,0,.06);
}
.mock-body { padding: 20px; }

/* -- Showcase Block 1: AI Chat -- */
.sc-chat-msg { margin-bottom: 12px; }
.sc-chat-msg:last-of-type { margin-bottom: 0; }
.sc-user { display: flex; justify-content: flex-end; }
.sc-user .sc-bubble {
  background: #4F6EF7; color: #fff;
  border-radius: 12px 12px 4px 12px;
  padding: 12px 16px; font-size: 13px; line-height: 1.6;
  max-width: 85%;
}
.sc-ai .sc-bubble {
  background: #f5f7fa; color: #1e293b;
  border-radius: 12px 12px 12px 4px;
  padding: 12px 16px; font-size: 13px; line-height: 1.7;
  max-width: 95%;
}
.sc-input-mock {
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #eef0f4;
  background: #f8f9fb;
  font-size: 12px; color: #b0b5c0;
  display: flex; justify-content: space-between; align-items: center;
}
.sc-send-icon {
  width: 26px; height: 26px; border-radius: 6px;
  background: #4F6EF7; color: #fff;
  display: flex; align-items: center; justify-content: center;
}

/* -- Showcase Block 2: Plan -- */
.sc-plan-title {
  font-size: 15px; font-weight: 700; color: #0f172a;
  margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #f0f2f5;
}
.sc-plan-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }
.sc-plan-item {
  display: flex; align-items: center; gap: 10px;
  font-size: 14px; color: #374151;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f8f9fb;
}
.sc-plan-check {
  width: 20px; height: 20px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.sc-plan-check.done {
  background: #10b981; color: #fff;
}
.sc-plan-actions { display: flex; gap: 10px; }
.sc-btn-outline {
  flex: 1; padding: 9px; text-align: center; border-radius: 8px;
  border: 1.5px solid #e5e7eb; font-size: 13px; color: #6b7280; font-weight: 500;
  background: #fff;
}
.sc-btn-primary {
  flex: 1; padding: 9px; text-align: center; border-radius: 8px;
  background: #4F6EF7; color: #fff; font-size: 13px; font-weight: 600;
}

/* -- Showcase Block 3: Workbench -- */
.sc-method-tag {
  display: inline-block; padding: 4px 12px; border-radius: 6px;
  background: #f0f4ff; color: #4F6EF7; font-size: 12px; font-weight: 600;
  margin-bottom: 14px;
}
.sc-var-row { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.sc-var-chip {
  padding: 7px 14px; border-radius: 8px; font-size: 13px; font-weight: 500;
}
.chip-blue { background: #dbeafe; color: #2563eb; }
.chip-green { background: #d1fae5; color: #059669; }
.sc-config-row { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.sc-config-item {
  padding: 6px 12px; border-radius: 6px; font-size: 12px; color: #6b7280;
  background: #f5f6f8; border: 1px solid #eef0f4;
}
.sc-config-item.active {
  background: #f0f4ff; color: #4F6EF7; border-color: rgba(79,110,247,.2);
}
.sc-run-btn {
  padding: 10px; text-align: center; border-radius: 8px;
  background: #4F6EF7; color: #fff; font-size: 14px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}

/* -- Showcase Block 4: Report -- */
.sc-report-select { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.sc-report-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 8px;
  background: #f8f9fb; font-size: 13px; color: #374151;
}
.sc-report-item.selected { background: #f0f4ff; }
.sc-checkbox {
  width: 20px; height: 20px; border-radius: 5px;
  border: 1.5px solid #d1d5db;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; color: transparent; flex-shrink: 0;
}
.sc-checkbox.checked {
  background: #4F6EF7; border-color: #4F6EF7; color: #fff;
}
.sc-template-row { display: flex; gap: 8px; margin-bottom: 16px; }
.sc-tpl {
  flex: 1; padding: 8px; text-align: center; border-radius: 8px;
  font-size: 12px; font-weight: 500; color: #6b7280;
  background: #f5f6f8; border: 1.5px solid #eef0f4;
}
.sc-tpl.active {
  background: #f0f4ff; color: #4F6EF7; border-color: rgba(79,110,247,.3);
  font-weight: 600;
}



/* ===== Login Modal ===== */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(15,23,42,.34);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn .2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  display: flex;
  width: 720px; max-width: calc(100vw - 40px);
  min-height: 460px;
  background: #fff; border-radius: 16px;
  box-shadow: 0 20px 56px rgba(15,23,42,.2);
  position: relative;
  overflow: hidden;
  animation: modalIn .25s ease-out;
}
@keyframes modalIn {
  from { opacity: 0; transform: translateY(16px) scale(.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-close {
  position: absolute; top: 12px; right: 14px; z-index: 2;
  width: 32px; height: 32px; border: none; background: none;
  font-size: 22px; color: #9ca3af; cursor: pointer;
  border-radius: 8px; transition: all .15s;
  display: flex; align-items: center; justify-content: center;
}
.modal-close:hover { background: #f3f4f6; color: #4b5563; }

.modal-brand {
  flex: 0 0 280px;
  background: linear-gradient(165deg, #4d76e6 0%, #5b83ec 58%, #6077e8 100%);
  padding: 36px 28px;
  display: flex;
  flex-direction: column;
  color: #fff;
  border-right: 1px solid rgba(255,255,255,.16);
  position: relative;
  overflow: hidden;
}
.modal-brand::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.12) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: .16;
  pointer-events: none;
}
.modal-brand::after {
  content: '';
  position: absolute;
  right: -56px;
  top: -72px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.22);
  box-shadow: -36px 46px 0 -24px rgba(255,255,255,.16);
  pointer-events: none;
}
.modal-brand-logo {
  height: 40px; width: auto;
  filter: brightness(0) invert(1);
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}
.modal-brand-slogan {
  font-size: 14px;
  color: rgba(255,255,255,.85);
  margin-bottom: 32px;
  letter-spacing: .5px;
  position: relative;
  z-index: 1;
}
.modal-brand-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: auto;
  position: relative;
  z-index: 1;
}
.modal-brand-list li {
  font-size: 13px;
  color: rgba(255,255,255,.92);
  padding-left: 22px;
  position: relative;
  line-height: 1.4;
}
.modal-brand-list li::before {
  content: '';
  position: absolute;
  left: 0; top: 4px;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: rgba(255,255,255,.2);
  border: 1.5px solid rgba(255,255,255,.6);
  box-sizing: border-box;
}
.modal-brand-list li::after {
  content: '';
  position: absolute;
  left: 3px; top: 7px;
  width: 5px; height: 3px;
  border-left: 1.5px solid #fff;
  border-bottom: 1.5px solid #fff;
  transform: rotate(-45deg);
}

.modal-form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px 32px;
}
.modal-form-inner {
  width: 100%;
  max-width: 300px;
}
.modal-form-inner h3 {
  font-size: 22px; font-weight: 700; color: #111827; margin-bottom: 4px;
}
.modal-greeting {
  font-size: 13px; color: #9ca3af; margin-bottom: 28px;
}

.modal-form { display: flex; flex-direction: column; gap: 14px; }
.m-form-group { display: flex; flex-direction: column; }
.m-form-group input {
  width: 100%; padding: 11px 14px;
  border: 1px solid #e5e7eb; border-radius: 8px;
  font-size: 14px; outline: none; font-family: inherit;
  transition: border-color .2s, box-shadow .2s;
  background: #fff; color: #1f2937;
}
.m-form-group input::placeholder { color: #c5c9d2; }
.m-form-group input:focus {
  border-color: #4F6EF7;
  box-shadow: 0 0 0 2px rgba(79,110,247,.1);
}

.m-error {
  color: #ef4444; font-size: 13px; text-align: center;
  background: #fef2f2; padding: 8px 12px; border-radius: 8px;
}

.m-consent {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.6;
  cursor: pointer;
  user-select: none;
}
.m-consent input {
  margin-top: 2px;
  width: 16px;
  height: 16px;
  accent-color: #4F6EF7;
  cursor: pointer;
  flex-shrink: 0;
}
.m-consent a {
  color: #6b7280;
  text-decoration: none;
}
.m-consent a:hover {
  color: #4F6EF7;
  text-decoration: underline;
}

.m-btn {
  padding: 11px; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 600;
  background: linear-gradient(135deg, #3f7ee6 0%, #4e86ea 100%);
  color: #fff;
  cursor: pointer; transition: all .2s; font-family: inherit;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  margin-top: 4px;
}
.m-btn:hover { box-shadow: 0 6px 18px rgba(62, 126, 230, .32); filter: saturate(1.05); }
.m-btn:active { transform: scale(.98); }
.m-btn:disabled { opacity: .6; cursor: not-allowed; transform: none; box-shadow: none; }

.m-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: #fff;
  border-radius: 50%; animation: spin .6s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== Responsive ===== */
@media (max-width: 1080px) {
  .hero-content { flex-direction: column; text-align: center; gap: 40px; min-height: auto; }
  .hero-left { text-align: center; }
  .hero-actions { justify-content: center; }
  .hero-right { flex: none; width: 100%; max-width: 420px; }
  .hero-mockup { transform: none; }
  .hero-mockup:hover { transform: none; }
  .hero-stats { margin: 0 auto; }
  .deliv-grid { grid-template-columns: repeat(2, 1fr); }
  .tg-row { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 960px) {
  .tg-row { grid-template-columns: 1fr; }
  .gen-row { flex-direction: column; align-items: center; gap: 16px; }
  .gen-arrow { transform: rotate(90deg); width: auto; height: 32px; }
  .gen-card { max-width: 100%; width: 100%; }
  .gen-hero-content { flex-direction: column; gap: 20px; }
  .gen-hero-right { grid-template-columns: 1fr; gap: 8px; }
  .gen-hero-list { min-width: 0; width: 100%; }
  .footer-inner-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
  .showcase-item, .showcase-item-reverse { flex-direction: column; gap: 36px; }
  .showcase-visual { flex: none; width: 100%; max-width: 420px; margin: 0 auto; }
}
@media (max-width: 768px) {
  .nav-links a:not(.nav-btn):not(.nav-github) { display: none; }
  .hero { padding: 120px 24px 64px; }
  .hero h1 { font-size: 32px; letter-spacing: -.5px; }
  .hero h1 br { display: none; }
  .hero-copy-stage { min-height: 268px; }
  .hero-desc { font-size: 15px; }
  .hero h1 { min-height: auto; }
  .hero-desc { min-height: auto; }
  .hero-desc br { display: none; }
  .hero-note { font-size: 11px; }
  .hero-note-below { margin: 14px auto 0; min-height: 0; }
  .hero-stats { flex-direction: column; border-radius: 12px; padding: 12px 0; gap: 0; }
  .hero-stat { padding: 10px 24px; }
  .hero-stat-sep { width: 60%; height: 1px; margin: 0 auto; }
  .wf-row { flex-wrap: wrap; gap: 12px; }
  .wf-line { display: none; }
  .wf-step { flex: 0 0 calc(33% - 8px); }
  .deliv-grid { grid-template-columns: 1fr; }
  .footer-inner-grid { grid-template-columns: 1fr; gap: 28px; }
  .modal-brand { display: none; }
  .modal-card { width: 400px; }
}
@media (max-width: 480px) {
  .wf-step { flex: 0 0 calc(50% - 8px); }
  .hero h1 { font-size: 28px; }
  .hero-copy-stage { min-height: 356px; }
}
</style>
