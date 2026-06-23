import { _ as _export_sfc, o as openBlock, c as createElementBlock, ag as createStaticVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing.md","filePath":"processing.md"}');
const _sfc_main = { name: "processing.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createStaticVNode('<h1 id="数据处理" tabindex="-1">数据处理 <a class="header-anchor" href="#数据处理" aria-label="Permalink to &quot;数据处理&quot;">​</a></h1><h2 id="为什么先做数据处理" tabindex="-1">为什么先做数据处理？ <a class="header-anchor" href="#为什么先做数据处理" aria-label="Permalink to &quot;为什么先做数据处理？&quot;">​</a></h2><p>高质量分析的前提是高质量数据。缺失值、异常值、重复样本、编码混乱等问题，如果不先处理，后续统计结果会很容易失真。</p><p>SPSSGO 把数据处理独立成单独模块，方便你按步骤完成清洗，再进入正式分析。</p><h2 id="推荐处理顺序" tabindex="-1">推荐处理顺序 <a class="header-anchor" href="#推荐处理顺序" aria-label="Permalink to &quot;推荐处理顺序&quot;">​</a></h2><ol><li><strong>先检查缺失值</strong>：先确认哪些变量存在空值、空值比例如何，再决定删除、填补还是标记。</li><li><strong>再处理异常值</strong>：对定量变量优先识别极端值，避免少量异常点过度影响均值、标准差和回归结果。</li><li><strong>最后做转换与编码</strong>：如有需要，再进行标准化、重编码、虚拟变量转换、降维等操作，让数据更适合建模和分析。</li></ol><h2 id="使用提醒" tabindex="-1">使用提醒 <a class="header-anchor" href="#使用提醒" aria-label="Permalink to &quot;使用提醒&quot;">​</a></h2><ul><li><strong>看清方法适用变量</strong>：有些方法只支持定量变量，有些只支持定类变量，执行前先留意页面中的变量限制提示。</li><li><strong>一次只改清楚一件事</strong>：如果连续进行多步处理，建议每一步都明确目的，避免在不知不觉中改变数据含义。</li><li><strong>重视结果解释</strong>：数据处理不是机械操作，每一种处理都会影响后续分析含义，尤其在论文与正式报告中要说明理由。</li></ul>', 8)
  ])]);
}
const processing = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  processing as default
};
