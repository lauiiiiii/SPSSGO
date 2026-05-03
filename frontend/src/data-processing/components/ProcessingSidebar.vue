<template>
  <div class="dp-sidebar">
    <div class="dp-sidebar-path">
      数据处理<template v-if="dataFileName"> / {{ dataFileName }}</template>
    </div>

    <div class="dp-sidebar-section">通用方法</div>
    <div class="dp-method-grid">
      <button
        v-for="method in methods"
        :key="method.key"
        class="dp-method-btn"
        :class="{ active: activeMethod === method.key }"
        @click="$emit('open-method', method.key)"
      >{{ method.label }}</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  dataFileName: { type: String, default: '' },
  activeMethod: { type: String, default: '' },
  methods: { type: Array, default: () => [] },
})

defineEmits(['open-method'])
</script>
