<template>
  <div>
    <div class="dp-tip-banner">
      特征筛选用于从原始特征中挑出更有效的变量，降低噪声和模型复杂度，并在变量名后标明“应保留”或“应剔除”。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：至少 2 个无空值定量变量。输出：在变量名后标明应保留还是应剔除。特征筛选更适合变量较多、希望控制过拟合或提升解释性的场景。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>筛选方法</span>
    </div>
    <select class="dp-select" v-model="options.featureMethod">
      <option value="variance">方差选择法</option>
      <option value="random_forest">随机森林特征重要度</option>
      <option value="xgboost">XGBoost</option>
      <option value="pearson">相关系数法</option>
      <option value="mutual_info">互信息法</option>
      <option value="chi2">卡方检验法</option>
      <option value="vif">VIF 法</option>
      <option value="rfe">递归特征消除法</option>
    </select>

    <div class="dp-config-hint">
      <template v-if="options.featureMethod === 'variance'">
        方差选择法会过滤方差较低的特征，适合快速预处理。它不依赖目标变量，但也不会考虑特征与目标变量的直接关系。
      </template>
      <template v-else-if="options.featureMethod === 'random_forest'">
        随机森林会根据特征在树分裂中的贡献度进行排序，适合非线性关系较明显的场景。
      </template>
      <template v-else-if="options.featureMethod === 'xgboost'">
        XGBoost 会根据提升树中的特征增益评估重要性，再保留贡献度较高的变量。
      </template>
      <template v-else-if="options.featureMethod === 'pearson'">
        相关系数法通过 Pearson 系数绝对值衡量每个特征与目标变量的线性相关程度，目标变量需为定量变量。
      </template>
      <template v-else-if="options.featureMethod === 'mutual_info'">
        互信息法衡量特征与目标变量之间的关联程度，互信息越大，说明变量越值得保留。
      </template>
      <template v-else-if="options.featureMethod === 'chi2'">
        卡方检验法根据卡方值大小对特征排序，通常用于分类目标变量，且所有待筛选特征应为非负数。
      </template>
      <template v-else-if="options.featureMethod === 'vif'">
        VIF 法用于识别多重共线性，VIF 越高说明该特征越容易被其他特征解释，通常需要优先剔除。
      </template>
      <template v-else>
        递归特征消除法会反复训练模型并剔除贡献较小的特征，逐轮逼近更优的特征组合。
      </template>
    </div>

    <div v-if="needsTarget" class="dp-config-step" style="margin-top: 16px;">
      <span class="dp-step-num">2</span>
      <span>目标变量</span>
    </div>
    <div v-if="needsTarget" class="dp-form-row">
      <label>目标变量</label>
      <select class="dp-select" v-model="options.featureTarget">
        <option value="">请选择</option>
        <option v-for="v in allVars" :key="v.name" :value="v.name">{{ v.display_name || v.name }}</option>
      </select>
    </div>

    <div class="dp-config-step" :style="{ marginTop: needsTarget ? '16px' : '16px' }">
      <span class="dp-step-num">{{ needsTarget ? 3 : 2 }}</span>
      <span>筛选参数</span>
    </div>

    <div v-if="options.featureMethod === 'variance'" class="dp-form-row">
      <label>最小方差阈值</label>
      <input class="dp-input" type="number" v-model.number="options.featureVarianceThreshold" step="0.01" min="0" placeholder="0.01" />
    </div>

    <div v-else-if="options.featureMethod === 'vif'" class="dp-form-row">
      <label>VIF 阈值</label>
      <input class="dp-input" type="number" v-model.number="options.featureVifThreshold" step="0.1" min="1.1" placeholder="5" />
    </div>

    <div v-else class="dp-form-row">
      <label>目标维度</label>
      <input class="dp-input" type="number" v-model.number="options.featureKeepCount" step="1" min="1" :max="Math.max(selectedCount, 1)" placeholder="5" />
    </div>

    <div class="dp-config-hint">
      <template v-if="options.featureMethod === 'variance'">
        方差低于阈值的变量会被标记为“应剔除”；其余变量标记为“应保留”。
      </template>
      <template v-else-if="options.featureMethod === 'vif'">
        系统会不断移除 VIF 过高的变量，直到剩余特征的共线性降到阈值以内或只剩 1 个特征。
      </template>
      <template v-else>
        系统会按得分高低排序，仅保留前 {{ options.featureKeepCount || 0 }} 个变量，其余变量标记为“应剔除”。
      </template>
    </div>

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：特征筛选不支持对存在空值的变量进行处理，需要提前处理空值。XGBoost、随机森林、互信息、卡方、RFE 等方法都依赖目标变量；方差和 VIF 方法不依赖目标变量。
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  options: { type: Object, required: true },
  selectedCount: { type: Number, default: 0 },
  numericVars: { type: Array, default: () => [] },
  catVars: { type: Array, default: () => [] },
})

const allVars = computed(() => [...props.numericVars, ...props.catVars])
const needsTarget = computed(() => !['variance', 'vif'].includes(props.options.featureMethod))
</script>
