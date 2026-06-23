import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"卡方检验","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/chi-square.md","filePath":"analysis/chi-square.md"}');
const _sfc_main = { name: "analysis/chi-square.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "卡方检验",
      tabindex: "-1"
    }, [
      createTextVNode("卡方检验 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#卡方检验",
        "aria-label": 'Permalink to "卡方检验"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-chi-square", -1),
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
      createBaseVNode("li", null, "输入：2 个分类变量。"),
      createBaseVNode("li", null, "输出：交叉频数、卡方值、自由度、显著性和关联强度指标。")
    ], -1)
  ])]);
}
const chiSquare = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  chiSquare as default
};
