import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"数据编码","description":"","frontmatter":{},"headers":[],"relativePath":"processing/encode.md","filePath":"processing/encode.md"}');
const _sfc_main = { name: "processing/encode.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="数据编码" tabindex="-1">数据编码 <a class="header-anchor" href="#数据编码" aria-label="Permalink to &quot;数据编码&quot;">​</a></h1><p>processing-encode</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个定量变量或定类变量，并选择新编码、范围编码或自动分组等方式。</li><li>输出：生成重新编码后的变量结果，可用于后续分组比较、交叉分析或建模。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/encode.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const encode = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  encode as default
};
