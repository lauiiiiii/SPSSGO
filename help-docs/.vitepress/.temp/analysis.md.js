import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis.md","filePath":"analysis.md"}');
const _sfc_main = { name: "analysis.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据分析" tabindex="-1">数据分析 <a class="header-anchor" href="#数据分析" aria-label="Permalink to &quot;数据分析&quot;">​</a></h1><h2 id="如何开始一次分析" tabindex="-1">如何开始一次分析？ <a class="header-anchor" href="#如何开始一次分析" aria-label="Permalink to &quot;如何开始一次分析？&quot;">​</a></h2><ol><li><strong>选定分析目标</strong>：先确认你是想描述现状、比较差异、研究关系，还是做预测，这会决定方法方向。</li><li><strong>拖入正确变量</strong>：根据页面要求把目标变量、自变量或分组变量放入对应区域，避免变量角色放错。</li><li><strong>设置必要参数</strong>：如显著性水平、分组方式、检验方向等，建议理解含义后再修改默认值。</li><li><strong>查看并解释结果</strong>：不要只盯着显著性结果，还要结合样本背景、效应方向和实际意义一起判断。</li></ol><h2 id="怎么看分析结果" tabindex="-1">怎么看分析结果？ <a class="header-anchor" href="#怎么看分析结果" aria-label="Permalink to &quot;怎么看分析结果？&quot;">​</a></h2><h3 id="先看问题是否匹配" tabindex="-1">先看问题是否匹配 <a class="header-anchor" href="#先看问题是否匹配" aria-label="Permalink to &quot;先看问题是否匹配&quot;">​</a></h3><p>结果是否回答了你一开始想解决的问题，比单纯&quot;有没有显著&quot;更重要。</p><h3 id="再看关键统计量" tabindex="-1">再看关键统计量 <a class="header-anchor" href="#再看关键统计量" aria-label="Permalink to &quot;再看关键统计量&quot;">​</a></h3><p>均值、标准差、p 值、相关系数、回归系数等要结合具体方法来读，不能混用。</p><h3 id="最后写成解释语言" tabindex="-1">最后写成解释语言 <a class="header-anchor" href="#最后写成解释语言" aria-label="Permalink to &quot;最后写成解释语言&quot;">​</a></h3><p>尽量把统计结果翻译成业务语言、研究语言或论文表达，避免只复制表格而没有结论。</p><h2 id="常见误区" tabindex="-1">常见误区 <a class="header-anchor" href="#常见误区" aria-label="Permalink to &quot;常见误区&quot;">​</a></h2><p><strong>p 值显著就说明研究结论一定成立吗？</strong> 不是。显著性只是统计意义的一部分，还要看研究设计、样本质量、效应大小和实际背景。</p><p><strong>变量越多越好吗？</strong> 不一定。变量过多可能带来噪声、共线性和解释困难，很多时候合适比堆砌更重要。</p><p><strong>AI 解释能直接复制进论文吗？</strong> 建议作为草稿参考，再结合你的研究背景进行人工核对、修改和定稿。</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const analysis = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  analysis as default
};
