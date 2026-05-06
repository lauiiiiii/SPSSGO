import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"单因素方差分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/anova.md","filePath":"analysis/anova.md"}');
const _sfc_main = { name: "analysis/anova.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="单因素方差分析" tabindex="-1">单因素方差分析 <a class="header-anchor" href="#单因素方差分析" aria-label="Permalink to &quot;单因素方差分析&quot;">​</a></h1><p>analysis-anova</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个分组变量（3 组及以上），以及 1 个或多个定量检验变量。</li><li>输出：分组描述统计、方差分析表、F 检验结果和事后比较结果。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/anova.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const anova = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  anova as default
};
