import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"无效样本处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/invalid-sample.md","filePath":"processing/invalid-sample.md"}');
const _sfc_main = { name: "processing/invalid-sample.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="无效样本处理" tabindex="-1">无效样本处理 <a class="header-anchor" href="#无效样本处理" aria-label="Permalink to &quot;无效样本处理&quot;">​</a></h1><p>processing-invalid-sample</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：至少 2 个变量，并设置无效识别规则，如重复比例、缺失比例等。</li><li>输出：系统会删除无效样本，或新增一列有效/无效标记变量。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/invalid-sample.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const invalidSample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  invalidSample as default
};
