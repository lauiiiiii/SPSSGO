import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"多选分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/multiple-choice.md","filePath":"analysis/multiple-choice.md"}');
const _sfc_main = { name: "analysis/multiple-choice.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="多选分析" tabindex="-1">多选分析 <a class="header-anchor" href="#多选分析" aria-label="Permalink to &quot;多选分析&quot;">​</a></h1><p>analysis-multiple-choice</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：同一多选题对应的多个选项变量，通常每列表示一个选项是否被选择。</li><li>输出：各选项的被选频次、被选率和排序结果。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/multiple-choice.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const multipleChoice = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  multipleChoice as default
};
