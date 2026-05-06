import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"频数分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/frequency.md","filePath":"analysis/frequency.md"}');
const _sfc_main = { name: "analysis/frequency.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="频数分析" tabindex="-1">频数分析 <a class="header-anchor" href="#频数分析" aria-label="Permalink to &quot;频数分析&quot;">​</a></h1><p>analysis-frequency</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个需要统计频次的变量，可为定类变量，也可为离散型定量变量。</li><li>输出：每个类别的频数、百分比和累计百分比，帮助你快速把握分布结构。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/frequency.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const frequency = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  frequency as default
};
