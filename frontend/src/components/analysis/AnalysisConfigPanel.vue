<template>
  <div ref="configRoot" class="ap-config">
    <div v-if="editingConfig && results.length" class="ap-report-banner">
      <span>已有本次分析结果，可随时查看完整报告页。</span>
      <button type="button" class="ap-btn ap-btn-primary ap-btn-sm" @click="$emit('show-report')">
        查看分析结果
      </button>
    </div>
    <div class="ap-method-title">
      <span class="ap-method-name">{{ method.label }}</span>
    </div>
    <div class="ap-method-desc">{{ method.description }}</div>
    <template v-if="isSummaryTMethod">
      <div class="ap-summary-t-card">
        <div class="ap-summary-t-radios">
          <label>
            <input
              type="radio"
              name="summary-t-test-type"
              :checked="optionValues.test_type !== 'independent'"
              @change="$emit('option-change', 'test_type', 'one_sample')"
            />
            单样本T检验
          </label>
          <label>
            <input
              type="radio"
              name="summary-t-test-type"
              :checked="optionValues.test_type === 'independent'"
              @change="$emit('option-change', 'test_type', 'independent')"
            />
            独立样本T检验
          </label>
        </div>

        <table v-if="optionValues.test_type !== 'independent'" class="ap-summary-stat-table">
          <thead>
            <tr>
              <th></th>
              <th>样本量</th>
              <th>平均值</th>
              <th>标准差</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>样本1</td>
              <td><input type="number" step="1" min="2" :value="optionValues.n" placeholder="请输入样本量" @input="$emit('option-change', 'n', $event.target.value)" /></td>
              <td><input type="number" step="any" :value="optionValues.mean" placeholder="请输入平均值" @input="$emit('option-change', 'mean', $event.target.value)" /></td>
              <td><input type="number" step="any" min="0" :value="optionValues.std" placeholder="请输入标准差" @input="$emit('option-change', 'std', $event.target.value)" /></td>
            </tr>
          </tbody>
        </table>

        <template v-else>
          <table class="ap-summary-stat-table">
            <thead>
              <tr>
                <th></th>
                <th>样本量</th>
                <th>平均值</th>
                <th>标准差</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>样本1</td>
                <td><input type="number" step="1" min="2" :value="optionValues.group1_n" placeholder="请输入样本量" @input="$emit('option-change', 'group1_n', $event.target.value)" /></td>
                <td><input type="number" step="any" :value="optionValues.group1_mean" placeholder="请输入平均值" @input="$emit('option-change', 'group1_mean', $event.target.value)" /></td>
                <td><input type="number" step="any" min="0" :value="optionValues.group1_std" placeholder="请输入标准差" @input="$emit('option-change', 'group1_std', $event.target.value)" /></td>
              </tr>
            </tbody>
          </table>
          <table class="ap-summary-stat-table">
            <thead>
              <tr>
                <th></th>
                <th>样本量</th>
                <th>平均值</th>
                <th>标准差</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>样本1</td>
                <td><input type="number" step="1" min="2" :value="optionValues.group2_n" placeholder="请输入样本量" @input="$emit('option-change', 'group2_n', $event.target.value)" /></td>
                <td><input type="number" step="any" :value="optionValues.group2_mean" placeholder="请输入平均值" @input="$emit('option-change', 'group2_mean', $event.target.value)" /></td>
                <td><input type="number" step="any" min="0" :value="optionValues.group2_std" placeholder="请输入标准差" @input="$emit('option-change', 'group2_std', $event.target.value)" /></td>
              </tr>
            </tbody>
          </table>
        </template>

        <div class="ap-summary-t-options">
          <label>置信度级别</label>
          <select :value="optionValues.confidence_level" @change="$emit('option-change', 'confidence_level', $event.target.value)">
            <option value="99">99%</option>
            <option value="95">95%</option>
            <option value="90">90%</option>
          </select>
          <label>检验值</label>
          <input
            type="number"
            step="any"
            :value="optionValues.test_type === 'independent' ? optionValues.diff_test_value : optionValues.test_value"
            @input="$emit('option-change', optionValues.test_type === 'independent' ? 'diff_test_value' : 'test_value', $event.target.value)"
          />
        </div>
      </div>
    </template>
    <template v-else-if="isSummaryOneWayAnovaMethod">
      <div class="ap-summary-anova-card">
        <table class="ap-summary-anova-table">
          <thead>
            <tr>
              <th>组</th>
              <th>样本量</th>
              <th>平均值</th>
              <th>标准差</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(group, index) in summaryOneWayGroups" :key="index">
              <td>
                <button
                  type="button"
                  class="ap-summary-anova-remove"
                  :disabled="summaryOneWayGroups.length <= 3"
                  @click="$emit('remove-summary-one-way-group', index)"
                >
                  −
                </button>
                <input
                  class="ap-summary-anova-group-name"
                  :value="group.label"
                  @input="$emit('update-summary-one-way-group', index, 'label', $event.target.value)"
                />
              </td>
              <td>
                <input type="number" step="1" min="2" :value="group.n" placeholder="请输入样本量" @input="$emit('update-summary-one-way-group', index, 'n', $event.target.value)" />
              </td>
              <td>
                <input type="number" step="any" :value="group.mean" placeholder="请输入平均值" @input="$emit('update-summary-one-way-group', index, 'mean', $event.target.value)" />
              </td>
              <td>
                <input type="number" step="any" min="0" :value="group.std" placeholder="请输入标准差" @input="$emit('update-summary-one-way-group', index, 'std', $event.target.value)" />
              </td>
            </tr>
          </tbody>
        </table>
        <button type="button" class="ap-summary-anova-add" @click="$emit('add-summary-one-way-group')">+增加组</button>
        <div class="ap-summary-anova-options">
          <label>置信度级别</label>
          <select :value="optionValues.confidence_level" @change="$emit('option-change', 'confidence_level', $event.target.value)">
            <option value="99">99%</option>
            <option value="95">95%</option>
            <option value="90">90%</option>
          </select>
        </div>
      </div>
    </template>
    <template v-else-if="isIndependentTMethod">
      <div class="ap-one-way-card">
        <div class="ap-one-way-options">
          <label>检验数据形式：</label>
          <select :value="optionValues.data_format" @change="$emit('option-change', 'data_format', $event.target.value)">
            <option value="样本在同一列">样本在同一列</option>
            <option value="样本在不同列">样本在不同列</option>
          </select>
        </div>

        <template v-if="optionValues.data_format === '样本在不同列'">
          <div class="ap-one-way-slot ap-one-way-slot--measure">
            <div class="ap-slot-label">
              放入
              <span class="ap-accept-tag accept-numeric">[定量]</span>
              变量Y
              <span class="ap-slot-constraint">（变量数=2）</span>
              <span v-if="slotValues.test_vars?.length" class="ap-slot-count">{{ slotValues.test_vars.length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              empty-text="拖入两个样本列到此区域"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="independentDifferentColumnSlot"
              slot-key="test_vars"
              :values="slotValues.test_vars || []"
              zone-class="ap-one-way-drop-zone ap-one-way-drop-zone--large"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>
        <template v-else>
          <div v-for="slot in independentSameColumnSlots" :key="slot.key" class="ap-one-way-slot" :class="slot.key === 'group_var' ? 'ap-one-way-slot--group' : 'ap-one-way-slot--measure'">
            <div class="ap-slot-label">
              放入{{ slot.key === 'group_var' ? '二分类' : '' }}
              <span class="ap-accept-tag" :class="'accept-' + slot.accept">[{{ getAcceptLabel(slot) }}]</span>
              {{ slot.label }}
              <span class="ap-slot-constraint">（变量数{{ slot.key === 'group_var' ? '=1' : '≥1' }}）</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="slot.hint || '拖拽变量到此区域'"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              :zone-class="slot.key === 'group_var' ? 'ap-one-way-drop-zone ap-one-way-drop-zone--small' : 'ap-one-way-drop-zone ap-one-way-drop-zone--large'"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>
      </div>
    </template>
    <template v-else-if="isOneWayAnovaMethod">
      <div class="ap-one-way-card">
        <div class="ap-one-way-options">
          <label>检验数据形式：</label>
          <select :value="optionValues.data_format" @change="$emit('option-change', 'data_format', $event.target.value)">
            <option value="样本在同一列">样本在同一列</option>
            <option value="样本在不同列">样本在不同列</option>
          </select>
        </div>

        <template v-if="optionValues.data_format === '样本在不同列'">
          <div v-for="slot in oneWayDifferentColumnSlots" :key="slot.key" class="ap-one-way-slot ap-one-way-slot--measure">
            <div class="ap-slot-label">
              放入
              <span class="ap-accept-tag accept-numeric">[定量]</span>
              {{ slot.label }}
              <span class="ap-slot-constraint">（变量数≥3）</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="slot.hint || '拖拽变量到此区域'"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              zone-class="ap-one-way-drop-zone ap-one-way-drop-zone--large"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>
        <template v-else>
          <div
            v-for="slot in oneWaySameColumnSlots"
            :key="slot.key"
            class="ap-one-way-slot"
            :class="slot.key === 'group_var' ? 'ap-one-way-slot--group' : 'ap-one-way-slot--measure'"
          >
            <div class="ap-slot-label">
              放入{{ slot.key === 'group_var' ? '分组' : '' }}
              <span class="ap-accept-tag" :class="'accept-' + slot.accept">[{{ getAcceptLabel(slot) }}]</span>
              {{ slot.label }}
              <span class="ap-slot-constraint">（变量数{{ slot.key === 'group_var' ? '=1' : '≥1' }}）</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="slot.hint || '拖拽变量到此区域'"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              :zone-class="slot.key === 'group_var' ? 'ap-one-way-drop-zone ap-one-way-drop-zone--small' : 'ap-one-way-drop-zone ap-one-way-drop-zone--large'"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>
      </div>
    </template>
    <template v-else-if="isOneSampleEquivalenceMethod">
      <div class="ap-one-eq-card">
        <div v-if="displaySlots[0]" class="ap-slot-label">
          放入
          <span v-if="getAcceptLabel(displaySlots[0])" class="ap-accept-tag" :class="'accept-' + displaySlots[0].accept">
            [{{ getAcceptLabel(displaySlots[0]) }}]
          </span>
          {{ displaySlots[0].label }}
          <span class="ap-slot-constraint">（{{ slotConstraintText(displaySlots[0]) }}）</span>
          <span v-if="slotValues[displaySlots[0].key]?.length" class="ap-slot-count">{{ slotValues[displaySlots[0].key].length }}</span>
        </div>
        <AnalysisDropZone
          v-if="displaySlots[0]"
          :drag-over-slot="dragOverSlot"
          :drag-preview-count="dragPreviewCount"
          :empty-text="displaySlots[0].hint || '拖入变量到此区域'"
          :get-var-type="getVarType"
          :get-var-type-class="getVarTypeClass"
          :slot="displaySlots[0]"
          :slot-key="displaySlots[0].key"
          :values="slotValues[displaySlots[0].key] || []"
          zone-class="ap-one-eq-drop-zone"
          @drag-over="$emit('drag-over', $event)"
          @drag-leave="$emit('drag-leave')"
          @drop-slot="(...args) => $emit('drop-slot', ...args)"
          @remove-var="(...args) => $emit('remove-var', ...args)"
        />
        <div class="ap-one-eq-options">
          <label>备择假设：</label>
          <select :value="optionValues.alternative" @change="$emit('option-change', 'alternative', $event.target.value)">
            <option value="下限<检验均值-目标值<上限">下限&lt;检验均值-目标值&lt;上限</option>
            <option value="检验均值>目标值">检验均值&gt;目标值</option>
            <option value="检验均值<目标值">检验均值&lt;目标值</option>
            <option value="检验均值-目标值>下限">检验均值-目标值&gt;下限</option>
            <option value="检验均值-目标值<上限">检验均值-目标值&lt;上限</option>
          </select>

          <label>目标值：</label>
          <input
            type="number"
            step="any"
            :value="optionValues.target_value"
            placeholder="目标值"
            @input="$emit('option-change', 'target_value', $event.target.value)"
          />

          <label>下限：</label>
          <input
            type="number"
            step="any"
            :value="optionValues.lower"
            @input="$emit('option-change', 'lower', $event.target.value)"
          />

          <label>上限：</label>
          <input
            type="number"
            step="any"
            :value="optionValues.upper"
            @input="$emit('option-change', 'upper', $event.target.value)"
          />

          <label class="ap-one-eq-check">
            <input
              type="checkbox"
              :checked="!!optionValues.scale_by_target"
              @change="$emit('option-change', 'scale_by_target', $event.target.checked)"
            />
            <span>乘以目标值</span>
            <span class="ap-option-help" data-hint="勾选后，下限和上限按目标值比例换算，例如目标值为2、上下限为±0.1时，等价区间为±0.2。">?</span>
          </label>
        </div>
      </div>
    </template>
    <template v-else-if="isTwoSampleEquivalenceMethod">
      <div class="ap-two-eq-card">
        <template v-if="optionValues.data_format === '样本在不同列'">
          <div v-for="slot in twoSampleDifferentColumnSlots" :key="slot.key" class="ap-two-eq-slot">
            <div class="ap-slot-label">
              放入
              <span class="ap-accept-tag accept-numeric">[定量]</span>
              {{ slot.label }}
              <span class="ap-slot-constraint">（变量数=1）</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="slot.hint || '拖入变量到此区域'"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              zone-class="ap-two-eq-drop-zone"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>
        <template v-else>
          <div v-for="slot in twoSampleSameColumnSlots" :key="slot.key" class="ap-two-eq-slot">
            <div class="ap-slot-label">
              放入{{ slot.key === 'test_var' ? '检验样本' : '二分类' }}
              <span class="ap-accept-tag" :class="'accept-' + slot.accept">[{{ getAcceptLabel(slot) }}]</span>
              变量
              <span class="ap-slot-constraint">（变量数=1）</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="slot.hint || '拖入变量到此区域'"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              zone-class="ap-two-eq-drop-zone"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
        </template>

        <div class="ap-two-eq-options">
          <label>检验数据形式：</label>
          <select :value="optionValues.data_format" @change="$emit('option-change', 'data_format', $event.target.value)">
            <option value="样本在同一列">样本在同一列</option>
            <option value="样本在不同列">样本在不同列</option>
          </select>

          <label>参考水平：</label>
          <select :value="optionValues.reference_level" :disabled="optionValues.data_format === '样本在不同列'" @change="$emit('option-change', 'reference_level', $event.target.value)">
            <option value="">请选择</option>
            <option value="1">1.0</option>
            <option value="2">2.0</option>
            <option value="3">3.0</option>
          </select>

          <label>相关假设：</label>
          <select :value="optionValues.relationship" @change="$emit('option-change', 'relationship', $event.target.value)">
            <option value="检验均值 - 参考均值">检验均值 - 参考均值</option>
            <option value="检验均值/参考均值">检验均值/参考均值</option>
            <option value="检验均值/参考均值(通过对数变换)">检验均值/参考均值(通过对数变换)</option>
          </select>

          <label>备择假设：</label>
          <select :value="optionValues.alternative" @change="$emit('option-change', 'alternative', $event.target.value)">
            <option value="下限<检验均值 - 参考均值<上限">下限&lt;检验均值 - 参考均值&lt;上限</option>
            <option value="检验均值>参考均值">检验均值&gt;参考均值</option>
            <option value="检验均值<参考均值">检验均值&lt;参考均值</option>
            <option value="检验均值 - 参考均值>下限">检验均值 - 参考均值&gt;下限</option>
            <option value="检验均值 - 参考均值<上限">检验均值 - 参考均值&lt;上限</option>
          </select>

          <label>下限：</label>
          <input type="number" step="any" :value="optionValues.lower" @input="$emit('option-change', 'lower', $event.target.value)" />

          <label>上限：</label>
          <input type="number" step="any" :value="optionValues.upper" @input="$emit('option-change', 'upper', $event.target.value)" />

          <label class="ap-two-eq-check">
            <input type="checkbox" :checked="!!optionValues.scale_by_reference" @change="$emit('option-change', 'scale_by_reference', $event.target.checked)" />
            <span>乘以参考均值</span>
            <span class="ap-option-help" data-hint="将上下限的值乘以参考均值。适合把相对比例转换为绝对差值的场景。">?</span>
          </label>
        </div>
      </div>
    </template>
    <template v-else-if="isPairedEquivalenceMethod">
      <div class="ap-two-eq-card">
        <div v-for="slot in pairedEquivalenceSlots" :key="slot.key" class="ap-two-eq-slot">
          <div class="ap-slot-label">
            放入
            <span class="ap-accept-tag accept-numeric">[定量]</span>
            {{ slot.label }}
            <span class="ap-slot-constraint">（变量数=1）</span>
            <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
          </div>
          <AnalysisDropZone
            :drag-over-slot="dragOverSlot"
            :drag-preview-count="dragPreviewCount"
            :empty-text="slot.hint || '拖入变量到此区域'"
            :get-var-type="getVarType"
            :get-var-type-class="getVarTypeClass"
            :slot="slot"
            :slot-key="slot.key"
            :values="slotValues[slot.key] || []"
            zone-class="ap-two-eq-drop-zone"
            @drag-over="$emit('drag-over', $event)"
            @drag-leave="$emit('drag-leave')"
            @drop-slot="(...args) => $emit('drop-slot', ...args)"
            @remove-var="(...args) => $emit('remove-var', ...args)"
          />
        </div>

        <div class="ap-two-eq-options">
          <label>相关假设：</label>
          <select :value="optionValues.relationship" @change="$emit('option-change', 'relationship', $event.target.value)">
            <option value="检验均值 - 参考均值">检验均值 - 参考均值</option>
            <option value="检验均值/参考均值">检验均值/参考均值</option>
            <option value="检验均值/参考均值(通过对数变换)">检验均值/参考均值(通过对数变换)</option>
          </select>

          <label>备择假设：</label>
          <select :value="optionValues.alternative" @change="$emit('option-change', 'alternative', $event.target.value)">
            <option value="下限<检验均值 - 参考均值<上限">下限&lt;检验均值 - 参考均值&lt;上限</option>
            <option value="检验均值>参考均值">检验均值&gt;参考均值</option>
            <option value="检验均值<参考均值">检验均值&lt;参考均值</option>
            <option value="检验均值 - 参考均值>下限">检验均值 - 参考均值&gt;下限</option>
            <option value="检验均值 - 参考均值<上限">检验均值 - 参考均值&lt;上限</option>
          </select>

          <label>下限：</label>
          <input type="number" step="any" :value="optionValues.lower" @input="$emit('option-change', 'lower', $event.target.value)" />

          <label>上限：</label>
          <input type="number" step="any" :value="optionValues.upper" @input="$emit('option-change', 'upper', $event.target.value)" />

          <label class="ap-two-eq-check">
            <input type="checkbox" :checked="!!optionValues.scale_by_reference" @change="$emit('option-change', 'scale_by_reference', $event.target.checked)" />
            <span>乘以参考均值</span>
            <span class="ap-option-help" data-hint="将上下限的值乘以参考均值。适合把相对比例转换为绝对差值的场景。">?</span>
          </label>
        </div>
      </div>
    </template>
    <template v-else-if="isCfaMethod">
      <div class="ap-slot-label">
        放入
        <span class="ap-accept-tag accept-numeric">[定量]</span>
        变量
        <span class="ap-slot-constraint">（变量数≥2）</span>
      </div>
      <div class="ap-cfa-board" :class="{ 'ap-cfa-board--with-second-order': optionValues.second_order_model }">
        <div class="ap-cfa-sidebar">
          <button type="button" class="ap-factor-btn ap-factor-btn--wide" @click="$emit('add-factor')" :disabled="dynamicFactorCount >= maxDynamicFactors">
            {{ dynamicGroupAddText }}
          </button>
          <div class="ap-cfa-factor-list">
            <button
              v-for="slot in displaySlots"
              :key="slot.key"
              type="button"
              class="ap-cfa-factor-item"
              :class="{ 'is-active': activeFactorKey === slot.key }"
              @click="$emit('select-factor', slot.key)"
            >
              <span class="ap-cfa-factor-name">{{ getFactorShortLabel(slot.key) }}</span>
              <span v-if="slotValues[slot.key]?.length" class="ap-cfa-factor-badge">{{ slotValues[slot.key].length }}</span>
              <span class="ap-cfa-factor-menu-wrap">
                <button type="button" class="ap-cfa-factor-more" @click.stop="$emit('toggle-factor-menu', slot.key)">...</button>
                <div v-if="factorMenuKey === slot.key" class="ap-cfa-factor-menu">
                  <button type="button" class="ap-cfa-factor-menu-item" @click.stop="$emit('rename-factor', slot.key)">
                    重命名
                  </button>
                  <button type="button" class="ap-cfa-factor-menu-item is-danger" @click.stop="$emit('delete-factor', slot.key)" :disabled="dynamicFactorCount <= 1">
                    删除
                  </button>
                </div>
              </span>
            </button>
          </div>
          <div class="ap-factor-tip">{{ dynamicGroupTip }}</div>
        </div>
        <div class="ap-cfa-main">
          <div class="ap-cfa-main-head">
            <label class="ap-cfa-title-edit">
              <input
                ref="titleInputRef"
                class="ap-cfa-title-input"
                :value="activeFactorTitle"
                @change="$emit('rename-factor-inline', activeFactorKey, $event.target.value)"
              />
              <span class="ap-cfa-title-edit-btn" title="重命名">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </span>
            </label>
            <span class="ap-cfa-main-sub">{{ activeFactorItems.length }} 个{{ dynamicGroupItemName }}</span>
          </div>
          <AnalysisDropZone
            v-if="activeFactorSlot"
            :drag-over-slot="dragOverSlot"
            :drag-preview-count="dragPreviewCount"
            :empty-text="`将待分析变量拖入到 ${activeFactorTitle}`"
            :get-var-type="getVarType"
            :get-var-type-class="getVarTypeClass"
            :slot="activeFactorSlot"
            :slot-key="activeFactorKey"
            :values="activeFactorItems"
            zone-class="ap-cfa-drop-zone"
            @drag-over="$emit('drag-over', $event)"
            @drag-leave="$emit('drag-leave')"
            @drop-slot="(...args) => $emit('drop-slot', ...args)"
            @remove-var="(...args) => $emit('remove-var', ...args)"
            @zone-click="$emit('close-factor-menu')"
          />
        </div>
      </div>
      <div v-if="optionValues.second_order_model" class="ap-slot-label ap-second-order-label">
        归属
        <span class="ap-accept-tag accept-numeric">[一阶因子]</span>
        因子
        <span class="ap-slot-constraint">（因子数≥2）</span>
      </div>
      <div v-if="optionValues.second_order_model" class="ap-cfa-board ap-second-order-board">
        <div class="ap-cfa-sidebar ap-second-order-sidebar">
          <button type="button" class="ap-factor-btn ap-factor-btn--wide" @click="$emit('add-second-order-model')" :disabled="secondOrderModels.length >= maxSecondOrderModels">
            + 新建模型
          </button>
          <div class="ap-cfa-factor-list">
            <button
              v-for="model in secondOrderModels"
              :key="model.key"
              type="button"
              class="ap-cfa-factor-item"
              :class="{ 'is-active': activeSecondOrderKey === model.key }"
              @click="$emit('select-second-order-model', model.key)"
            >
              <span class="ap-cfa-factor-name">{{ model.label }}</span>
              <span class="ap-cfa-factor-badge">{{ model.members.length }}</span>
              <span class="ap-cfa-factor-menu-wrap">
                <button
                  type="button"
                  class="ap-cfa-factor-more"
                  @click.stop="$emit('delete-second-order-model', model.key)"
                  :disabled="secondOrderModels.length <= 1"
                >
                  ×
                </button>
              </span>
            </button>
          </div>
          <div class="ap-factor-tip">点击右侧一阶因子，将其加入或移出当前二阶模型。</div>
        </div>
        <div class="ap-cfa-main">
          <div class="ap-cfa-main-head">
            <label class="ap-cfa-title-edit">
              <input
                class="ap-cfa-title-input"
                :value="activeSecondOrderFactorName"
                @change="$emit('rename-second-order-factor', $event.target.value)"
              />
              <span class="ap-cfa-title-edit-btn" title="重命名">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M12 20h9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                </svg>
              </span>
            </label>
            <span class="ap-cfa-main-sub">{{ activeSecondOrderMembers.length }} 个一阶因子</span>
          </div>
          <div class="ap-second-order-drop-zone">
            <button
              v-for="factor in secondOrderFactorChoices"
              :key="factor.key"
              type="button"
              class="ap-second-order-factor-row"
              :class="{ 'is-included': activeSecondOrderMembers.includes(factor.key), 'is-disabled': factor.disabled }"
              :disabled="factor.disabled"
              @click="$emit('toggle-second-order-member', factor.key)"
            >
              <span class="ap-second-order-check">
                <svg v-if="activeSecondOrderMembers.includes(factor.key)" width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M3.5 8.2 6.7 11.2 12.6 4.8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="ap-var-row-name">{{ factor.label }}</span>
              <span v-if="factor.disabled" class="ap-second-order-owner">已归属：{{ factor.ownerLabel }}</span>
              <span class="ap-var-row-tag accept-numeric">{{ factor.count }} 个题项</span>
            </button>
            <div v-if="!firstOrderFactorChoices.length" class="ap-drop-empty">
              先在上方建立一阶因子
            </div>
          </div>
          <div v-if="activeSecondOrderMembers.length < 2" class="ap-second-order-warning">
            二阶因子至少需要选择 2 个一阶因子。
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="isNWayAnovaMethod">
      <div class="ap-nway-form">
        <div
          v-for="slot in nWaySlots"
          :key="slot.key"
          class="ap-nway-slot"
          :class="{
            'ap-nway-slot--factors': slot.key === 'factors',
            'ap-nway-slot--dependent': slot.key === 'dependent',
          }"
        >
          <div class="ap-slot-label">
            放入
            <span v-if="getAcceptLabel(slot)" class="ap-accept-tag" :class="'accept-' + slot.accept">
              [{{ getAcceptLabel(slot) }}]
            </span>
            {{ slot.label }}
            <span class="ap-slot-constraint">
              （{{ slotConstraintText(slot) }}）
            </span>
            <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
          </div>
          <AnalysisDropZone
            :drag-over-slot="dragOverSlot"
            :drag-preview-count="dragPreviewCount"
            :empty-text="nWaySlotEmptyText(slot)"
            :get-var-type="getVarType"
            :get-var-type-class="getVarTypeClass"
            :slot="slot"
            :slot-key="slot.key"
            :values="slotValues[slot.key] || []"
            zone-class="ap-nway-drop-zone"
            @drag-over="$emit('drag-over', $event)"
            @drag-leave="$emit('drag-leave')"
            @drop-slot="(...args) => $emit('drop-slot', ...args)"
            @remove-var="(...args) => $emit('remove-var', ...args)"
          />
        </div>
      </div>
    </template>

    <template v-else-if="isMediationConfig">
      <div class="ap-mediation-form" :class="{ 'ap-mediation-form--with-preview': isModeratedMediationMethod }">
        <div class="ap-mediation-main">
          <div
            v-for="slot in mediationSlots"
            :key="slot.key"
            class="ap-mediation-slot"
            :class="[`ap-mediation-slot--${slot.key}`, { 'ap-mediation-slot--single': slot.type === 'single' }]"
          >
            <div class="ap-slot-label">
              放入
              <span v-if="getAcceptLabel(slot)" class="ap-accept-tag" :class="'accept-' + slot.accept">
                [{{ getAcceptLabel(slot) }}]
              </span>
              {{ slot.label }}
              <span class="ap-slot-constraint">
                （{{ mediationSlotConstraintText(slot) }}）
              </span>
              <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
            </div>
            <AnalysisDropZone
              :drag-over-slot="dragOverSlot"
              :drag-preview-count="dragPreviewCount"
              :empty-text="mediationSlotEmptyText(slot)"
              :get-var-type="getVarType"
              :get-var-type-class="getVarTypeClass"
              :slot="slot"
              :slot-key="slot.key"
              :values="slotValues[slot.key] || []"
              :zone-class="`ap-mediation-drop-zone ap-mediation-drop-zone--${slot.key} ${slot.type === 'single' ? 'ap-mediation-drop-zone--single' : ''}`"
              @drag-over="$emit('drag-over', $event)"
              @drag-leave="$emit('drag-leave')"
              @drop-slot="(...args) => $emit('drop-slot', ...args)"
              @remove-var="(...args) => $emit('remove-var', ...args)"
            />
          </div>
          <div class="ap-mediation-options">
            <template v-if="isModeratedMediationMethod">
              <div class="ap-mediation-extra-options">
                <div v-for="option in moderatedMediationLeftOptions" :key="option.key" class="ap-mediation-option">
                  <label>
                    {{ option.label }}
                    <span v-if="option.hint" class="ap-option-help" :data-hint="option.hint">?</span>
                  </label>
                  <select :value="optionValues[option.key]" @change="$emit('option-change', option.key, $event.target.value)">
                    <option v-for="choice in optionChoices(option)" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
                  </select>
                </div>
              </div>
            </template>
            <template v-else>
              <div v-for="option in mediationFormOptions" :key="option.key" class="ap-mediation-option">
                <label v-if="option.type === 'checkbox'" class="ap-option-check">
                  <input
                    type="checkbox"
                    :checked="!!optionValues[option.key]"
                    @change="$emit('option-change', option.key, $event.target.checked)"
                  />
                  <span>{{ option.label }}</span>
                </label>
                <template v-else>
                  <label>
                    {{ option.label }}
                    <span v-if="option.hint" class="ap-option-help" :data-hint="option.hint">?</span>
                  </label>
                  <select :value="optionValues[option.key]" @change="$emit('option-change', option.key, $event.target.value)">
                    <option v-for="choice in optionChoices(option)" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
                  </select>
                </template>
              </div>
            </template>
          </div>
        </div>
        <aside v-if="isModeratedMediationMethod" class="ap-mediation-preview-panel">
          <div class="ap-mediation-preview" :class="{ 'is-empty': !hasModeratedMediationPath }">
              <div class="ap-mediation-preview-head">
                <span>{{ hasModeratedMediationPath ? `PROCESS ${moderatedMediationModelText}` : '未选择模型' }}</span>
                <span :class="{ 'is-warning': !hasModeratedMediationPath }">{{ moderatedMediationPreviewDescription }}</span>
              </div>
              <div class="ap-mediation-path-row ap-mediation-path-row--preview">
                <div v-for="option in moderatedMediationPathOptions" :key="option.key" class="ap-mediation-option">
                  <label class="ap-option-check">
                    <input
                      type="checkbox"
                      :checked="!!optionValues[option.key]"
                      @change="$emit('option-change', option.key, $event.target.checked)"
                    />
                    <span>{{ option.label }}</span>
                  </label>
                </div>
              </div>
              <svg class="ap-mediation-preview-svg" viewBox="0 0 500 190" role="img" aria-label="调节中介模型预览图">
                <defs>
                  <marker id="moderatedPreviewArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563"/>
                  </marker>
                  <marker id="moderatedPreviewArrowActive" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e88ff"/>
                  </marker>
                </defs>
                <rect x="18" y="16" width="464" height="158" fill="#fff" stroke="#d9dee8"/>
                <line x1="105" y1="126" x2="216" y2="82" stroke="#4b5563" stroke-width="1.5" marker-end="url(#moderatedPreviewArrow)"/>
                <line x1="280" y1="82" x2="390" y2="126" stroke="#4b5563" stroke-width="1.5" marker-end="url(#moderatedPreviewArrow)"/>
                <line x1="105" y1="138" x2="390" y2="138" stroke="#4b5563" stroke-width="1.5" marker-end="url(#moderatedPreviewArrow)"/>
                <line
                  v-if="optionValues.moderate_x_m"
                  :x1="moderatedMediationPreview.z.cx"
                  :y1="moderatedMediationPreview.z.cy"
                  x2="166"
                  y2="102"
                  stroke="#1e88ff"
                  stroke-width="2"
                  marker-end="url(#moderatedPreviewArrowActive)"
                />
                <line
                  v-if="optionValues.moderate_m_y"
                  :x1="moderatedMediationPreview.z.cx"
                  :y1="moderatedMediationPreview.z.cy"
                  x2="334"
                  y2="102"
                  stroke="#1e88ff"
                  stroke-width="2"
                  marker-end="url(#moderatedPreviewArrowActive)"
                />
                <line
                  v-if="optionValues.moderate_x_y"
                  :x1="moderatedMediationPreview.z.cx"
                  :y1="moderatedMediationPreview.z.cy"
                  x2="250"
                  y2="124"
                  stroke="#1e88ff"
                  stroke-width="2"
                  marker-end="url(#moderatedPreviewArrowActive)"
                />
                <g class="ap-mediation-preview-node">
                  <rect x="70" y="118" width="36" height="32"/>
                  <text x="88" y="139">X</text>
                  <rect x="220" y="60" width="60" height="38"/>
                  <text x="250" y="84">M</text>
                  <rect x="390" y="118" width="36" height="32"/>
                  <text x="408" y="139">Y</text>
                  <rect :x="moderatedMediationPreview.z.x" :y="moderatedMediationPreview.z.y" width="44" height="34"/>
                  <text :x="moderatedMediationPreview.z.cx" :y="moderatedMediationPreview.z.cy + 5">Z</text>
                </g>
              </svg>
              <div class="ap-mediation-preview-options">
                <div v-for="option in moderatedMediationPreviewOptions" :key="option.key" class="ap-mediation-option">
                  <label>
                    {{ option.label }}
                    <span v-if="option.hint" class="ap-option-help" :data-hint="option.hint">?</span>
                  </label>
                  <select :value="optionValues[option.key]" @change="$emit('option-change', option.key, $event.target.value)">
                    <option v-for="choice in optionChoices(option)" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
                  </select>
                </div>
              </div>
          </div>
        </aside>
      </div>
    </template>

    <template v-else-if="isGoodnessOfFitChiSquareMethod">
      <div class="ap-gof-card">
        <div v-if="displaySlots[0]" class="ap-slot-label">
          放入
          <span class="ap-accept-tag accept-categorical">[{{ getAcceptLabel(displaySlots[0]) }}]</span>
          {{ displaySlots[0].label }}
          <span class="ap-slot-constraint">（变量数=1）</span>
          <span v-if="slotValues[displaySlots[0].key]?.length" class="ap-slot-count">{{ slotValues[displaySlots[0].key].length }}</span>
        </div>
        <AnalysisDropZone
          v-if="displaySlots[0]"
          :drag-over-slot="dragOverSlot"
          :drag-preview-count="dragPreviewCount"
          :empty-text="displaySlots[0].hint || '拖入变量到此区域'"
          :get-var-type="getVarType"
          :get-var-type-class="getVarTypeClass"
          :slot="displaySlots[0]"
          :slot-key="displaySlots[0].key"
          :values="slotValues[displaySlots[0].key] || []"
          zone-class="ap-gof-drop-zone"
          @drag-over="$emit('drag-over', $event)"
          @drag-leave="$emit('drag-leave')"
          @drop-slot="(...args) => $emit('drop-slot', ...args)"
          @remove-var="(...args) => $emit('remove-var', ...args)"
        />

        <div v-if="slotValues.variable?.length" class="ap-gof-ratio-grid">
          <div class="ap-gof-ratio-head">分组</div>
          <div class="ap-gof-ratio-head">期望比例(%)</div>
          <template v-if="goodnessOfFitLoading">
            <div class="ap-gof-loading">正在读取分组...</div>
          </template>
          <template v-else>
            <template v-for="label in goodnessOfFitCategories" :key="label">
              <input class="ap-gof-group-input" :value="label" disabled />
              <div class="ap-gof-ratio-row">
                <span>表示</span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  :value="goodnessOfFitRatioValue(label)"
                  @input="$emit('set-goodness-of-fit-ratio', label, $event.target.value)"
                />
              </div>
            </template>
          </template>
        </div>
      </div>
    </template>

    <div
      v-else
      v-for="(slot, slotIndex) in displaySlots"
      :key="slot.key"
      class="ap-slot"
      :class="{
        'ap-slot-grow': !usesEqualSlotHeights && slotIndex === displaySlots.length - 1,
        'ap-slot-equal': usesEqualSlotHeights,
      }"
    >
      <div class="ap-slot-label">
        放入
        <span v-if="slot.prefixLabel">{{ slot.prefixLabel }}</span>
        <span v-if="getAcceptLabel(slot)" class="ap-accept-tag" :class="'accept-' + slot.accept">
          [{{ getAcceptLabel(slot) }}]
        </span>
        {{ slot.label }}
        <span class="ap-slot-constraint">
          （{{ slotConstraintText(slot) }}）
        </span>
        <span v-if="slotValues[slot.key]?.length" class="ap-slot-count">{{ slotValues[slot.key].length }}</span>
      </div>
      <AnalysisDropZone
        :drag-over-slot="dragOverSlot"
        :drag-preview-count="dragPreviewCount"
        :empty-text="slot.hint || `将待分析变量拖入到此区域${slot.type === 'single' ? '（单个变量）' : ''}`"
        :get-var-type="getVarType"
        :get-var-type-class="getVarTypeClass"
        :slot="slot"
        :slot-key="slot.key"
        :values="slotValues[slot.key] || []"
        @drag-over="$emit('drag-over', $event)"
        @drag-leave="$emit('drag-leave')"
        @drop-slot="(...args) => $emit('drop-slot', ...args)"
        @remove-var="(...args) => $emit('remove-var', ...args)"
      />
    </div>

    <div class="ap-actions">
      <button class="ap-btn ap-btn-ghost" @click="$emit('reset')">重置</button>
      <button class="ap-btn ap-btn-primary" :disabled="!canExecute || executing" @click="$emit('execute')">
        <svg v-if="!executing" width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M4 2l10 6-10 6V2z" fill="currentColor"/></svg>
        <span v-if="executing" class="spinner-sm"></span>
        {{ executing ? '分析中...' : '开始分析' }}
      </button>
      <div v-if="actionOptions.length" class="ap-options ap-options--actions">
        <div v-for="option in actionOptions" :key="option.key" class="ap-option-group">
          <label v-if="option.type === 'checkbox'" class="ap-option-check">
            <input
              type="checkbox"
              :checked="!!optionValues[option.key]"
              @change="$emit('option-change', option.key, $event.target.checked)"
            />
            <span>{{ option.label }}</span>
          </label>
          <template v-else-if="option.type === 'multiple'">
            <label>{{ option.label }}：</label>
            <details class="ap-option-multi">
              <summary>{{ multiOptionText(option) }}</summary>
              <div class="ap-option-multi-menu">
                <label
                  v-for="choice in option.choices"
                  :key="choice"
                  class="ap-option-multi-item"
                >
                  <input
                    type="checkbox"
                    :checked="multiOptionValues(option.key).includes(choice)"
                    @change="toggleMultiOption(option, choice)"
                  />
                  <span>{{ choice }}</span>
                </label>
              </div>
            </details>
          </template>
          <template v-else>
            <label>
              {{ option.label }}：
              <span v-if="option.hint" class="ap-option-help" :data-hint="option.hint">?</span>
            </label>
            <input
              v-if="option.type === 'number'"
              type="number"
              step="any"
              :value="optionValues[option.key]"
              @input="$emit('option-change', option.key, $event.target.value)"
            />
            <select v-else :value="optionValues[option.key]" @change="$emit('option-change', option.key, $event.target.value)">
              <option v-for="choice in optionChoices(option)" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
            </select>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AnalysisDropZone from './AnalysisDropZone.vue'

