import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"卡方检验","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/chi-square.md","filePath":"analysis/chi-square.md"}');
const _sfc_main = { name: "analysis/chi-square.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="卡方检验" tabindex="-1">卡方检验 <a class="header-anchor" href="#卡方检验" aria-label="Permalink to &quot;卡方检验&quot;">​</a></h1><p>analysis-chi-square</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个分类变量。</li><li>输出：交叉频数、卡方值、自由度、显著性和关联强度指标。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/chi-square.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const chiSquare = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  chiSquare as default
};
