<script setup>
defineEmits(["login-click"]);
</script>

<template>
  <section class="pt-20 px-8 pb-24 text-center bg-slate-100">
    <div
      class="max-w-7xl mx-auto py-16 px-12 rounded-3xl bg-linear-to-br from-white via-blue-50 to-indigo-50 border border-slate-200 shadow-xl anim"
      data-anim="fade-up"
    >
      <h2 class="text-4xl font-bold text-slate-900 mb-3">
        准备好让 AI 帮你分析了吗？
      </h2>
      <p class="text-base text-slate-500 mb-8">
        上传数据，描述需求，AI 自动规划 + 执行 + 生成报告。永久免费，永久开源。
      </p>
      <div class="flex gap-3.5 justify-center items-center flex-wrap">
        <a
          class="px-8 py-3.5 rounded-xl bg-blue-600 text-white text-base font-medium no-underline transition-all duration-200 hover:bg-blue-700"
          href="#"
          @click.prevent="$emit('login-click')"
          >立即开始</a
        >
        <a
          class="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-700 text-base font-medium no-underline transition-all duration-200 hover:bg-slate-50 hover:border-slate-400 hover:text-slate-900"
          href="https://github.com/lauiiiiii/spssgo"
          target="_blank"
        >
          <svg class="size-4" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
            />
          </svg>
          GitHub
        </a>
        <a
          class="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-700 text-base font-medium no-underline transition-all duration-200 hover:bg-slate-50 hover:border-slate-400 hover:text-slate-900"
          href="https://gitee.com/jahge/SPSSGO"
          target="_blank"
        >
          <svg
            class="size-5 shrink-0 text-red-600"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M12 2.5a9.5 9.5 0 1 0 0 19 9.5 9.5 0 0 0 0-19Zm4.75 8.2h-5.58a.95.95 0 0 0-.95.95v.7h4.25c.52 0 .95.43.95.95v.36a3.1 3.1 0 0 1-3.1 3.1H7.85a.95.95 0 0 1-.95-.95v-5.74a3.1 3.1 0 0 1 3.1-3.1h6.75c.52 0 .95.43.95.95v1.83c0 .52-.43.95-.95.95Z"
              fill="currentColor"
            />
          </svg>
          Gitee
        </a>
      </div>
    </div>
  </section>
</template>
