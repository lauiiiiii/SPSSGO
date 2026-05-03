<template>
  <div>
    <div class="dp-tip-banner">
      异常值可能是明显偏离整体分布的离群点，也可能是超出合理范围的数据点。处理后可将异常值置空，或替换为其它有效值。
    </div>

    <div class="dp-config-hint" style="margin-bottom: 14px;">
      输入：一项或以上的定量变量。输出：对异常值置空，或对异常值进行填补。多列处理中各列独立判断，互不影响。
    </div>

    <div class="dp-config-step">
      <span class="dp-step-num">1</span>
      <span>异常值识别</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.outlierDetect" value="auto" /> 自动识别</label>
      <label><input type="radio" v-model="options.outlierDetect" value="custom" /> 自定义识别</label>
    </div>

    <div class="dp-radio-group dp-radio-indent" v-if="options.outlierDetect === 'auto'">
      <label><input type="radio" v-model="options.outlierMethod" value="mad" /> MAD 异常值识别</label>
      <label><input type="radio" v-model="options.outlierMethod" value="iqr" /> IQR 异常值识别</label>
      <label><input type="radio" v-model="options.outlierMethod" value="3sigma" /> 3σ 异常值识别</label>
    </div>

    <div class="dp-config-hint" v-if="options.outlierDetect === 'auto'">
      <template v-if="options.outlierMethod === 'mad'">
        MAD 基于中位数绝对偏差，稳健性较强，少量极端值对结果影响较小，适合存在偏态分布的数据。
      </template>
      <template v-else-if="options.outlierMethod === 'iqr'">
        IQR 以四分位距为基础，通常将低于 Q1 - 1.5×IQR 或高于 Q3 + 1.5×IQR 的值视为异常值。
      </template>
      <template v-else>
        3σ 准则是最常见的异常值识别方法。若某个值超出均值 ± 3 倍标准差范围，则视为异常值。
      </template>
    </div>

    <div v-if="options.outlierDetect === 'custom'" class="dp-inline-form">
      <span>自定义范围：</span>
      <input class="dp-input dp-input-sm" v-model.number="options.outlierMin" placeholder="最小值" style="width:96px" />
      <span>~</span>
      <input class="dp-input dp-input-sm" v-model.number="options.outlierMax" placeholder="最大值" style="width:96px" />
    </div>
    <div v-if="options.outlierDetect === 'custom'" class="dp-config-hint">
      不在该范围内的数据将被视为异常值。
    </div>

    <div class="dp-config-step" style="margin-top:16px">
      <span class="dp-step-num">2</span>
      <span>处理方式</span>
    </div>
    <div class="dp-radio-group">
      <label><input type="radio" v-model="options.outlierAction" value="null" /> 置为空值</label>
      <label><input type="radio" v-model="options.outlierAction" value="replace" /> 替换为其它有效值</label>
    </div>

    <select v-if="options.outlierAction === 'replace'" class="dp-select" v-model="options.outlierReplace">
      <option value="">请选择</option>
      <option value="custom">自定义值</option>
      <option value="mean">平均值</option>
      <option value="median">中位数</option>
      <option value="mode">众数</option>
      <option value="zero">数字 0</option>
      <option value="random">随机有效值</option>
    </select>
    <input
      v-if="options.outlierAction === 'replace' && options.outlierReplace === 'custom'"
      class="dp-input"
      v-model="options.outlierCustomVal"
      placeholder="请输入自定义替换值"
    />

    <div class="dp-config-hint" style="margin-top: 14px;">
      注意：异常值处理不支持含空值变量，请先完成缺失值处理。若将异常值置空，后续通常还需要进入缺失值处理继续处理这些空值。
    </div>
  </div>
</template>

<script setup>
defineProps({ options: { type: Object, required: true } })
</script>
