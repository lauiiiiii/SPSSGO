import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据降维","description":"","frontmatter":{},"headers":[],"relativePath":"processing/reduce.md","filePath":"processing/reduce.md"}');
const _sfc_main = { name: "processing/reduce.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据降维" tabindex="-1">数据降维 <a class="header-anchor" href="#数据降维" aria-label="Permalink to &quot;数据降维&quot;">​</a></h1><p>processing-reduce</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：至少 2 个无空值定量变量，必要时再指定目标变量或维度数。</li><li>输出：系统生成更少维度的新变量，用于可视化、建模或降低复杂度。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/reduce.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const reduce = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  reduce as default
};
