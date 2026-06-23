import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"Kano模型","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/kano.md","filePath":"analysis/kano.md"}');
const _sfc_main = { name: "analysis/kano.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "kano模型",
      tabindex: "-1"
    }, [
      createTextVNode("Kano模型 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#kano模型",
        "aria-label": 'Permalink to "Kano模型"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-kano", -1),
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
      createBaseVNode("li", null, "输入：按一一对应关系整理好的正向题变量和反向题变量。"),
      createBaseVNode("li", null, "输出：每个属性的 Kano 分类结果及类别分布，帮助你判断不同功能特征的优先级。")
    ], -1)
  ])]);
}
const kano = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  kano as default
};
