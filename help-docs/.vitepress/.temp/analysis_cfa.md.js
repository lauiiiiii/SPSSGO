import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"验证性因子分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/cfa.md","filePath":"analysis/cfa.md"}');
const _sfc_main = { name: "analysis/cfa.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="验证性因子分析" tabindex="-1">验证性因子分析 <a class="header-anchor" href="#验证性因子分析" aria-label="Permalink to &quot;验证性因子分析&quot;">​</a></h1><p>analysis-cfa</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：按理论结构分组后的多个题项集合，每组题项对应一个潜变量因子。</li><li>输出：拟合指标、因子载荷、误差项、判别效度与模型调整建议。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/cfa.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const cfa = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  cfa as default
};
