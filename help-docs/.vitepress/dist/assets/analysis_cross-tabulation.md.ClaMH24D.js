import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"列联（交叉）分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/cross-tabulation.md","filePath":"analysis/cross-tabulation.md"}');
const _sfc_main = { name: "analysis/cross-tabulation.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "列联-交叉-分析",
      tabindex: "-1"
    }, [
      createTextVNode("列联（交叉）分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#列联-交叉-分析",
        "aria-label": 'Permalink to "列联（交叉）分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-cross-tabulation", -1),
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
      createBaseVNode("li", null, "输入：2 个分类变量，分别作为行变量和列变量。"),
      createBaseVNode("li", null, "输出：交叉频数、理论频数、卡方检验结果和关联强度指标。")
    ], -1)
  ])]);
}
const crossTabulation = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  crossTabulation as default
};
