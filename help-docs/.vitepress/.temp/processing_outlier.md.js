import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"异常值处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/outlier.md","filePath":"processing/outlier.md"}');
const _sfc_main = { name: "processing/outlier.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="异常值处理" tabindex="-1">异常值处理 <a class="header-anchor" href="#异常值处理" aria-label="Permalink to &quot;异常值处理&quot;">​</a></h1><p>processing-outlier</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个或多个无空值定量变量，选择异常识别规则和处理动作。</li><li>输出：异常值会被置空、替换，或按规则进行处理，帮助后续分析更稳健。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/outlier.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const outlier = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  outlier as default
};
