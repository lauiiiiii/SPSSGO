import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据标准化","description":"","frontmatter":{},"headers":[],"relativePath":"processing/standardize.md","filePath":"processing/standardize.md"}');
const _sfc_main = { name: "processing/standardize.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "数据标准化",
      tabindex: "-1"
    }, [
      createTextVNode("数据标准化 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#数据标准化",
        "aria-label": 'Permalink to "数据标准化"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-standardize", -1),
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
      createBaseVNode("li", null, "输入：1 个或多个无空值定量变量，并选择标准化方法。"),
      createBaseVNode("li", null, "输出：原始变量会被转换到统一尺度，便于综合评价、聚类、回归或机器学习建模。")
    ], -1)
  ])]);
}
const standardize = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  standardize as default
};