const configRoot = ref(null)
const titleInputRef = ref(null)

const props = defineProps({
  activeSecondOrderFactorName: { type: String, default: '二阶模型1' },
  activeSecondOrderKey: { type: String, default: 'second_order_1' },
  activeSecondOrderMembers: { type: Array, default: () => [] },
  activeFactorItems: { type: Array, default: () => [] },
  activeFactorKey: { type: String, default: '' },
  activeFactorSlot: { type: Object, default: null },
  activeFactorTitle: { type: String, default: '' },
  canExecute: { type: Boolean, default: false },
  displaySlots: { type: Array, default: () => [] },
  dragPreviewCount: { type: Number, default: 0 },
  dragOverSlot: { type: String, default: null },
  dynamicFactorCount: { type: Number, default: 1 },
  dynamicGroupAddText: { type: String, default: '+ 新建因子' },
  dynamicGroupItemName: { type: String, default: '题项' },
  dynamicGroupTip: { type: String, default: '' },
  editingConfig: { type: Boolean, default: false },
  executing: { type: Boolean, default: false },
  factorMenuKey: { type: String, default: null },
  firstOrderFactorChoices: { type: Array, default: () => [] },
  getFactorShortLabel: { type: Function, required: true },
  getVarType: { type: Function, required: true },
  getVarTypeClass: { type: Function, required: true },
  goodnessOfFitCategories: { type: Array, default: () => [] },
  goodnessOfFitLoading: { type: Boolean, default: false },
  isCfaMethod: { type: Boolean, default: false },
  isGoodnessOfFitChiSquareMethod: { type: Boolean, default: false },
  isIndependentTMethod: { type: Boolean, default: false },
  isModeratedMediationMethod: { type: Boolean, default: false },
  isOneSampleEquivalenceMethod: { type: Boolean, default: false },
  isOneWayAnovaMethod: { type: Boolean, default: false },
  isPairedEquivalenceMethod: { type: Boolean, default: false },
  isSummaryOneWayAnovaMethod: { type: Boolean, default: false },
  isSummaryTMethod: { type: Boolean, default: false },
  isTwoSampleEquivalenceMethod: { type: Boolean, default: false },
  maxDynamicFactors: { type: Number, default: 12 },
  maxSecondOrderModels: { type: Number, default: 8 },
  method: { type: Object, required: true },
  optionValues: { type: Object, required: true },
  renameFocusToken: { type: Object, default: () => ({ key: '', nonce: 0 }) },
  results: { type: Array, default: () => [] },
  secondOrderModels: { type: Array, default: () => [] },
  secondOrderFactorChoices: { type: Array, default: () => [] },
  slotValues: { type: Object, required: true },
  variables: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'add-second-order-model',
  'add-factor',
  'add-summary-one-way-group',
  'close-factor-menu',
  'delete-factor',
  'delete-second-order-model',
  'drag-leave',
  'drag-over',
  'drop-slot',
  'execute',
  'option-change',
  'remove-var',
  'remove-summary-one-way-group',
  'rename-second-order-factor',
  'rename-factor',
  'rename-factor-inline',
  'reset',
  'select-factor',
  'select-second-order-model',
  'set-goodness-of-fit-ratio',
  'show-report',
  'toggle-factor-menu',
  'toggle-second-order-member',
  'update-summary-one-way-group',
])

