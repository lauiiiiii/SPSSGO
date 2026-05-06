import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"描述性统计","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/descriptive.md","filePath":"analysis/descriptive.md"}');
const _sfc_main = { name: "analysis/descriptive.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="描述性统计" tabindex="-1">描述性统计 <a class="header-anchor" href="#描述性统计" aria-label="Permalink to &quot;描述性统计&quot;">​</a></h1><p>analysis-descriptive</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个或多个定量变量。</li><li>输出：均值、标准差、最小值、最大值等描述指标，帮助你理解变量的大致水平和波动范围。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/descriptive.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const descriptive = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  descriptive as default
};
