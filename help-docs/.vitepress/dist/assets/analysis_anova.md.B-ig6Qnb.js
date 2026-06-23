import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"单因素方差分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/anova.md","filePath":"analysis/anova.md"}');
const _sfc_main = { name: "analysis/anova.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "单因素方差分析",
      tabindex: "-1"
    }, [
      createTextVNode("单因素方差分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#单因素方差分析",
        "aria-label": 'Permalink to "单因素方差分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-anova", -1),
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
      createBaseVNode("li", null, "输入：1 个分组变量（3 组及以上），以及 1 个或多个定量检验变量。"),
      createBaseVNode("li", null, "输出：分组描述统计、方差分析表、F 检验结果和事后比较结果。")
    ], -1)
  ])]);
}
const anova = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  anova as default
};
