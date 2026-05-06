import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"生成变量","description":"","frontmatter":{},"headers":[],"relativePath":"processing/generate.md","filePath":"processing/generate.md"}');
const _sfc_main = { name: "processing/generate.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="生成变量" tabindex="-1">生成变量 <a class="header-anchor" href="#生成变量" aria-label="Permalink to &quot;生成变量&quot;">​</a></h1><p>processing-generate</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：选择基础变量，填写新变量名称和生成表达式。</li><li>输出：系统新增一个计算后的变量，供后续统计分析继续使用。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/generate.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const generate = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  generate as default
};
