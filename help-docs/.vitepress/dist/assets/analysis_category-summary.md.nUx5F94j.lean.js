import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"分类汇总","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/category-summary.md","filePath":"analysis/category-summary.md"}');
const _sfc_main = { name: "analysis/category-summary.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "分类汇总",
      tabindex: "-1"
    }, [
      createTextVNode("分类汇总 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#分类汇总",
        "aria-label": 'Permalink to "分类汇总"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-category-summary", -1),
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
      createBaseVNode("li", null, "输入：1 个分类变量，外加 1 个或多个需要按组汇总的定量变量。"),
      createBaseVNode("li", null, "输出：每个组别下的样本量、均值、最小值和最大值等统计结果。")
    ], -1)
  ])]);
}
const categorySummary = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  categorySummary as default
};
