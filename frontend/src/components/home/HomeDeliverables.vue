<template>
  <section id="deliverables" class="py-24 px-8 text-center bg-slate-50">
    <div class="max-w-7xl mx-auto px-9">
      <span class="inline-block px-3.5 py-1 rounded-2xl bg-indigo-50 text-indigo-500 text-xs font-semibold tracking-wide mb-4 anim" data-anim="fade-up">分析成果</span>
      <h2 class="text-4xl font-bold text-slate-900 mb-3 anim" data-anim="fade-up">你将获得这些专业交付物</h2>
      <p class="text-base text-slate-400 mb-12 anim" data-anim="fade-up">统计引擎真实运算，每一个数值都可复现、可验证，直接用于论文和报告</p>
      <div class="grid grid-cols-4 gap-5 text-left anim" data-anim="fade-up">
        <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-transparent">
          <div class="h-40 bg-gray-50 relative flex items-center justify-center p-4 border-b border-slate-100">
            <table class="w-full border-collapse text-xs">
              <thead><tr class="border-t-2 border-b border-gray-700"><th class="px-2 py-1.5 text-center font-semibold text-gray-700">变量</th><th class="px-2 py-1.5 text-center font-semibold text-gray-700">M</th><th class="px-2 py-1.5 text-center font-semibold text-gray-700">SD</th><th class="px-2 py-1.5 text-center font-semibold text-gray-700">t</th><th class="px-2 py-1.5 text-center font-semibold text-gray-700">p</th></tr></thead>
              <tbody>
                <tr><td class="px-2 py-1 text-center text-gray-500">实验组</td><td class="px-2 py-1 text-center text-gray-500">4.23</td><td class="px-2 py-1 text-center text-gray-500">0.87</td><td class="px-2 py-1 text-center text-gray-500">2.41</td><td class="px-2 py-1 text-center text-gray-500">.018*</td></tr>
                <tr class="border-b-2 border-gray-700"><td class="px-2 py-1 text-center text-gray-500">对照组</td><td class="px-2 py-1 text-center text-gray-500">3.76</td><td class="px-2 py-1 text-center text-gray-500">0.92</td><td class="px-2 py-1 text-center text-gray-500"></td><td class="px-2 py-1 text-center text-gray-500"></td></tr>
              </tbody>
            </table>
            <span class="absolute top-2.5 right-2.5 inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-gray-200 text-xs text-gray-500 font-medium">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M11 5V3.5A1.5 1.5 0 009.5 2h-6A1.5 1.5 0 002 3.5v6A1.5 1.5 0 003.5 11H5" stroke="currentColor" stroke-width="1.2"/></svg>
              复制
            </span>
          </div>
          <h4 class="text-base font-semibold text-slate-800 pt-4 px-5 pb-1">APA 三线表</h4>
          <p class="text-xs text-slate-400 leading-relaxed px-5 pb-5">自动生成规范三线表，一键复制粘贴到论文</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-transparent">
          <div class="h-40 bg-gray-50 relative flex items-center justify-center pt-5 px-6 pb-3 border-b border-slate-100">
            <div class="flex items-end gap-4 h-full w-full">
              <div class="flex-1 flex flex-col items-center gap-1.5 h-full justify-end"><div class="w-full rounded-t-md bg-linear-to-b from-indigo-300 to-indigo-200 transition-all duration-500" style="height:55%"></div><span class="text-xs text-slate-400 font-medium">A</span></div>
              <div class="flex-1 flex flex-col items-center gap-1.5 h-full justify-end"><div class="w-full rounded-t-md bg-linear-to-b from-indigo-500 to-purple-600 transition-all duration-500" style="height:82%"></div><span class="text-xs text-slate-400 font-medium">B</span></div>
              <div class="flex-1 flex flex-col items-center gap-1.5 h-full justify-end"><div class="w-full rounded-t-md bg-linear-to-b from-indigo-300 to-indigo-200 transition-all duration-500" style="height:68%"></div><span class="text-xs text-slate-400 font-medium">C</span></div>
              <div class="flex-1 flex flex-col items-center gap-1.5 h-full justify-end"><div class="w-full rounded-t-md bg-linear-to-b from-indigo-300 to-indigo-200 transition-all duration-500" style="height:45%"></div><span class="text-xs text-slate-400 font-medium">D</span></div>
            </div>
          </div>
          <h4 class="text-base font-semibold text-slate-800 pt-4 px-5 pb-1">统计图表</h4>
          <p class="text-xs text-slate-400 leading-relaxed px-5 pb-5">自动可视化分析结果，直观展示数据趋势</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-transparent">
          <div class="h-40 bg-gray-50 relative flex flex-col items-start gap-2.5 p-4 border-b border-slate-100">
            <div class="px-2.5 py-0.5 rounded-md bg-linear-to-br from-indigo-500 to-purple-600 text-white text-xs font-bold">AI</div>
            <div class="text-xs text-gray-600 leading-relaxed">独立样本T检验显示，实验组 (M=4.23) 显著高于对照组 (M=3.76)，t(198)=2.41, p=.018&lt;.05，效应量 Cohen's d=0.52...</div>
          </div>
          <h4 class="text-base font-semibold text-slate-800 pt-4 px-5 pb-1">AI 智能解读</h4>
          <p class="text-xs text-slate-400 leading-relaxed px-5 pb-5">AI 自动解读统计结果，给出专业分析建议</p>
        </div>
        <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-transparent">
          <div class="h-40 bg-gray-50 relative flex flex-col items-stretch gap-2.5 py-3.5 px-4 border-b border-slate-100">
            <div class="flex gap-1.5">
              <span class="px-3.5 py-1 rounded-md text-xs font-medium bg-indigo-500 text-white">Word</span>
              <span class="px-3.5 py-1 rounded-md text-xs font-medium text-slate-400 bg-slate-100">PPT</span>
            </div>
            <div class="flex flex-col gap-1.5 flex-1">
              <div class="h-1.5 rounded-sm bg-gray-200 w-full"></div>
              <div class="h-1.5 rounded-sm bg-gray-200 w-2/3"></div>
              <div class="rounded overflow-hidden border border-slate-100">
                <div class="h-4 bg-gray-100"></div>
                <div class="h-3.5 border-t border-gray-100 bg-white"></div>
                <div class="h-3.5 border-t border-gray-100 bg-white"></div>
              </div>
              <div class="h-1.5 rounded-sm bg-gray-200 w-1/2"></div>
            </div>
          </div>
          <h4 class="text-base font-semibold text-slate-800 pt-4 px-5 pb-1">专业报告</h4>
          <p class="text-xs text-slate-400 leading-relaxed px-5 pb-5">一键生成论文、市场分析报告，更多模板持续扩展</p>
        </div>
      </div>
    </div>
  </section>
</template>
