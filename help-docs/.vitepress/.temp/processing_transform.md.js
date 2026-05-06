import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据变换","description":"","frontmatter":{},"headers":[],"relativePath":"processing/transform.md","filePath":"processing/transform.md"}');
const _sfc_main = { name: "processing/transform.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据变换" tabindex="-1">数据变换 <a class="header-anchor" href="#数据变换" aria-label="Permalink to &quot;数据变换&quot;">​</a></h1><p>processing-transform</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个无空值定量变量，并选择变换方法及其参数。</li><li>输出：变量分布、尺度或表示形式会被改变，以满足分析模型对数据的要求。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/transform.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const transform = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  transform as default
};
