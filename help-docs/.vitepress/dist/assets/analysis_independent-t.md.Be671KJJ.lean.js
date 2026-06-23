import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"独立样本T检验","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/independent-t.md","filePath":"analysis/independent-t.md"}');
const _sfc_main = { name: "analysis/independent-t.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "独立样本t检验",
      tabindex: "-1"
    }, [
      createTextVNode("独立样本T检验 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#独立样本t检验",
        "aria-label": 'Permalink to "独立样本T检验"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-independent-t", -1),
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
      createBaseVNode("li", null, "输入：1 个二分类分组变量，以及 1 个或多个需要比较的定量检验变量。"),
      createBaseVNode("li", null, "输出：分组描述统计、方差齐性检验、t 检验结果和效应量。")
    ], -1)
  ])]);
}
const independentT = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  independentT as default
};
