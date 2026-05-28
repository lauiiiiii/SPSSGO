<script setup>
import { ref } from 'vue'
import { faqItems } from '@/data/homePageContent.js'

const faqOpen = ref(-1)
</script>

<template>
  <section id="faq" class="py-24 px-8 text-center bg-gray-50">
    <div class="max-w-7xl mx-auto px-9">
      <span class="inline-block px-3.5 py-1 rounded-2xl bg-indigo-50 text-indigo-500 text-xs font-semibold tracking-wide mb-4 anim" data-anim="fade-up">常见问题</span>
      <h2 class="text-4xl font-bold text-slate-900 mb-3 anim" data-anim="fade-up">你可能想知道的</h2>
      <p class="text-base text-slate-400 mb-12 anim" data-anim="fade-up">还有其他问题？欢迎联系我们</p>
      <div class="max-w-2xl mx-auto text-left anim" data-anim="fade-up">
        <div v-for="(item, i) in faqItems" :key="i" class="border border-slate-100 rounded-xl mb-3 bg-white overflow-hidden transition-shadow duration-200 hover:shadow-sm" :class="faqOpen === i ? 'shadow-sm' : ''">
          <button class="w-full px-5 py-4 border-0 bg-transparent text-base font-semibold text-slate-800 flex items-center justify-between gap-3 cursor-pointer text-left transition-colors duration-200 hover:text-indigo-500" @click="faqOpen = faqOpen === i ? -1 : i">
            <span>{{ item.q }}</span>
            <svg :class="['shrink-0 transition-transform duration-300 text-gray-400', faqOpen === i ? 'rotate-180 text-indigo-500' : '']" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div :class="['overflow-hidden transition-all duration-300 px-5', faqOpen === i ? 'max-h-56 pb-4' : 'max-h-0']">
            <p class="text-sm text-gray-500 leading-relaxed">{{ item.a }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
