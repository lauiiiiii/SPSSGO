import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据降采样","description":"","frontmatter":{},"headers":[],"relativePath":"processing/downsample.md","filePath":"processing/downsample.md"}');
const _sfc_main = { name: "processing/downsample.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "数据降采样",
      tabindex: "-1"
    }, [
      createTextVNode("数据降采样 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#数据降采样",
        "aria-label": 'Permalink to "数据降采样"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-downsample", -1),
    createBaseVNode("h2", {
      id: "输入输出描述",
      tabindex: "-1"
    }, [
      createTextVNode("输入输出描述 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#输入输出描述",
        "aria-label": 'Permalink to "输入输出描述"'
      }, "​")
    ], -1),
    createBaseVNode("ul", null, [
      createBaseVNode("li", null, "输入：1 个或多个定量变量，并设置降采样因子、位置或聚合方式。"),
      createBaseVNode("li", null, "输出：样本数量减少，但整体趋势会尽量被保留，适合长序列或高频数据预处理。")
    ], -1)
  ])]);
}
const downsample = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  downsample as default
};
