import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"分析总览","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/overview-doc.md","filePath":"analysis/overview-doc.md"}');
const _sfc_main = { name: "analysis/overview-doc.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="分析总览" tabindex="-1">分析总览 <a class="header-anchor" href="#分析总览" aria-label="Permalink to &quot;分析总览&quot;">​</a></h1><p>analysis-overview-doc</p><h2 id="作用与适用场景" tabindex="-1">作用与适用场景 <a class="header-anchor" href="#作用与适用场景" aria-label="Permalink to &quot;作用与适用场景&quot;">​</a></h2><p>如果你希望快速上手整个分析工作流，可以先看这页。它会告诉你从选方法、拖变量、设参数到解释结果的通用顺序。</p><p>后续每一个具体分析方法都提供独立教程页，你可以在左侧继续点开相应方法查看更细的操作说明。</p><h2 id="输入输出描述" tabindex="-1">输入输出描述 <a class="header-anchor" href="#输入输出描述" aria-label="Permalink to &quot;输入输出描述&quot;">​</a></h2><ul><li>输入：一份已经上传并完成基础清洗的数据集，以及你想回答的分析问题。</li><li>输出：方法配置、结构化结果表、AI 辅助解读，以及可复制到报告中的解释文本。</li></ul><h2 id="注意事项" tabindex="-1">注意事项 <a class="header-anchor" href="#注意事项" aria-label="Permalink to &quot;注意事项&quot;">​</a></h2><ul><li>建议先完成缺失值、异常值、编码、量表方向等基础数据处理，再进入正式分析。</li><li>如果一个问题需要多种方法支持，推荐先做描述性统计，再逐步进入差异、相关、回归或结构分析。</li></ul></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("analysis/overview-doc.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const overviewDoc = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  overviewDoc as default
};
