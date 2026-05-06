import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据降采样","description":"","frontmatter":{},"headers":[],"relativePath":"processing/downsample.md","filePath":"processing/downsample.md"}');
const _sfc_main = { name: "processing/downsample.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据降采样" tabindex="-1">数据降采样 <a class="header-anchor" href="#数据降采样" aria-label="Permalink to &quot;数据降采样&quot;">​</a></h1><p>processing-downsample</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个或多个定量变量，并设置降采样因子、位置或聚合方式。</li><li>输出：样本数量减少，但整体趋势会尽量被保留，适合长序列或高频数据预处理。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/downsample.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const downsample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  downsample as default
};
