<template>
  <div class="home">
    <!-- ===== 导航栏 ===== -->
    <nav class="nav">
      <div class="nav-inner">
        <div class="nav-brand">
          <img class="nav-logo" src="/logo.png" alt="SPSSGO" />
          <span class="nav-version">3.0</span>
        </div>
        <div class="nav-links">
          <a href="#workflow">工作流</a>
          <a href="#showcase">特性</a>
          <a href="#deliverables">成果</a>
          <a href="/about">关于我们</a>
          <a href="#faq">FAQ</a>
          <a href="https://github.com/lauiiiiii/spssgo" target="_blank" class="nav-github">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          </a>
          <a class="nav-btn" href="#" @click.prevent="showLogin = true">登录</a>
        </div>
      </div>
    </nav>

    <!-- ===== Hero（左右分栏） ===== -->
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
            <a class="btn-primary btn-hero" href="#" @click.prevent="showLogin = true">
              开始让 AI 规划分析
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </a>
            <a class="btn-ghost" href="https://github.com/lauiiiiii/spssgo" target="_blank">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
              GitHub
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

    <!-- ===== 代际演进 ===== -->
    <section class="generation">
      <div class="section-inner">
        <span class="section-tag anim" data-anim="fade-up">数据分析的进化之路</span>
        <h2 class="anim" data-anim="fade-up">为什么我们是第三代</h2>
        <p class="section-desc anim" data-anim="fade-up">从桌面软件到在线搬运，从伪 AI 到真正的 AI 深度驱动 &mdash; SPSSGO 是数据分析的下一个形态</p>
        <!-- 上排：第一代 + 第二代 -->
        <div class="gen-row anim" data-anim="fade-up">
          <div class="gen-card gen-card-old">
            <div class="gen-badge gen-badge-1">第一代</div>
            <h4>桌面统计软件</h4>
            <div class="gen-name">SPSS / SAS / Stata</div>
            <ul class="gen-list">
              <li class="gen-con">需要安装，动辄数 GB</li>
              <li class="gen-con">操作复杂，学习曲线陡峭</li>
              <li class="gen-con">授权费用高昂</li>
              <li class="gen-con">结果需手动整理到论文</li>
            </ul>
          </div>
          <div class="gen-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </div>
          <div class="gen-card gen-card-old">
            <div class="gen-badge gen-badge-2">第二代</div>
            <h4>在线统计工具</h4>
            <div class="gen-name">SPSSAU / SPSSPRO 等</div>
            <ul class="gen-list">
              <li class="gen-pro">无需安装，浏览器可用</li>
              <li class="gen-con">本质是桌面 SPSS 的网页搬运</li>
              <li class="gen-con">后期加的 AI 仅浅层辅助</li>
              <li class="gen-con">仍需用户自行选择分析方法</li>
            </ul>
          </div>
          <div class="gen-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </div>
          <div class="gen-card gen-card-warn">
            <div class="gen-badge gen-badge-warn">伪 AI</div>
            <h4>工具 + AI 按钮</h4>
            <div class="gen-name">传统工具硬加 AI 入口</div>
            <ul class="gen-list">
              <li class="gen-pro">有 AI 辅助入口</li>
              <li class="gen-con">AI 只是附加功能，未深度集成</li>
              <li class="gen-con">核心流程仍是手动操作</li>
              <li class="gen-con">AI 与分析引擎各自为战</li>
            </ul>
          </div>
          <div class="gen-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </div>
          <div class="gen-card gen-card-warn">
            <div class="gen-badge gen-badge-warn">伪 AI</div>
            <h4>对话式 AI 分析</h4>
            <div class="gen-name">大模型套壳 / AI 直出结果</div>
            <ul class="gen-list">
              <li class="gen-pro">能用自然语言交互</li>
              <li class="gen-con">AI 直接编造统计结果</li>
              <li class="gen-con">每次输出不一致，无法复现</li>
              <li class="gen-con">幻觉严重，数据不可信</li>
            </ul>
          </div>
        </div>
        <!-- 下排：第三代（突出） -->
        <div class="gen-hero-wrap anim" data-anim="fade-up">
          <div class="gen-hero-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
          </div>
          <div class="gen-card gen-card-new gen-card-hero">
            <div class="gen-badge gen-badge-3">第三代</div>
            <div class="gen-hero-content">
              <div class="gen-hero-left">
                <h4>AI 深度驱动 + 统计引擎 &mdash; SPSSGO</h4>
                <p class="gen-hero-desc">不是给 SPSS 加个 AI 按钮，也不是让大模型编造数据。<br/>SPSSGO 从架构层面重新设计：AI 全程深度参与需求理解、方案规划、结果解读和报告生成，而所有统计运算由专业引擎完成 &mdash; 真正做到既聪明又靠谱。</p>
              </div>
              <div class="gen-hero-right">
                <ul class="gen-list gen-hero-list">
                  <li class="gen-pro">AI 对话式交互，自然语言描述需求即可</li>
                  <li class="gen-pro">AI 自动规划完整分析方案，确认后再执行</li>
                  <li class="gen-pro">统计引擎真实运算，每个 P 值、t 值可溯源</li>
                  <li class="gen-pro">结果 100% 可复现，相同输入永远相同输出</li>
                  <li class="gen-pro">零幻觉零编造，经得起导师和审稿人审查</li>
                </ul>
                <ul class="gen-list gen-hero-list">
                  <li class="gen-pro">200+ 统计分析方法，覆盖主流研究场景</li>
                  <li class="gen-pro">APA 三线表一键复制，直接粘贴到论文</li>
                  <li class="gen-pro">AI 自动解读统计结果，给出专业分析建议</li>
                  <li class="gen-pro">勾选结果一键生成论文 / 市场报告 / PPT</li>
                  <li class="gen-pro">支持 SPSS、Excel、CSV、Stata 等 10+ 格式</li>
                  <li class="gen-pro">永久免费使用，永久开源，不收一分钱</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 五步工作流 ===== -->
    <section id="workflow" class="workflow">
      <div class="section-inner">
        <span class="section-tag anim" data-anim="fade-up">完整分析闭环</span>
        <h2 class="anim" data-anim="fade-up">从需求到报告，AI 全程驱动</h2>
        <p class="section-desc anim" data-anim="fade-up">五步完成从原始数据到专业报告的完整流程</p>
        <div class="wf-row anim" data-anim="fade-up">
          <div class="wf-step">
            <div class="wf-num">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
            </div>
            <div class="wf-label">上传数据</div>
            <div class="wf-hint">数据 / 问卷 / 研究目标</div>
          </div>
          <div class="wf-line"></div>
          <div class="wf-step">
            <div class="wf-num">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            </div>
            <div class="wf-label">AI 对话</div>
            <div class="wf-hint">澄清需求 / 推荐方法</div>
          </div>
          <div class="wf-line"></div>
          <div class="wf-step">
            <div class="wf-num">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
            </div>
            <div class="wf-label">确认计划</div>
            <div class="wf-hint">审核 / 编辑 / 确认</div>
          </div>
          <div class="wf-line"></div>
          <div class="wf-step">
            <div class="wf-num">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            </div>
            <div class="wf-label">执行分析</div>
            <div class="wf-hint">拖拽配置 / 即时运算</div>
          </div>
          <div class="wf-line"></div>
          <div class="wf-step">
            <div class="wf-num">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
            </div>
            <div class="wf-label">生成报告</div>
            <div class="wf-hint">论文 / 市场报告 / PPT</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 可信赖保证 ===== -->
    <section class="trust-guarantee">
      <div class="section-inner">
        <div class="tg-row anim" data-anim="fade-up">
          <div class="tg-card">
            <div class="tg-icon tg-icon-engine">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <h4>统计引擎真实运算</h4>
            <p>所有 P 值、t 值、F 值均由专业统计引擎计算，不是 AI 编造的数字</p>
          </div>
          <div class="tg-card">
            <div class="tg-icon tg-icon-reproduce">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
            </div>
            <h4>结果 100% 可复现</h4>
            <p>相同数据 + 相同参数 = 相同结果，每次运行完全一致，经得起反复验证</p>
          </div>
          <div class="tg-card">
            <div class="tg-icon tg-icon-transparent">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </div>
            <h4>过程透明可审计</h4>
            <p>AI 只负责规划方案，不参与数值计算，分析过程和参数配置全程可见</p>
          </div>
        </div>
      </div>
    </section>

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

    <!-- ===== 分析成果展示 ===== -->
    <section id="deliverables" class="deliverables">
      <div class="section-inner">
        <span class="section-tag anim" data-anim="fade-up">分析成果</span>
        <h2 class="anim" data-anim="fade-up">你将获得这些专业交付物</h2>
        <p class="section-desc anim" data-anim="fade-up">统计引擎真实运算，每一个数值都可复现、可验证，直接用于论文和报告</p>
        <div class="deliv-grid anim" data-anim="fade-up">
          <!-- 三线表 -->
          <div class="deliv-card">
            <div class="deliv-card-visual">
              <table class="mini-tlt">
                <thead><tr><th>变量</th><th>M</th><th>SD</th><th>t</th><th>p</th></tr></thead>
                <tbody>
                  <tr><td>实验组</td><td>4.23</td><td>0.87</td><td>2.41</td><td>.018*</td></tr>
                  <tr><td>对照组</td><td>3.76</td><td>0.92</td><td></td><td></td></tr>
                </tbody>
              </table>
              <span class="deliv-copy-btn">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
                复制
              </span>
            </div>
            <h4>APA 三线表</h4>
            <p>自动生成规范三线表，一键复制粘贴到论文</p>
          </div>
          <!-- 统计图表 -->
          <div class="deliv-card">
            <div class="deliv-card-visual deliv-chart">
              <div class="chart-bars">
                <div class="chart-col"><div class="chart-bar" style="height:55%"></div><span>A</span></div>
                <div class="chart-col"><div class="chart-bar bar-hl" style="height:82%"></div><span>B</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:68%"></div><span>C</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:45%"></div><span>D</span></div>
              </div>
            </div>
            <h4>统计图表</h4>
            <p>自动可视化分析结果，直观展示数据趋势</p>
          </div>
          <!-- AI 解读 -->
          <div class="deliv-card">
            <div class="deliv-card-visual deliv-ai">
              <div class="deliv-ai-badge">AI</div>
              <div class="deliv-ai-text">独立样本T检验显示，实验组 (M=4.23) 显著高于对照组 (M=3.76)，t(198)=2.41, p=.018&lt;.05，效应量 Cohen's d=0.52...</div>
            </div>
            <h4>AI 智能解读</h4>
            <p>AI 自动解读统计结果，给出专业分析建议</p>
          </div>
          <!-- 专业报告 -->
          <div class="deliv-card">
            <div class="deliv-card-visual deliv-report">
              <div class="deliv-report-tabs">
                <span class="deliv-tab active">Word</span>
                <span class="deliv-tab">PPT</span>
              </div>
              <div class="deliv-report-body">
                <div class="deliv-doc-line w100"></div>
                <div class="deliv-doc-line w70"></div>
                <div class="deliv-doc-table-mini">
                  <div class="deliv-doc-thead"></div>
                  <div class="deliv-doc-trow"></div>
                  <div class="deliv-doc-trow"></div>
                </div>
                <div class="deliv-doc-line w50"></div>
              </div>
            </div>
            <h4>专业报告</h4>
            <p>一键生成论文、市场分析报告，更多模板持续扩展</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== FAQ ===== -->
    <section id="faq" class="faq">
      <div class="section-inner">
        <span class="section-tag anim" data-anim="fade-up">常见问题</span>
        <h2 class="anim" data-anim="fade-up">你可能想知道的</h2>
        <p class="section-desc anim" data-anim="fade-up">还有其他问题？欢迎联系我们</p>
        <div class="faq-list anim" data-anim="fade-up">
          <div v-for="(item, i) in faqItems" :key="i" class="faq-item" :class="{ open: faqOpen === i }">
            <button class="faq-q" @click="faqOpen = faqOpen === i ? -1 : i">
              <span>{{ item.q }}</span>
              <svg class="faq-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
            </button>
            <div class="faq-a">
              <p>{{ item.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== CTA ===== -->
    <section class="cta">
      <div class="section-inner cta-inner anim" data-anim="fade-up">
        <h2>准备好让 AI 帮你分析了吗？</h2>
        <p>上传数据，描述需求，AI 自动规划 + 执行 + 生成报告。永久免费，永久开源。</p>
        <div class="cta-actions">
          <a class="btn-primary btn-lg" href="#" @click.prevent="showLogin = true">立即开始</a>
          <a class="btn-cta-github" href="https://github.com/lauiiiiii/spssgo" target="_blank">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub
          </a>
        </div>
      </div>
    </section>

    <!-- ===== Footer ===== -->
    <footer class="footer">
      <div class="footer-top">
        <div class="footer-inner-grid">
          <div class="footer-brand">
            <img class="footer-logo" src="/logo.png" alt="SPSSGO" />
            <p class="footer-brand-fullname">Smart Processing Statistical System Guided Operations</p>
            <p class="footer-brand-desc">AI 驱动的永久免费在线数据分析工作台</p>
            <p class="footer-brand-meta">永久免费 · 永久开源 · AGPL-3.0</p>
            <div class="footer-social">
              <a href="https://github.com/lauiiiiii/spssgo" target="_blank" title="GitHub" class="footer-social-link">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
              </a>
              <a href="mailto:jahe@jahe.top" title="邮箱" class="footer-social-link">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4L12 13 2 4"/></svg>
              </a>
            </div>
          </div>
          <div class="footer-col">
            <h4>产品</h4>
            <a href="#workflow">分析闭环</a>
            <a href="#showcase">深度特性</a>
            <a href="#deliverables">分析成果</a>
            <a href="/about">关于我们</a>
            <a href="#" @click.prevent="showLogin = true">开始使用</a>
          </div>
          <div class="footer-col">
            <h4>支持</h4>
            <a href="/help">帮助中心</a>
            <a href="#faq">常见问题</a>
            <a href="mailto:jahe@jahe.top">联系我们</a>
            <a href="https://github.com/lauiiiiii/spssgo" target="_blank">GitHub</a>
          </div>
          <div class="footer-col">
            <h4>法律</h4>
            <a href="/legal#terms" target="_blank">用户服务协议</a>
            <a href="/legal#privacy" target="_blank">隐私政策</a>
            <a href="/legal#license" target="_blank">开源协议 (AGPL-3.0)</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="footer-bottom-inner">
          <p>&copy; {{ new Date().getFullYear() }} 日照广泰佳和网络科技有限公司</p>
          <span class="footer-bottom-sep">&middot;</span>
          <p>SPSSGO 3.0 数据分析工作台 社区版</p>
        </div>
      </div>
    </footer>

    <HomeLoginModal v-if="showLogin" @close="showLogin = false" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { checkToken } from '../api.js'
import HomeLoginModal from '../components/home/HomeLoginModal.vue'
import { useHomeHero } from '../composables/shared/useHomeHero.js'
import { useScrollReveal } from '../composables/shared/useScrollReveal.js'
import { faqItems, heroCopies } from '../data/homePageContent.js'

const showLogin = ref(false)
const faqOpen = ref(-1)
const { activeHeroCopy, heroCopyIndex } = useHomeHero(heroCopies)
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
* { margin: 0; padding: 0; box-sizing: border-box; }
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

/* ===== Nav ===== */
.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0,0,0,.04);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 36px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-brand { display: flex; align-items: center; gap: 6px; }
.nav-logo { height: 30px; width: auto; }
.nav-version {
  font-size: 15px; font-weight: 300; color: #4F6EF7;
  background: rgba(79,110,247,.08);
  border: 1px solid rgba(79,110,247,.15);
  padding: 2px 8px; border-radius: 6px;
  letter-spacing: 1px;
  line-height: 1.4;
  font-family: "DIN Alternate", "DIN Next", "Futura", "Trebuchet MS", "Arial Narrow", sans-serif;
  font-stretch: condensed;
}
.nav-links { display: flex; align-items: center; gap: 28px; }
.nav-links a {
  font-size: 14px; color: #6b7280; text-decoration: none; transition: color .2s; font-weight: 450;
}
.nav-links a:hover { color: #1f2937; }
.nav-github {
  display: flex; align-items: center; color: #4b5563 !important;
  transition: color .2s !important;
}
.nav-github:hover { color: #1f2937 !important; }
.nav-btn {
  padding: 8px 22px !important; border-radius: 8px;
  background: #4F6EF7; color: #fff !important; font-weight: 500;
  transition: all .2s !important;
}
.nav-btn:hover { background: #4361e0 !important; color: #fff !important; box-shadow: 0 2px 10px rgba(79,110,247,.25); }

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

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px; padding: 12px 28px; border-radius: 10px;
  background: var(--hero-accent); color: #fff; font-size: 15px; font-weight: 600;
  text-decoration: none; transition: all .25s; border: none; cursor: pointer; font-family: inherit;
}
.btn-primary:hover { filter: brightness(.96); box-shadow: 0 6px 24px color-mix(in srgb, var(--hero-accent) 35%, transparent); transform: translateY(-2px); }
.btn-hero { padding: 14px 32px; font-size: 16px; border-radius: 12px; gap: 8px; }
.btn-lg { padding: 14px 36px; font-size: 16px; border-radius: 12px; }
.btn-ghost {
  display: inline-flex; align-items: center; padding: 12px 28px; border-radius: 10px;
  border: 1.5px solid #e5e7eb; color: #4b5563; font-size: 15px; font-weight: 500;
  text-decoration: none; transition: all .2s; background: rgba(255,255,255,.6);
  backdrop-filter: blur(4px);
}
.btn-ghost:hover { border-color: #d1d5db; background: #f9fafb; }

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

/* ===== Trust ===== */
.trust {
  padding: 36px 0;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
  overflow: hidden;
}
.trust-inner { max-width: 1200px; margin: 0 auto; text-align: center; }
.trust-label {
  font-size: 12px; color: #b0b5c0; letter-spacing: 1px; margin-bottom: 20px; font-weight: 500;
}
.trust-track-wrap {
  position: relative; overflow: hidden;
  mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
}
.trust-track {
  display: flex; gap: 48px; white-space: nowrap;
  animation: scrollTrack 30s linear infinite;
  width: max-content;
}
.trust-item {
  font-size: 14px; font-weight: 500; color: #c5c9d2;
  letter-spacing: .5px;
  flex-shrink: 0;
}
@keyframes scrollTrack {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

/* ===== Section Common ===== */
.section-inner { max-width: 1200px; margin: 0 auto; padding: 0 36px; }
.section-tag {
  display: inline-block; padding: 5px 14px; border-radius: 16px;
  background: #f0f4ff; color: #4F6EF7; font-size: 12px; font-weight: 600;
  letter-spacing: 1px; margin-bottom: 16px;
}
.workflow h2, .showcase h2, .deliverables h2, .faq h2, .cta h2, .generation h2 {
  font-size: 34px; font-weight: 700; color: #0f172a; margin-bottom: 12px;
}
.generation h2 { font-size: 40px; }
.section-desc { font-size: 15px; color: #94a3b8; margin-bottom: 52px; }
.generation .section-desc { font-size: 17px; }

/* ===== Generation Evolution ===== */
.generation {
  padding: 100px 32px; text-align: center; background: #fcfdff;
}
.gen-row {
  display: flex; align-items: stretch; justify-content: center; gap: 0;
}
.gen-card {
  flex: 1; max-width: 320px;
  padding: 28px 24px; border-radius: 16px;
  border: 1px solid #eef0f4; background: #fff;
  text-align: left; position: relative;
  transition: box-shadow .3s, transform .3s;
}
.gen-card:hover {
  box-shadow: 0 8px 28px rgba(0,0,0,.06);
  transform: translateY(-2px);
}
.gen-card-old {
  opacity: .85;
}
.gen-card-warn {
  border-color: rgba(239,68,68,.2);
  background: #fffbfb;
}
.gen-card-warn:hover {
  box-shadow: 0 8px 28px rgba(239,68,68,.08);
}
.gen-card-new {
  border-color: rgba(79,110,247,.3);
  background: linear-gradient(160deg, #fafaff 0%, #f0f4ff 100%);
  box-shadow: 0 4px 20px rgba(79,110,247,.1);
}
.gen-card-new:hover {
  box-shadow: 0 12px 36px rgba(79,110,247,.18);
  border-color: rgba(79,110,247,.4);
}
.gen-card-hero {
  max-width: 100%; width: 100%;
  padding: 32px 36px;
}
.gen-hero-content {
  display: flex; flex-direction: column; gap: 24px;
}
.gen-hero-left { margin-bottom: 4px; }
.gen-hero-left h4 { font-size: 22px; margin-bottom: 10px; }
.gen-hero-desc { font-size: 14px; color: #6b7280; line-height: 1.8; }
.gen-hero-right {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px 32px;
}
.gen-hero-list { min-width: 0; }
.gen-hero-wrap {
  margin-top: 24px; display: flex; flex-direction: column; align-items: center;
}
.gen-hero-arrow {
  color: #4F6EF7; margin-bottom: 16px; opacity: .5;
}
.gen-badge {
  display: inline-block; padding: 3px 12px; border-radius: 6px;
  font-size: 11px; font-weight: 700; letter-spacing: .5px; margin-bottom: 14px;
}
.gen-badge-warn { background: #fee2e2; color: #dc2626; }
.gen-badge-1 { background: #f3f4f6; color: #6b7280; }
.gen-badge-2 { background: #fef3c7; color: #b45309; }
.gen-badge-3 { background: linear-gradient(135deg, #4F6EF7, #7c3aed); color: #fff; }
.gen-card h4 {
  font-size: 17px; font-weight: 700; color: #0f172a; margin-bottom: 4px;
}
.gen-name {
  font-size: 13px; color: #94a3b8; margin-bottom: 16px; font-weight: 500;
}
.gen-list {
  list-style: none; display: flex; flex-direction: column; gap: 8px;
}
.gen-list li {
  font-size: 13px; line-height: 1.5; padding-left: 22px; position: relative;
}
.gen-con { color: #94a3b8; }
.gen-pro { color: #1e293b; font-weight: 500; }
.gen-con::before {
  content: ''; position: absolute; left: 0; top: 5px;
  width: 14px; height: 14px; border-radius: 50%;
  background: #fee2e2; border: 1.5px solid #fca5a5;
  box-sizing: border-box;
}
.gen-con::after {
  content: ''; position: absolute; left: 4px; top: 11px;
  width: 6px; height: 0; border-top: 1.5px solid #f87171;
}
.gen-pro::before {
  content: ''; position: absolute; left: 0; top: 5px;
  width: 14px; height: 14px; border-radius: 50%;
  background: #ecfdf5; border: 1.5px solid #10b981;
  box-sizing: border-box;
}
.gen-pro::after {
  content: ''; position: absolute; left: 3px; top: 9px;
  width: 5px; height: 3px;
  border-left: 1.5px solid #10b981; border-bottom: 1.5px solid #10b981;
  transform: rotate(-45deg);
}
.gen-arrow {
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; width: 48px; color: #d1d5db;
}

/* ===== Workflow (5-Step Strip) ===== */
.workflow { padding: 80px 32px; text-align: center; background: #f7f9fc; }
.wf-row {
  display: flex; align-items: flex-start; justify-content: center; gap: 0;
}
.wf-step {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  flex: 0 0 140px; text-align: center;
}
.wf-num {
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #4F6EF7, #7c3aed);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 16px rgba(79,110,247,.25);
}
.wf-label { font-size: 15px; font-weight: 600; color: #1e293b; }
.wf-hint { font-size: 12px; color: #94a3b8; line-height: 1.4; }
.wf-line {
  flex: 1;
  max-width: 80px;
  height: 2px;
  background: linear-gradient(90deg, #4F6EF7, #7c3aed);
  margin-top: 25px;
  border-radius: 1px;
  opacity: .4;
}

/* ===== Trust Guarantee ===== */
.trust-guarantee {
  padding: 0 32px 80px;
  background: #fafbfc;
}
.tg-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.tg-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #eef0f4;
  padding: 28px 24px;
  text-align: center;
  transition: box-shadow .3s, transform .3s;
}
.tg-card:hover {
  box-shadow: 0 8px 28px rgba(0,0,0,.06);
  transform: translateY(-2px);
  border-color: transparent;
}
.tg-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
}
.tg-icon-engine { background: #fef3c7; color: #d97706; }
.tg-icon-reproduce { background: #d1fae5; color: #059669; }
.tg-icon-transparent { background: #dbeafe; color: #2563eb; }
.tg-card h4 {
  font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 8px;
}
.tg-card p {
  font-size: 13px; color: #6b7280; line-height: 1.65;
}

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

/* ===== Deliverables ===== */
.deliverables { padding: 100px 32px; text-align: center; background: #f7f9fc; }
.deliv-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: left;
}
.deliv-card {
  background: #fff; border-radius: 16px; border: 1px solid #eef0f4;
  padding: 0; overflow: hidden;
  transition: box-shadow .3s, transform .3s;
}
.deliv-card:hover {
  box-shadow: 0 12px 36px rgba(0,0,0,.07);
  transform: translateY(-3px);
  border-color: transparent;
}
.deliv-card h4 {
  font-size: 15px; font-weight: 600; color: #1e293b;
  padding: 16px 20px 4px;
}
.deliv-card > p {
  font-size: 12px; color: #94a3b8; line-height: 1.6;
  padding: 0 20px 20px;
}
.deliv-card-visual {
  height: 160px; background: #f8f9fb; position: relative;
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
  border-bottom: 1px solid #f0f2f5;
}

/* -- Deliverable: Three-line Table -- */
.mini-tlt {
  width: 100%; border-collapse: collapse; font-size: 11px;
}
.mini-tlt thead tr {
  border-top: 2px solid #374151; border-bottom: 1px solid #374151;
}
.mini-tlt th {
  padding: 6px 8px; text-align: center; font-weight: 600; color: #374151;
}
.mini-tlt td {
  padding: 5px 8px; text-align: center; color: #6b7280; font-size: 11px;
}
.mini-tlt tbody tr:last-child {
  border-bottom: 2px solid #374151;
}
.deliv-copy-btn {
  position: absolute; top: 10px; right: 10px;
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 6px;
  background: #fff; border: 1px solid #e5e7eb;
  font-size: 11px; color: #6b7280; font-weight: 500;
}

/* -- Deliverable: Chart -- */
.deliv-chart { padding: 20px 24px 12px; }
.chart-bars {
  display: flex; align-items: flex-end; gap: 16px;
  height: 100%; width: 100%;
}
.chart-col {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  height: 100%;
  justify-content: flex-end;
}
.chart-bar {
  width: 100%; border-radius: 6px 6px 0 0;
  background: linear-gradient(180deg, #93a8f7, #dbe4ff);
  transition: height .4s ease;
}
.chart-bar.bar-hl {
  background: linear-gradient(180deg, #4F6EF7, #7c3aed);
}
.chart-col span { font-size: 11px; color: #94a3b8; font-weight: 500; }

/* -- Deliverable: AI Interpretation -- */
.deliv-ai {
  flex-direction: column; align-items: flex-start; gap: 10px;
  padding: 16px 18px;
}
.deliv-ai-badge {
  padding: 3px 10px; border-radius: 6px;
  background: linear-gradient(135deg, #4F6EF7, #7c3aed);
  color: #fff; font-size: 11px; font-weight: 700;
}
.deliv-ai-text {
  font-size: 12px; color: #4b5563; line-height: 1.7;
}

/* -- Deliverable: Report -- */
.deliv-report {
  flex-direction: column; align-items: stretch; gap: 10px; padding: 14px 18px;
}
.deliv-report-tabs { display: flex; gap: 6px; }
.deliv-tab {
  padding: 4px 14px; border-radius: 6px; font-size: 11px; font-weight: 500;
  color: #94a3b8; background: #eef0f4;
}
.deliv-tab.active {
  background: #4F6EF7; color: #fff;
}
.deliv-report-body {
  display: flex; flex-direction: column; gap: 6px; flex: 1;
}
.deliv-doc-line { height: 6px; border-radius: 3px; background: #e8eaef; }
.w100 { width: 100%; }
.w70 { width: 70%; }
.w50 { width: 50%; }
.deliv-doc-table-mini {
  border-radius: 4px; overflow: hidden; border: 1px solid #eef0f4;
}
.deliv-doc-thead { height: 16px; background: #f0f2f5; }
.deliv-doc-trow { height: 14px; border-top: 1px solid #f0f2f5; background: #fff; }

/* ===== FAQ ===== */
.faq { padding: 100px 32px; text-align: center; background: #fcfdff; }
.faq-list { max-width: 700px; margin: 0 auto; text-align: left; }
.faq-item {
  border: 1px solid #eef0f4; border-radius: 12px; margin-bottom: 12px;
  background: #fff; overflow: hidden; transition: box-shadow .2s;
}
.faq-item:hover { box-shadow: 0 2px 12px rgba(0,0,0,.04); }
.faq-q {
  width: 100%; padding: 18px 20px; border: none; background: none;
  font-size: 15px; font-weight: 600; color: #1e293b;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  cursor: pointer; font-family: inherit; text-align: left;
  transition: color .2s;
}
.faq-q:hover { color: #4F6EF7; }
.faq-chevron {
  flex-shrink: 0; transition: transform .25s; color: #9ca3af;
}
.faq-item.open .faq-chevron { transform: rotate(180deg); color: #4F6EF7; }
.faq-a {
  max-height: 0; overflow: hidden;
  transition: max-height .3s ease-out, padding .3s ease-out;
  padding: 0 20px;
}
.faq-item.open .faq-a {
  max-height: 220px; padding: 0 20px 18px;
}
.faq-a p { font-size: 14px; color: #6b7280; line-height: 1.7; }

/* ===== CTA ===== */
.cta { padding: 80px 32px 96px; text-align: center; background: #f3f6fa; }
.cta-inner {
  padding: 64px 48px; border-radius: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 58%, #f3f6ff 100%);
  border: 1px solid #e5ecf5;
  box-shadow: 0 18px 40px rgba(15, 23, 42, .08);
}
.cta h2 { margin-bottom: 12px; color: #0f172a !important; }
.cta p { font-size: 16px; color: #64748b; margin-bottom: 32px; }
.cta .btn-primary {
  background: #2563eb; color: #fff;
}
.cta .btn-primary:hover {
  background: #1d4ed8; box-shadow: 0 8px 22px rgba(37, 99, 235, .28);
}
.cta-actions {
  display: flex; gap: 14px; justify-content: center; align-items: center; flex-wrap: wrap;
}
.btn-cta-github {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 28px; border-radius: 12px;
  border: 1px solid #cfd8e6; color: #334155; font-size: 16px; font-weight: 500;
  text-decoration: none; transition: all .2s; background: #fff;
}
.btn-cta-github:hover {
  background: #f8fafc; border-color: #94a3b8; color: #0f172a;
}

/* ===== Footer ===== */
.footer {
  background: #ffffff;
  border-top: 1px solid #e9edf4;
}
.footer-top { padding: 56px 36px 40px; }
.footer-inner-grid {
  max-width: 1200px; margin: 0 auto;
  display: grid; grid-template-columns: minmax(420px, 2.5fr) 1fr 1fr 1fr; gap: 40px;
}
.footer-brand { max-width: 500px; }
.footer-logo { height: 28px; width: auto; opacity: .95; margin-bottom: 8px; }
.footer-brand-fullname {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 10px;
}
.footer-brand-desc { font-size: 14px; color: #334155; line-height: 1.8; margin-bottom: 12px; }
.footer-brand-meta { font-size: 12px; color: #94a3b8; line-height: 1.7; margin-bottom: 16px; }
.footer-social { display: flex; gap: 10px; }
.footer-social-link {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 8px;
  background: #f1f5f9; color: #64748b;
  transition: all .2s; text-decoration: none;
}
.footer-social-link:hover { background: #e2e8f0; color: #0f172a; }
.footer-col { display: flex; flex-direction: column; gap: 10px; }
.footer-col h4 {
  font-size: 12px; font-weight: 600; color: #64748b;
  letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px;
}
.footer-col a {
  font-size: 13px; color: #475569; text-decoration: none; transition: color .2s;
}
.footer-col a:hover { color: #0f172a; }
.footer-bottom {
  border-top: 1px solid #eef2f7;
  padding: 18px 36px;
}
.footer-bottom-inner {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  flex-wrap: wrap;
}
.footer-bottom p { font-size: 12px; color: #94a3b8; }
.footer-bottom-sep { color: #cbd5e1; font-size: 12px; }

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
