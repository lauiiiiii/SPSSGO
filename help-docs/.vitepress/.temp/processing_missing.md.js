import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"缺失值处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/missing.md","filePath":"processing/missing.md"}');
const _sfc_main = { name: "processing/missing.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="缺失值处理" tabindex="-1">缺失值处理 <a class="header-anchor" href="#缺失值处理" aria-label="Permalink to &quot;缺失值处理&quot;">​</a></h1><p>processing-missing</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个或多个变量，并选择删除、标记或填补等处理动作。</li><li>输出：空值会被剔除、标注或按指定策略补齐，为后续分析提供更完整的数据。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/missing.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const missing = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  missing as default
};
