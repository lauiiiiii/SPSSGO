import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"样本加权","description":"","frontmatter":{},"headers":[],"relativePath":"processing/weight.md","filePath":"processing/weight.md"}');
const _sfc_main = { name: "processing/weight.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="样本加权" tabindex="-1">样本加权 <a class="header-anchor" href="#样本加权" aria-label="Permalink to &quot;样本加权&quot;">​</a></h1><p>processing-weight</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：选择待分析变量，并指定一个权重变量作为加权依据。</li><li>输出：后续统计中，不同样本会按权重值产生不同影响。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/weight.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const weight = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  weight as default
};
