import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"无效样本处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/processing-invalid-sample.md","filePath":"processing/processing-invalid-sample.md"}');
const _sfc_main = { name: "processing/processing-invalid-sample.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="无效样本处理" tabindex="-1">无效样本处理 <a class="header-anchor" href="#无效样本处理" aria-label="Permalink to &quot;无效样本处理&quot;">​</a></h1></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/processing-invalid-sample.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const processingInvalidSample = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  processingInvalidSample as default
};
