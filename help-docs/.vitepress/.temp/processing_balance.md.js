import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"样本均衡","description":"","frontmatter":{},"headers":[],"relativePath":"processing/balance.md","filePath":"processing/balance.md"}');
const _sfc_main = { name: "processing/balance.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="样本均衡" tabindex="-1">样本均衡 <a class="header-anchor" href="#样本均衡" aria-label="Permalink to &quot;样本均衡&quot;">​</a></h1><p>processing-balance</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：选择参与建模的变量，并指定一个定类目标变量作为均衡对象。</li><li>输出：系统会按均衡策略调整不同类别样本数量，使训练数据分布更接近。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/balance.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const balance = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  balance as default
};