const equalSlotMethodLabels = new Set([
  'Kano模型',
  '多选-多选（交叉分析）',
  '多选-单选（对比分析）',
  '单选-多选（对比分析）',
  '多变量方差分析',
  '配对样本Wilcoxon符号秩检验',
])
const usesEqualSlotHeights = computed(() => equalSlotMethodLabels.has(props.method?.label))
const isNWayAnovaMethod = computed(() => props.method?.label === '多因素方差分析')
const isMediationConfig = computed(() => (
  props.method?.label === '中介效应'
  || props.method?.label === '平行中介效应'
  || ['x', 'y', 'mediators'].every(key => props.displaySlots.some(slot => slot.key === key))
))
const summaryOneWayGroups = computed(() => (
  Array.isArray(props.optionValues.groups) ? props.optionValues.groups : []
))
function twoSampleSlot(key, fallback) {
  return props.displaySlots.find(slot => slot.key === key) || fallback
}
function oneWaySlot(key, fallback) {
  return { ...(props.displaySlots.find(slot => slot.key === key) || {}), ...fallback }
}
const twoSampleSameColumnSlots = computed(() => [
  twoSampleSlot('test_var', { key: 'test_var', label: '检验样本', type: 'single', accept: 'numeric', hint: '拖入变量到此区域' }),
  twoSampleSlot('group_var', { key: 'group_var', label: '二分类', type: 'single', accept: 'categorical', hint: '拖入变量到此区域' }),
])
const oneWaySameColumnSlots = computed(() => [
  oneWaySlot('group_var', { key: 'group_var', label: '变量X', type: 'single', accept: 'categorical', hint: '拖拽变量到此区域' }),
  oneWaySlot('test_vars', { key: 'test_vars', label: '变量Y', type: 'multiple', accept: 'numeric', min: 1, hint: '拖拽变量到此区域' }),
])
const independentSameColumnSlots = computed(() => [
  oneWaySlot('group_var', { key: 'group_var', label: '变量X', type: 'single', accept: 'categorical', hint: '拖入二分类变量到此区域' }),
  oneWaySlot('test_vars', { key: 'test_vars', label: '变量Y', type: 'multiple', accept: 'numeric', min: 1, hint: '拖入定量变量到此区域' }),
])
const independentDifferentColumnSlot = computed(() => (
  oneWaySlot('test_vars', { key: 'test_vars', label: '变量Y', type: 'multiple', accept: 'numeric', min: 2, max: 2, hint: '拖入两个样本列到此区域' })
))
const oneWayDifferentColumnSlots = computed(() => [
  twoSampleSlot('group_columns', { key: 'group_columns', label: '变量Y', type: 'multiple', accept: 'numeric', min: 3, hint: '拖拽变量到此区域' }),
])
const twoSampleDifferentColumnSlots = computed(() => [
  twoSampleSlot('test_var', { key: 'test_var', label: '检验样本', type: 'single', accept: 'numeric', hint: '拖入变量到此区域' }),
  twoSampleSlot('reference_var', { key: 'reference_var', label: '参考样本', type: 'single', accept: 'numeric', hint: '拖入变量到此区域' }),
])
const pairedEquivalenceSlots = computed(() => [
  twoSampleSlot('test_var', { key: 'test_var', label: '检验变量', type: 'single', accept: 'numeric', hint: '拖入变量到此区域' }),
  twoSampleSlot('reference_var', { key: 'reference_var', label: '参考变量', type: 'single', accept: 'numeric', hint: '拖入变量到此区域' }),
])
const nWaySlots = computed(() => {
  if (!isNWayAnovaMethod.value) return []
  const order = ['dependent', 'factors']
  return order
    .map(key => props.displaySlots.find(slot => slot.key === key))
    .filter(Boolean)
})
const mediationSlots = computed(() => {
  const fallbackMap = {
    y: { key: 'y', label: '变量Y', type: 'single', accept: 'numeric', hint: '拖入因变量Y' },
    x: { key: 'x', label: '变量X', type: 'multiple', accept: 'numeric', min: 1, hint: '拖入变量X' },
    mediators: { key: 'mediators', label: '中介变量M', type: 'multiple', accept: 'numeric', min: 1, hint: '拖入中介变量M' },
    z: { key: 'z', label: '调节变量Z', type: 'single', accept: 'numeric', hint: '拖入调节变量Z' },
    controls: { key: 'controls', label: '控制变量', type: 'multiple', accept: 'numeric', min: 0, hint: '拖入控制变量' },
  }
  const slotOrder = props.isModeratedMediationMethod ? ['y', 'x', 'mediators', 'z', 'controls'] : ['y', 'x', 'mediators', 'controls']
  return slotOrder.map(key => ({
    ...fallbackMap[key],
    ...(props.displaySlots.find(slot => slot.key === key) || {}),
  }))
})
const hasModeratedMediationPath = computed(() => (
  Boolean(props.optionValues.moderate_x_m || props.optionValues.moderate_m_y || props.optionValues.moderate_x_y)
))
const moderatedMediationPathKeys = new Set(['moderate_x_m', 'moderate_m_y', 'moderate_x_y'])
const moderatedMediationPathOptions = computed(() => (
  visibleOptions.value.filter(option => moderatedMediationPathKeys.has(option.key))
))
const moderatedMediationPreviewOptionKeys = new Set(['moderator_levels', 'bootstrap_reps', 'bootstrap_method'])
const moderatedMediationPreviewOptions = computed(() => (
  visibleOptions.value.filter(option => moderatedMediationPreviewOptionKeys.has(option.key))
))
function isActionOption(option) {
  return option?.key === 'include_missing_analysis'
}
const mediationFormOptions = computed(() => (
  visibleOptions.value.filter(option => !isActionOption(option))
))
const moderatedMediationLeftOptions = computed(() => (
  mediationFormOptions.value.filter(option => (
    !moderatedMediationPathKeys.has(option.key)
    && !moderatedMediationPreviewOptionKeys.has(option.key)
  ))
))
const moderatedMediationModelText = computed(() => {
  const xM = Boolean(props.optionValues.moderate_x_m)
  const mY = Boolean(props.optionValues.moderate_m_y)
  const xY = Boolean(props.optionValues.moderate_x_y)
  if (!xM && !mY && xY) return 'Model 5'
  if (xM && !mY && !xY) return 'Model 7'
  if (xM && !mY && xY) return 'Model 8'
  if (!xM && mY && !xY) return 'Model 14'
  if (!xM && mY && xY) return 'Model 15'
  if (xM && mY && !xY) return 'Model 58'
  if (xM && mY && xY) return 'Model 59'
  return '未选择模型'
})
const moderatedMediationPreviewDescription = computed(() => {
  const paths = []
  if (props.optionValues.moderate_x_m) paths.push('X→M')
  if (props.optionValues.moderate_m_y) paths.push('M→Y')
  if (props.optionValues.moderate_x_y) paths.push('X→Y')
  return paths.length ? `Z 调节 ${paths.join('、')}` : '请选择至少一条 Z 调节路径'
})
const moderatedMediationPreview = computed(() => {
  const xM = Boolean(props.optionValues.moderate_x_m)
  const mY = Boolean(props.optionValues.moderate_m_y)
  let z = { x: 70, y: 44 }
  if (mY && !xM) z = { x: 338, y: 46 }
  if (mY && xM) z = { x: 228, y: 136 }
  return {
    z: {
      ...z,
      cx: z.x + 22,
      cy: z.y + 17,
    },
  }
})
const visibleOptions = computed(() => (props.method?.options || []).filter(option => {
  if (['second_order_interaction', 'third_order_interaction'].includes(option.key)) {
    return Boolean(props.optionValues.include_interaction)
  }
  if (option.key === 'post_hoc_method') return Boolean(props.optionValues.do_post_hoc)
  return true
}))
const actionOptions = computed(() => {
  if (isMediationConfig.value) {
    return visibleOptions.value.filter(isActionOption)
  }
  if (
    props.method?.options?.length
    && !props.isSummaryTMethod
    && !props.isSummaryOneWayAnovaMethod
    && !props.isIndependentTMethod
    && !props.isOneWayAnovaMethod
    && !props.isOneSampleEquivalenceMethod
    && !props.isTwoSampleEquivalenceMethod
    && !props.isPairedEquivalenceMethod
  ) {
    return visibleOptions.value
  }
  return []
})

