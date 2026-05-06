import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"Spearman 等级相关","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/spearman.md","filePath":"analysis/spearman.md"}');
const _sfc_main = { name: "analysis/spearman.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="spearman-等级相关" tabindex="-1">Spearman 等级相关 <a class="header-anchor" href="#spearman-等级相关" aria-label="Permalink to &quot;Spearman 等级相关&quot;">​</a></h1><p>analysis-spearman</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个或以上变量，常用于等级变量或明显非正态的定量变量。</li><li>输出：Spearman 相关系数矩阵及显著性水平。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/spearman.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const spearman = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  spearman as default
};
