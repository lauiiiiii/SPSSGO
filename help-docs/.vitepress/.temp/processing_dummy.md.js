import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"虚拟变量转换","description":"","frontmatter":{},"headers":[],"relativePath":"processing/dummy.md","filePath":"processing/dummy.md"}');
const _sfc_main = { name: "processing/dummy.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="虚拟变量转换" tabindex="-1">虚拟变量转换 <a class="header-anchor" href="#虚拟变量转换" aria-label="Permalink to &quot;虚拟变量转换&quot;">​</a></h1><p>processing-dummy</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：1 个无空值定类变量，并选择独热编码或哑变量化方式。</li><li>输出：系统会生成若干列 0/1 变量，让原始分类信息可以进入回归或机器学习模型。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("processing/dummy.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const dummy = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  dummy as default
};
