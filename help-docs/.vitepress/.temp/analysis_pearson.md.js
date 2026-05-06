import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"相关性分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/pearson.md","filePath":"analysis/pearson.md"}');
const _sfc_main = { name: "analysis/pearson.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="相关性分析" tabindex="-1">相关性分析 <a class="header-anchor" href="#相关性分析" aria-label="Permalink to &quot;相关性分析&quot;">​</a></h1><p>analysis-pearson</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个或以上定量变量。</li><li>输出：相关系数矩阵、显著性水平，以及各变量之间关系方向与强弱的解释。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/pearson.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const pearson = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  pearson as default
};
