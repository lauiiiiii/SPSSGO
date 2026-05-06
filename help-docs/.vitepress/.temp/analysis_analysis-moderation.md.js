import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"调节作用","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/analysis-moderation.md","filePath":"analysis/analysis-moderation.md"}');
const _sfc_main = { name: "analysis/analysis-moderation.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="调节作用" tabindex="-1">调节作用 <a class="header-anchor" href="#调节作用" aria-label="Permalink to &quot;调节作用&quot;">​</a></h1></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/analysis-moderation.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const analysisModeration = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  analysisModeration as default
};
