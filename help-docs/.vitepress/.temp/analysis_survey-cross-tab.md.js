import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"交叉表（调研专项）","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/survey-cross-tab.md","filePath":"analysis/survey-cross-tab.md"}');
const _sfc_main = { name: "analysis/survey-cross-tab.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="交叉表-调研专项" tabindex="-1">交叉表（调研专项） <a class="header-anchor" href="#交叉表-调研专项" aria-label="Permalink to &quot;交叉表（调研专项）&quot;">​</a></h1><p>analysis-survey-cross-tab</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个调研类分类变量，例如人群属性题和态度题、偏好题。</li><li>输出：交叉频数、行百分比、列百分比以及卡方检验结果。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/survey-cross-tab.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const surveyCrossTab = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  surveyCrossTab as default
};
