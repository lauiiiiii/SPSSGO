<template>
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
</template>

<style scoped>
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
</style>
