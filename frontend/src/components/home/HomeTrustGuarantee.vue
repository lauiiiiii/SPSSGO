<script setup></script>

<template>
  <section class="trust-guarantee">
    <div class="section-inner">
      <div class="tg-row anim" data-anim="fade-up">
        <div class="tg-card">
          <div class="tg-icon tg-icon-engine">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <h4>统计引擎真实运算</h4>
          <p>所有 P 值、t 值、F 值均由专业统计引擎计算，不是 AI 编造的数字</p>
        </div>
        <div class="tg-card">
          <div class="tg-icon tg-icon-reproduce">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path
                d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"
              />
            </svg>
          </div>
          <h4>结果 100% 可复现</h4>
          <p>
            相同数据 + 相同参数 = 相同结果，每次运行完全一致，经得起反复验证
          </p>
        </div>
        <div class="tg-card">
          <div class="tg-icon tg-icon-transparent">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
          <h4>过程透明可审计</h4>
          <p>AI 只负责规划方案，不参与数值计算，分析过程和参数配置全程可见</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
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
  transition:
    box-shadow 0.3s,
    transform 0.3s;
}
.tg-card:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
  border-color: transparent;
}
.tg-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
.tg-icon-engine {
  background: #fef3c7;
  color: #d97706;
}
.tg-icon-reproduce {
  background: #d1fae5;
  color: #059669;
}
.tg-icon-transparent {
  background: #dbeafe;
  color: #2563eb;
}
.tg-card h4 {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.tg-card p {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.65;
}
</style>