function getAcceptLabel(slot) {
  if (slot.acceptLabel) return slot.acceptLabel
  if (!slot.accept || slot.accept === 'any') return ''
  if (slot.accept === 'numeric') return '定量'
  if (slot.accept === 'categorical') return '定类'
  return slot.accept
}

function goodnessOfFitRatioValue(label) {
  const values = props.optionValues.expected_ratios || {}
  return values[String(label)] ?? ''
}

function slotConstraintText(slot) {
  if (slot.type === 'single') return '单个变量'
  const min = Number(slot.min ?? 1)
  const max = Number(slot.max)
  if (Number.isFinite(max) && max === min) return `变量数=${max}`
  if (Number.isFinite(max)) return `变量数${min}-${max}`
  return `变量数≥${min}`
}

function mediationSlotConstraintText(slot) {
  if (slot.key === 'controls') return '非必填，变量数≥0'
  if (slot.key === 'y' || slot.key === 'z') return '变量数=1'
  return slotConstraintText(slot)
}

function mediationSlotEmptyText(slot) {
  if (slot.key === 'y') return '拖入因变量Y'
  if (slot.key === 'x') return '拖入变量X'
  if (slot.key === 'mediators') return '拖入中介变量M'
  if (slot.key === 'z') return '拖入调节变量Z'
  if (slot.key === 'controls') return '拖入控制变量'
  return slot.hint || '拖拽变量到此区域'
}

