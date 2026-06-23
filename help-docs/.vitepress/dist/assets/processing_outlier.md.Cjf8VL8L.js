import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"异常值处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/outlier.md","filePath":"processing/outlier.md"}');
const _sfc_main = { name: "processing/outlier.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "异常值处理",
      tabindex: "-1"
    }, [
      createTextVNode("异常值处理 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#异常值处理",
        "aria-label": 'Permalink to "异常值处理"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-outlier", -1),
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
      createBaseVNode("li", null, "输入：1 个或多个无空值定量变量，选择异常识别规则和处理动作。"),
      createBaseVNode("li", null, "输出：异常值会被置空、替换，或按规则进行处理，帮助后续分析更稳健。")
    ], -1)
  ])]);
}
const outlier = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  outlier as default
};
