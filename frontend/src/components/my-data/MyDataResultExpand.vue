<template>
  <div v-if="result" class="md-result-expand">
    <div class="md-result-expand-head">
      <span class="md-result-expand-title">{{ result.name }}</span>
      <button class="md-result-expand-close" @click="$emit('close')">&times;</button>
    </div>
    <div class="md-result-expand-body">
      <template v-for="(r, ri) in results" :key="ri">
        <template v-if="r.sections?.length">
          <template v-for="(sec, si) in r.sections" :key="si">
            <div v-if="sec.type === 'table'" class="md-res-table-block">
              <div class="md-res-table-title">{{ sec.title }}</div>
              <div class="md-res-table-wrap">
                <table class="tlt">
                  <thead><tr><th v-for="(h, hi) in sec.headers" :key="hi">{{ h }}</th></tr></thead>
                  <tbody><tr v-for="(row, roi) in sec.rows" :key="roi"><td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td></tr></tbody>
                </table>
              </div>
              <p v-if="sec.note" class="md-res-note">{{ sec.note }}</p>
              <div v-if="sec.description" class="md-res-desc">{{ sec.description }}</div>
            </div>
            <div v-else-if="sec.type === 'advice'" class="md-res-advice">
              <strong>{{ sec.title }}</strong>
              <p>{{ sec.content }}</p>
            </div>
            <div v-else-if="sec.type === 'smart_analysis'" class="md-res-smart">
              <strong>{{ sec.title }}</strong>
              <p>{{ sec.content }}</p>
            </div>
            <div v-else-if="sec.type === 'references'" class="md-res-refs">
              <strong>{{ sec.title }}</strong>
              <ul><li v-for="(item, ii) in sec.items" :key="ii">{{ item }}</li></ul>
            </div>
          </template>
        </template>
        <template v-else>
          <div v-if="r.headers?.length" class="md-res-table-block">
            <div class="md-res-table-title">{{ r.name }}</div>
            <div class="md-res-table-wrap">
              <table class="tlt">
                <thead><tr><th v-for="(h, hi) in r.headers" :key="hi">{{ h }}</th></tr></thead>
                <tbody><tr v-for="(row, roi) in r.rows" :key="roi"><td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td></tr></tbody>
              </table>
            </div>
            <div v-if="r.description" class="md-res-desc">{{ r.description }}</div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: { type: Object, default: null },
  results: { type: Array, default: () => [] },
})

defineEmits(['close'])
</script>