function nWaySlotEmptyText(slot) {
  if (slot.key === 'factors') return '放入2个及以上分组因素'
  if (slot.key === 'dependent') return '放入因变量'
  return slot.hint || '将待分析变量拖入到此区域'
}

function multiOptionValues(key) {
  const value = props.optionValues[key]
  return Array.isArray(value) ? value : [value].filter(Boolean)
}

function multiOptionText(option) {
  const values = multiOptionValues(option.key)
  return values.length ? values.join('、') : '请选择'
}

function optionChoices(option) {
  if (option.type !== 'factor_count') {
    return (option.choices || []).map(choice => {
      const value = typeof choice === 'object' ? choice.value : choice
      const label = typeof choice === 'object'
        ? (choice.label || choice.value)
        : (option.choice_labels?.[choice] || choice)
      return { value, label }
    })
  }
  const selectedCount = Array.isArray(props.slotValues.variables) ? props.slotValues.variables.length : 0
  const numericCount = props.variables.filter(variable => variable?.type === 'numeric').length
  const max = Math.max(selectedCount, numericCount)
  const choices = [{ value: 'auto', label: '自动抽取' }]
  for (let index = 1; index <= max; index += 1) {
    choices.push({ value: String(index), label: String(index) })
  }
  return choices
}

function toggleMultiOption(option, choice) {
  const values = multiOptionValues(option.key)
  const next = values.includes(choice)
    ? values.filter(item => item !== choice)
    : [...values, choice]
  emit('option-change', option.key, next.length ? next : [option.choices[0]])
}

function closeMultiOptions() {
  configRoot.value
    ?.querySelectorAll('.ap-option-multi[open]')
    .forEach(el => {
      el.open = false
    })
}

function handleDocumentPointerDown(event) {
  if (event.target?.closest?.('.ap-option-multi')) return
  closeMultiOptions()
}

watch(
  () => props.renameFocusToken,
  async token => {
    if (!token?.key || token.key !== props.activeFactorKey) return
    await nextTick()
    titleInputRef.value?.focus?.()
    titleInputRef.value?.select?.()
  },
  { deep: true },
)

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
})
</script>
