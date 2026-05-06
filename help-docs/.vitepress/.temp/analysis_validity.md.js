import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"效度分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/validity.md","filePath":"analysis/validity.md"}');
const _sfc_main = { name: "analysis/validity.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="效度分析" tabindex="-1">效度分析 <a class="header-anchor" href="#效度分析" aria-label="Permalink to &quot;效度分析&quot;">​</a></h1><p>analysis-validity</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：同一量表或同一维度下的多个题项变量，通常至少 3 个。</li><li>输出：KMO 值、Bartlett 检验结果，以及对是否适合做因子分析的判断。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/validity.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const validity = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  validity as default
};
