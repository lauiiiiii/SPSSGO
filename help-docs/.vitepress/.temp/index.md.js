import { ssrRenderAttrs } from "vue/server-renderer";
import { useSSRContext } from "vue";
import { _ as _export_sfc } from "./plugin-vue_export-helper.1tPrXgE0.js";
const __pageData = JSON.parse('{"title":"","description":"","frontmatter":{"layout":"home","hero":{"name":"SPSSGO","text":"帮助中心","tagline":"数据分析平台使用文档 · 从入门到精通","actions":[{"theme":"brand","text":"我的数据","link":"/my-data"},{"theme":"alt","text":"数据分析","link":"/analysis"}]},"features":[{"title":"我的数据","details":"数据上传、格式支持、变量检查与常见问题","link":"/my-data"},{"title":"可视化绘图","details":"图表类型选择与使用建议","link":"/charts"},{"title":"数据处理","details":"缺失值、异常值、编码、标准化等 16 种数据处理方法","link":"/processing"},{"title":"数据分析","details":"描述统计、差异检验、回归分析等 40+ 分析方法","link":"/analysis"}]},"headers":[],"relativePath":"index.md","filePath":"index.md"}');
const _sfc_main = { name: "index.md" };
function _sfc_ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  _push(`<div${ssrRenderAttrs(_attrs)}></div>`);
}
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("index.md");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};
const index = /* @__PURE__ */ _export_sfc(_sfc_main, [["ssrRender", _sfc_ssrRender]]);
export {
  __pageData,
  index as default
};
