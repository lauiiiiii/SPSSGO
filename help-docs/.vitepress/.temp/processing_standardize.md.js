import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据标准化","description":"","frontmatter":{},"headers":[],"relativePath":"processing/standardize.md","filePath":"processing/standardize.md"}');
const _sfc_main = { name: "processing/standardize.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据标准化" tabindex="-1">数据标准化 <a class="header-anchor" href="#数据标准化" aria-label="Permalink to &quot;数据标准化&quot;">​</a></h1><p>processing-standardize</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个或多个无空值定量变量，并选择标准化方法。</li><li>输出：原始变量会被转换到统一尺度，便于综合评价、聚类、回归或机器学习建模。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/standardize.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const standardize = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  standardize as default
};
