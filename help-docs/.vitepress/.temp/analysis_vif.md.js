import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"多重共线性 VIF","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/vif.md","filePath":"analysis/vif.md"}');
const _sfc_main = { name: "analysis/vif.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="多重共线性-vif" tabindex="-1">多重共线性 VIF <a class="header-anchor" href="#多重共线性-vif" aria-label="Permalink to &quot;多重共线性 VIF&quot;">​</a></h1><p>analysis-vif</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个或以上用于建模的定量自变量。</li><li>输出：每个变量的 VIF 值，用于评估共线性风险。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/vif.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const vif = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  vif as default
};
