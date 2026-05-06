import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"独立样本T检验","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/independent-t.md","filePath":"analysis/independent-t.md"}');
const _sfc_main = { name: "analysis/independent-t.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="独立样本t检验" tabindex="-1">独立样本T检验 <a class="header-anchor" href="#独立样本t检验" aria-label="Permalink to &quot;独立样本T检验&quot;">​</a></h1><p>analysis-independent-t</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个二分类分组变量，以及 1 个或多个需要比较的定量检验变量。</li><li>输出：分组描述统计、方差齐性检验、t 检验结果和效应量。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/independent-t.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const independentT = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  independentT as default
};
