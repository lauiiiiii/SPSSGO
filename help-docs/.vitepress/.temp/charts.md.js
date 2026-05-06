import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"可视化绘图","description":"","frontmatter":{},"headers":[],"relativePath":"charts.md","filePath":"charts.md"}');
const _sfc_main = { name: "charts.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="可视化绘图" tabindex="-1">可视化绘图 <a class="header-anchor" href="#可视化绘图" aria-label="Permalink to &quot;可视化绘图&quot;">​</a></h1><h2 id="适合什么场景" tabindex="-1">适合什么场景？ <a class="header-anchor" href="#适合什么场景" aria-label="Permalink to &quot;适合什么场景？&quot;">​</a></h2><p>可视化绘图适合把统计结果进一步转成更适合展示的图形，用于论文插图、答辩汇报、教学演示或业务复盘。</p><p>如果你的目标是更直观地表达组间差异、趋势变化和分布特征，建议在完成分析后再进入图表能力进行补充。</p><h2 id="使用建议" tabindex="-1">使用建议 <a class="header-anchor" href="#使用建议" aria-label="Permalink to &quot;使用建议&quot;">​</a></h2><h3 id="图先服务于结论" tabindex="-1">图先服务于结论 <a class="header-anchor" href="#图先服务于结论" aria-label="Permalink to &quot;图先服务于结论&quot;">​</a></h3><p>先明确你要表达的是差异、趋势、结构还是分布，再决定图形类型，不要只追求图形复杂。</p><h3 id="命名要一致" tabindex="-1">命名要一致 <a class="header-anchor" href="#命名要一致" aria-label="Permalink to &quot;命名要一致&quot;">​</a></h3><p>变量名、组名与图例建议保持一致，避免正文、表格和图形之间叫法不统一。</p><h3 id="避免视觉噪音" tabindex="-1">避免视觉噪音 <a class="header-anchor" href="#避免视觉噪音" aria-label="Permalink to &quot;避免视觉噪音&quot;">​</a></h3><p>过多颜色、边框和装饰会削弱重点，学术型输出通常更适合简洁风格。</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("charts.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const charts = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  charts as default
};
