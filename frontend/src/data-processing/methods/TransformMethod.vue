<template>
  <div>
    <div class="dp-tip-banner">
      数据变换用于将原始数据转换成更适合分析的形式，可用于改善正态性、降低噪声、提取频域信息，或让数据更符合模型假设。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：1 个无空值定量变量。输出：变换后的新序列。适用于非正态数据、信号降噪、频域分析等场景。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>变换方式</span>
    </div>
    <select class="dp-select" v-model="options.transformMethod">
      <option value="fourier">傅里叶变换</option>
      <option value="inverse_fourier">傅里叶逆变换</option>
      <option value="boxcox">Box-Cox 变换</option>
      <option value="inverse_boxcox">Box-Cox 逆变换</option>
      <option value="cwt">连续小波变换</option>
      <option value="dwt">离散小波变换</option>
      <option value="johnson">Johnson 变换</option>
      <option value="yeojohnson">Yeo-Johnson 变换</option>
    </select>

    <div class="dp-config-hint">
      <template v-if="options.transformMethod === 'fourier'">
        傅里叶变换可将时域信号转换到频域，适合提取频域信息。
      </template>
      <template v-else-if="options.transformMethod === 'inverse_fourier'">
        傅里叶逆变换用于将频域结果恢复回时域序列。
      </template>
      <template v-else-if="options.transformMethod === 'boxcox'">
        Box-Cox 变换用于将正值数据变换得更接近正态分布，以满足线性模型的基本假设。
      </template>
      <template v-else-if="options.transformMethod === 'inverse_boxcox'">
        Box-Cox 逆变换用于把 Box-Cox 变换后的结果还原回原分布尺度。
      </template>
      <template v-else-if="options.transformMethod === 'cwt'">
        连续小波变换可以同时提取时域和频域的局部信息，适合非平稳信号分析。
      </template>
      <template v-else-if="options.transformMethod === 'dwt'">
        离散小波变换适合做一级小波分解和降噪，强调频域特征提取。
      </template>
      <template v-else-if="options.transformMethod === 'johnson'">
        Johnson 变换会在不同 Johnson 系列中选择更合适的形式，把非正态数据转换得更接近正态分布。
      </template>
      <template v-else>
        Yeo-Johnson 变换与 Box-Cox 类似，但支持零值和负值，更适合一般数值型数据正态化。
      </template>
    </div>

    <div v-if="['boxcox', 'inverse_boxcox'].includes(options.transformMethod)" class="dp-form-row" style="margin-top: 14px;">
      <label>Lambda（可选）</label>
      <input class="dp-input" v-model.number="options.transformLambda" placeholder="留空自动估计" />
    </div>

    <div v-if="options.transformMethod === 'inverse_boxcox'" class="dp-form-row">
      <label>平移常数</label>
      <input class="dp-input" v-model.number="options.transformShift" placeholder="默认 0" />
    </div>

    <div v-if="['cwt', 'dwt'].includes(options.transformMethod)" class="dp-form-row" style="margin-top: 14px;">
      <label>小波基函数</label>
      <select class="dp-select" v-model="options.transformWavelet">
        <template v-if="options.transformMethod === 'cwt'">
          <option value="morl">Morlet</option>
          <option value="mexh">Mexican Hat</option>
          <option value="gaus1">Gaussian 1</option>
          <option value="cgau1">Complex Gaussian 1</option>
        </template>
        <template v-else>
          <option value="haar">Haar</option>
          <option value="db2">Daubechies(db2)</option>
          <option value="db4">Daubechies(db4)</option>
          <option value="sym4">Symlet(sym4)</option>
        </template>
      </select>
    </div>

    <div class="dp-toggle-row" style="margin-top:16px">
      <span>生成新变量</span>
      <label class="dp-toggle">
        <input type="checkbox" v-model="options.transformNewVar" />
        <span class="dp-toggle-slider"></span>
      </label>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：数据变换不支持对存在空值的变量进行处理，需要提前处理空值。Box-Cox 要求数据为正值；Yeo-Johnson 支持零值和负值；傅里叶与小波变换更适合有序序列数据。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
