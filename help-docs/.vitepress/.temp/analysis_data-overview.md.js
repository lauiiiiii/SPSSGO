import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据概览","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/data-overview.md","filePath":"analysis/data-overview.md"}');
const _sfc_main = { name: "analysis/data-overview.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据概览" tabindex="-1">数据概览 <a class="header-anchor" href="#数据概览" aria-label="Permalink to &quot;数据概览&quot;">​</a></h1><p>analysis-data-overview</p><h2 id="作用与适用场景" tabindex="-1">作用与适用场景 <a class="header-anchor" href="#作用与适用场景" aria-label="Permalink to &quot;作用与适用场景&quot;">​</a></h2><p>当你刚上传一份数据，或者接手别人整理过的数据时，优先用数据概览确认字段是否完整、类型是否合理、缺失是否明显。</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：一个或多个需要查看的数据变量。</li><li>输出：变量概况、样本量、类型分布和缺失比例，用于决定后续分析或数据处理路径。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/data-overview.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const dataOverview = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  dataOverview as default
};
