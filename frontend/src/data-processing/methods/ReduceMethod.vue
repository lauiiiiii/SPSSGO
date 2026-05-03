<template>
  <div>
    <div class="dp-tip-banner">
      数据降维用于将多个原始变量映射为更少的低维变量，在减少噪声和冗余的同时，尽量保留原始数据中的有效信息。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：至少 2 个无空值定量变量。输出：新生成降维后的 M 个变量序列（M&lt;N）。适用于高维、稀疏或存在冗余信息的数据场景。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>降维方法</span>
    </div>
    <select class="dp-select" v-model="options.reduceMethod">
      <option value="pca">PCA 降维</option>
      <option value="lda">线性判别法（LDA）</option>
      <option value="isomap">ISOMap</option>
      <option value="lle">LLE</option>
      <option value="kpca">KPCA</option>
      <option value="tsne">t-SNE</option>
    </select>

    <div class="dp-config-hint">
      <template v-if="options.reduceMethod === 'pca'">
        PCA 是无监督降维方法，适合通过主成分保留原始变量的大部分方差信息。
      </template>
      <template v-else-if="options.reduceMethod === 'lda'">
        LDA 是监督降维方法，需要分类目标变量，强调类别之间的可分性。
      </template>
      <template v-else-if="options.reduceMethod === 'isomap'">
        ISOMap 是流形学习方法，强调保持样本点之间的测地距离，适合复杂非线性结构。
      </template>
      <template v-else-if="options.reduceMethod === 'lle'">
        LLE 通过保持局部线性关系来实现降维，适合存在局部线性结构的数据。
      </template>
      <template v-else-if="options.reduceMethod === 'kpca'">
        KPCA 是核主成分分析，通过核函数捕捉非线性结构，适合线性 PCA 难以分离的数据。
      </template>
      <template v-else>
        t-SNE 适合高维数据的低维可视化，能更好地呈现样本局部邻近关系，但不同运行结果可能存在差异。
      </template>
    </div>

    <div v-if="options.reduceMethod === 'lda'" class="dp-config-step" style="margin-top: 16px;">
      <span class="dp-step-num">2</span>
      <span>目标变量</span>
    </div>
    <div v-if="options.reduceMethod === 'lda'" class="dp-form-row">
      <label>目标变量（分类变量）</label>
      <select class="dp-select" v-model="options.reduceTarget">
        <option value="">请选择</option>
        <option v-for="v in catVars" :key="v.name" :value="v.name">{{ v.display_name || v.name }}</option>
      </select>
    </div>

    <div class="dp-config-step" :style="{ marginTop: '16px' }">
      <span class="dp-step-num">{{ options.reduceMethod === 'lda' ? 3 : 2 }}</span>
      <span>降维参数</span>
    </div>

    <template v-if="options.reduceMethod === 'pca'">
      <div class="dp-radio-group">
        <label><input type="radio" v-model="options.reducePcaMode" value="variance_ratio" /> 总方差解释率</label>
        <label><input type="radio" v-model="options.reducePcaMode" value="components" /> 主成分个数</label>
      </div>

      <div class="dp-form-row" style="margin-top: 14px;">
        <label>{{ options.reducePcaMode === 'variance_ratio' ? '总方差解释率' : '主成分个数' }}</label>
        <input
          v-if="options.reducePcaMode === 'variance_ratio'"
          class="dp-input"
          type="number"
          v-model.number="options.reduceVarianceRatio"
          min="0.01"
          max="0.999"
          step="0.01"
          placeholder="0.8"
        />
        <input
          v-else
          class="dp-input"
          type="number"
          v-model.number="options.reduceComponents"
          min="1"
          step="1"
          :max="Math.max(selectedCount - 1, 1)"
          placeholder="2"
        />
      </div>
    </template>

    <template v-else>
      <div class="dp-form-row">
        <label>降维后变量个数</label>
        <input
          class="dp-input"
          type="number"
          v-model.number="options.reduceComponents"
          min="1"
          step="1"
          :max="Math.max(selectedCount - 1, 1)"
          placeholder="2"
        />
      </div>
    </template>

    <div v-if="['isomap', 'lle', 'tsne'].includes(options.reduceMethod)" class="dp-form-row" style="margin-top: 14px;">
      <label>邻居数</label>
      <input class="dp-input" type="number" v-model.number="options.reduceNeighbors" min="2" step="1" placeholder="5" />
    </div>

    <div v-if="options.reduceMethod === 'kpca'" class="dp-form-row" style="margin-top: 14px;">
      <label>核函数</label>
      <select class="dp-select" v-model="options.reduceKernel">
        <option value="rbf">RBF</option>
        <option value="poly">Poly</option>
        <option value="sigmoid">Sigmoid</option>
        <option value="cosine">Cosine</option>
      </select>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：数据降维不支持对存在空值的变量进行处理，需要提前处理空值。PCA 支持按总方差解释率自动确定维度；LDA 需要额外提供定类目标变量。
    </div>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Object, required: true },
  catVars: { type: Array, default: () => [] },
  selectedCount: { type: Number, default: 0 },
})
</script>
