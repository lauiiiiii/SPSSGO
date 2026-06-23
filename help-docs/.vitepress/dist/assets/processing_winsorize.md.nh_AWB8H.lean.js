import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"缩尾/截尾处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/winsorize.md","filePath":"processing/winsorize.md"}');
const _sfc_main = { name: "processing/winsorize.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "缩尾-截尾处理",
      tabindex: "-1"
    }, [
      createTextVNode("缩尾/截尾处理 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#缩尾-截尾处理",
        "aria-label": 'Permalink to "缩尾/截尾处理"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-winsorize", -1),
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
      createBaseVNode("li", null, "输入：1 个或多个无空值定量变量，并设置百分位阈值和处理方式。"),
      createBaseVNode("li", null, "输出：连续变量尾部的极端值会被缩尾、置空或整行删除。")
    ], -1)
  ])]);
}
const winsorize = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  winsorize as default
};
