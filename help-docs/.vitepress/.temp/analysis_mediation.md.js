import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"中介效应分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/mediation.md","filePath":"analysis/mediation.md"}');
const _sfc_main = { name: "analysis/mediation.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="中介效应分析" tabindex="-1">中介效应分析 <a class="header-anchor" href="#中介效应分析" aria-label="Permalink to &quot;中介效应分析&quot;">​</a></h1><p>analysis-mediation</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个自变量 X、1 个中介变量 M、1 个因变量 Y。</li><li>输出：路径回归结果、直接效应、间接效应和总效应的解释。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/mediation.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const mediation = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  mediation as default
};
