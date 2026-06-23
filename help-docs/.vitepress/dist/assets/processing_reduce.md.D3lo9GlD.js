import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据降维","description":"","frontmatter":{},"headers":[],"relativePath":"processing/reduce.md","filePath":"processing/reduce.md"}');
const _sfc_main = { name: "processing/reduce.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "数据降维",
      tabindex: "-1"
    }, [
      createTextVNode("数据降维 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#数据降维",
        "aria-label": 'Permalink to "数据降维"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-reduce", -1),
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
      createBaseVNode("li", null, "输入：至少 2 个无空值定量变量，必要时再指定目标变量或维度数。"),
      createBaseVNode("li", null, "输出：系统生成更少维度的新变量，用于可视化、建模或降低复杂度。")
    ], -1)
  ])]);
}
const reduce = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  reduce as default
};
