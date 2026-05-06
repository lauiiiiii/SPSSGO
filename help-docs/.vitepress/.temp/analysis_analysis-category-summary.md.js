import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"分类汇总","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/analysis-category-summary.md","filePath":"analysis/analysis-category-summary.md"}');
const _sfc_main = { name: "analysis/analysis-category-summary.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="分类汇总" tabindex="-1">分类汇总 <a class="header-anchor" href="#分类汇总" aria-label="Permalink to &quot;分类汇总&quot;">​</a></h1></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/analysis-category-summary.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const analysisCategorySummary = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  analysisCategorySummary as default
};
