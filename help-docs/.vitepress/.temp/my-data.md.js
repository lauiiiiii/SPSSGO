import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"我的数据","description":"","frontmatter":{},"headers":[],"relativePath":"my-data.md","filePath":"my-data.md"}');
const _sfc_main = { name: "my-data.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}><h1 id="我的数据" tabindex="-1">我的数据 <a class="header-anchor" href="#我的数据" aria-label="Permalink to &quot;我的数据&quot;">​</a></h1><h2 id="如何上传数据" tabindex="-1">如何上传数据？ <a class="header-anchor" href="#如何上传数据" aria-label="Permalink to &quot;如何上传数据？&quot;">​</a></h2><p>第一次进入工作台后，先完成数据上传，系统才会开放后续变量配置与分析动作。</p><ol><li><strong>选择数据文件</strong>：在工作台中点击上传区域，选择本地数据文件。建议优先使用结构清晰、字段命名规范的表格文件。</li><li><strong>等待系统解析</strong>：系统会自动读取列名、样本记录与变量类型，并在左侧变量区域展示结果。</li><li><strong>核对变量信息</strong>：上传完成后先检查变量名、类型和空值情况，确认没有错列、乱码或类型识别异常。</li></ol><h2 id="上传后先检查什么" tabindex="-1">上传后先检查什么？ <a class="header-anchor" href="#上传后先检查什么" aria-label="Permalink to &quot;上传后先检查什么？&quot;">​</a></h2><h3 id="变量名是否清晰" tabindex="-1">变量名是否清晰 <a class="header-anchor" href="#变量名是否清晰" aria-label="Permalink to &quot;变量名是否清晰&quot;">​</a></h3><p>变量名尽量避免重复、含义模糊或只有编号，这会直接影响后续变量选择与结果解读。</p><h3 id="变量类型是否合理" tabindex="-1">变量类型是否合理 <a class="header-anchor" href="#变量类型是否合理" aria-label="Permalink to &quot;变量类型是否合理&quot;">​</a></h3><p>定量变量、定类变量与文本变量的判断会影响方法可用性，发现不合理时建议先做数据处理。</p><h3 id="缺失和异常是否明显" tabindex="-1">缺失和异常是否明显 <a class="header-anchor" href="#缺失和异常是否明显" aria-label="Permalink to &quot;缺失和异常是否明显&quot;">​</a></h3><p>如果存在大量空值、极端值或无效样本，建议在正式统计分析前先完成清洗。</p><h2 id="常见问题" tabindex="-1">常见问题 <a class="header-anchor" href="#常见问题" aria-label="Permalink to &quot;常见问题&quot;">​</a></h2><p><strong>上传后为什么有些方法不可选？</strong> 通常是因为变量类型、变量数量或缺失值状态不满足方法要求。先查看对应方法的变量限制和提示说明。</p><p><strong>为什么同一份数据换个方法后结果区为空？</strong> 部分方法需要先完成变量拖拽或参数设置；如果条件不足，系统不会直接运行有效结果。</p><p><strong>数据上传后会不会改变原始文件？</strong> 工作台内的处理是平台内部流程，不会直接修改你本地电脑里的原始文件。</p></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("my-data.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const myData = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  myData as default
};
