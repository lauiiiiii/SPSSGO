import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"多选分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/multiple-choice.md","filePath":"analysis/multiple-choice.md"}');
const _sfc_main = { name: "analysis/multiple-choice.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "多选分析",
      tabindex: "-1"
    }, [
      createTextVNode("多选分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#多选分析",
        "aria-label": 'Permalink to "多选分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-multiple-choice", -1),
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
      createBaseVNode("li", null, "输入：同一多选题对应的多个选项变量，通常每列表示一个选项是否被选择。"),
      createBaseVNode("li", null, "输出：各选项的被选频次、被选率和排序结果。")
    ], -1)
  ])]);
}
const multipleChoice = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  multipleChoice as default
};
