import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"对应分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/correspondence.md","filePath":"analysis/correspondence.md"}');
const _sfc_main = { name: "analysis/correspondence.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="对应分析" tabindex="-1">对应分析 <a class="header-anchor" href="#对应分析" aria-label="Permalink to &quot;对应分析&quot;">​</a></h1><p>analysis-correspondence</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：2 个分类变量，通常来自问卷偏好题、品牌认知题、人群细分题等。</li><li>输出：类别坐标、解释维度和类别接近关系，用于做结构可视化。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/correspondence.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const correspondence = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  correspondence as default
};
