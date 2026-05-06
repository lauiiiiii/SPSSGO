import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"调节作用","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/moderation.md","filePath":"analysis/moderation.md"}');
const _sfc_main = { name: "analysis/moderation.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="调节作用" tabindex="-1">调节作用 <a class="header-anchor" href="#调节作用" aria-label="Permalink to &quot;调节作用&quot;">​</a></h1><p>analysis-moderation</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个自变量 X、1 个调节变量 W、1 个因变量 Y。</li><li>输出：主效应、交互项效应以及调节是否成立的解释。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/moderation.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const moderation = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  moderation as default
};
