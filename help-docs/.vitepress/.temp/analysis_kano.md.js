import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"Kano模型","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/kano.md","filePath":"analysis/kano.md"}');
const _sfc_main = { name: "analysis/kano.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="kano模型" tabindex="-1">Kano模型 <a class="header-anchor" href="#kano模型" aria-label="Permalink to &quot;Kano模型&quot;">​</a></h1><p>analysis-kano</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：按一一对应关系整理好的正向题变量和反向题变量。</li><li>输出：每个属性的 Kano 分类结果及类别分布，帮助你判断不同功能特征的优先级。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/kano.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const kano = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  kano as default
};
