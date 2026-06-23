import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"频数分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/frequency.md","filePath":"analysis/frequency.md"}');
const _sfc_main = { name: "analysis/frequency.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "频数分析",
      tabindex: "-1"
    }, [
      createTextVNode("频数分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#频数分析",
        "aria-label": 'Permalink to "频数分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-frequency", -1),
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
      createBaseVNode("li", null, "输入：1 个需要统计频次的变量，可为定类变量，也可为离散型定量变量。"),
      createBaseVNode("li", null, "输出：每个类别的频数、百分比和累计百分比，帮助你快速把握分布结构。")
    ], -1)
  ])]);
}
const frequency = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  frequency as default
};
