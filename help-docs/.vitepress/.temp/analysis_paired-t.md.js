import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"配对样本T检验","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/paired-t.md","filePath":"analysis/paired-t.md"}');
const _sfc_main = { name: "analysis/paired-t.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="配对样本t检验" tabindex="-1">配对样本T检验 <a class="header-anchor" href="#配对样本t检验" aria-label="Permalink to &quot;配对样本T检验&quot;">​</a></h1><p>analysis-paired-t</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个一一对应的定量变量，例如前测与后测、干预前与干预后、A 条件与 B 条件。</li><li>输出：配对描述统计、均值差、t 检验结果和效应量。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/paired-t.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const pairedT = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  pairedT as default
};
