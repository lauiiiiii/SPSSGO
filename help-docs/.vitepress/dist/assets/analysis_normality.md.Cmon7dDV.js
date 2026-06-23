import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"正态性分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/normality.md","filePath":"analysis/normality.md"}');
const _sfc_main = { name: "analysis/normality.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "正态性分析",
      tabindex: "-1"
    }, [
      createTextVNode("正态性分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#正态性分析",
        "aria-label": 'Permalink to "正态性分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-normality", -1),
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
      createBaseVNode("li", null, "输入：1 个或多个定量变量。"),
      createBaseVNode("li", null, "输出：每个变量的 Shapiro-Wilk 检验统计量与显著性，用于辅助判断正态性。")
    ], -1)
  ])]);
}
const normality = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  normality as default
};
