import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"相关性分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/analysis-pearson.md","filePath":"analysis/analysis-pearson.md"}');
const _sfc_main = { name: "analysis/analysis-pearson.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="相关性分析" tabindex="-1">相关性分析 <a class="header-anchor" href="#相关性分析" aria-label="Permalink to &quot;相关性分析&quot;">​</a></h1></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/analysis-pearson.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const analysisPearson = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  analysisPearson as default
};
