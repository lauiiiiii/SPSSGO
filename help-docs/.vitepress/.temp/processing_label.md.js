import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据标签","description":"","frontmatter":{},"headers":[],"relativePath":"processing/label.md","filePath":"processing/label.md"}');
const _sfc_main = { name: "processing/label.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据标签" tabindex="-1">数据标签 <a class="header-anchor" href="#数据标签" aria-label="Permalink to &quot;数据标签&quot;">​</a></h1><p>processing-label</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个定类变量，以及每个编码值对应的文字标签。</li><li>输出：变量本身数值不变，但在展示和结果阅读时可直接看到更易理解的标签文字。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/label.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const label = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  label as default
};
