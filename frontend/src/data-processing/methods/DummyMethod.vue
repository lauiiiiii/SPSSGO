<template>
  <div>
    <div class="dp-tip-banner">
      无序定类变量不能直接参与回归计算，通常需要先转换成虚拟变量。虚拟变量转换包括独热编码和哑变量化。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：1 项定类变量。输出：新生成的哑变量或独热编码变量。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>转换方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.dummyMode" value="dummy" /> 哑变量化</label>
      <label><input type="radio" v-model="options.dummyMode" value="onehot" /> 独热编码</label>
    </div>

    <div class="dp-config-hint">
      <template v-if="options.dummyMode === 'onehot'">
        独热编码会为每个分类水平生成一个 0/1 变量。例如有 3 个类别，就会生成 3 列编码变量。
      </template>
      <template v-else>
        哑变量化会比独热编码少一列，未生成的那一列作为参照项，更适合直接用于回归分析以避免完全共线性。
      </template>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：虚拟变量转换不支持对存在空值的变量进行处理，需要提前处理空值。若你希望自行决定参照项，通常可先做独热编码，再在回归时手动排除其中一列作为参照项。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
