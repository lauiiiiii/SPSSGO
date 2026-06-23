import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"信度分析","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/reliability.md","filePath":"analysis/reliability.md"}');
const _sfc_main = { name: "analysis/reliability.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "信度分析",
      tabindex: "-1"
    }, [
      createTextVNode("信度分析 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#信度分析",
        "aria-label": 'Permalink to "信度分析"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-reliability", -1),
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
      createBaseVNode("li", null, "输入：来自同一量表、量纲一致、方向一致的多个题项变量。"),
      createBaseVNode("li", null, "输出：总体 Cronbach’s α、逐项统计、删除题项后的 α 变化等结果。")
    ], -1)
  ])]);
}
const reliability = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  reliability as default
};
