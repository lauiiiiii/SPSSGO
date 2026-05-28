<script setup>
defineEmits(["login-click"]);

const wechatQrSrc = "/wechat-qrcode.jpg";
</script>

<template>
  <footer class="bg-white border-t border-slate-200">
    <div class="pt-14 pb-10">
      <div class="max-w-7xl mx-auto flex flex-row justify-between">
        <div class="max-w-lg">
          <img
            class="h-7 w-auto opacity-95 mb-2"
            src="/logo.png"
            alt="SPSSGO"
          />
          <p class="m-0 text-xs text-slate-500 leading-relaxed mb-2.5">
            Smart Processing Statistical System Guided Operations
          </p>
          <p class="text-sm text-slate-700 leading-relaxed mb-3">
            AI 驱动的永久免费在线数据分析工作台
          </p>
          <p class="text-xs text-slate-400 leading-relaxed mb-4">
            永久免费 · 永久开源 · AGPL-3.0
          </p>
          <div class="flex gap-2.5">
            <a
              href="https://github.com/lauiiiiii/spssgo"
              target="_blank"
              title="GitHub"
              class="flex items-center justify-center size-8 rounded-lg bg-slate-100 text-slate-500 transition-all duration-200 no-underline hover:bg-slate-200 hover:text-slate-900"
            >
              <svg class="size-4" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
                />
              </svg>
            </a>
            <a
              href="https://gitee.com/jahge/SPSSGO"
              target="_blank"
              title="Gitee"
              class="flex items-center justify-center size-8 rounded-lg bg-slate-100 text-slate-500 transition-all duration-200 no-underline hover:bg-slate-200 hover:text-slate-900"
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
            </a>
            <a
              href="mailto:jahe@jahe.top"
              title="邮箱"
              class="flex items-center justify-center size-8 rounded-lg bg-slate-100 text-slate-500 transition-all duration-200 no-underline hover:bg-slate-200 hover:text-slate-900"
            >
              <svg
                class="size-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="M22 4L12 13 2 4" />
              </svg>
            </a>
          </div>
        </div>
        <div class="flex flex-col gap-2.5">
          <h4
            class="text-xs font-semibold text-slate-500 tracking-wide uppercase mb-1.5"
          >
            产品
          </h4>
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="#workflow"
            >分析闭环</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="#showcase"
            >深度特性</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="#deliverables"
            >分析成果</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/about"
            >关于我们</a
          >
        </div>
        <div class="flex flex-col gap-2.5">
          <h4
            class="text-xs font-semibold text-slate-500 tracking-wide uppercase mb-1.5"
          >
            支持
          </h4>
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/help"
            >帮助中心</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/changelog"
            >更新日志</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="#faq"
            >常见问题</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="mailto:jahe@jahe.top"
            >联系我们</a
          >
        </div>
        <div class="flex flex-col gap-2.5">
          <h4
            class="text-xs font-semibold text-slate-500 tracking-wide uppercase mb-1.5"
          >
            法律
          </h4>
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/legal#terms"
            target="_blank"
            >用户服务协议</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/legal#privacy"
            target="_blank"
            >隐私政策</a
          >
          <a
            class="text-sm text-slate-600 no-underline transition-colors duration-200 hover:text-slate-900"
            href="/legal#license"
            target="_blank"
            >开源协议 (AGPL-3.0)</a
          >
        </div>
        <div class="flex flex-col gap-2.5 items-start">
          <h4
            class="text-xs font-semibold text-slate-500 tracking-wide uppercase mb-1.5"
          >
            公众号
          </h4>
          <img
            class="size-28 object-cover border border-slate-200 rounded-xl bg-white p-1"
            :src="wechatQrSrc"
            alt="SPSSGO 数据公众号二维码"
          />
          <span class="text-xs text-slate-500 leading-relaxed"
            >扫码关注 SPSSGO 数派</span
          >
        </div>
      </div>
    </div>
    <div class="border-t border-slate-100 px-9 py-4">
      <div
        class="max-w-7xl mx-auto flex items-center justify-center gap-2 flex-wrap"
      >
        <p class="text-xs text-slate-400">
          &copy; {{ new Date().getFullYear() }} 日照广泰佳和网络科技有限公司
        </p>
        <span class="text-xs text-slate-300">&middot;</span>
        <p class="text-xs text-slate-400">SPSSGO 3.0 数据分析工作台 社区版</p>
      </div>
    </div>
  </footer>
</template>
