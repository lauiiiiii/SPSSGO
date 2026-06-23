import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据变换","description":"","frontmatter":{},"headers":[],"relativePath":"processing/transform.md","filePath":"processing/transform.md"}');
const _sfc_main = { name: "processing/transform.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "数据变换",
      tabindex: "-1"
    }, [
      createTextVNode("数据变换 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#数据变换",
        "aria-label": 'Permalink to "数据变换"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-transform", -1),
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
      createBaseVNode("li", null, "输入：1 个无空值定量变量，并选择变换方法及其参数。"),
      createBaseVNode("li", null, "输出：变量分布、尺度或表示形式会被改变，以满足分析模型对数据的要求。")
    ], -1)
  ])]);
}
const transform = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  transform as default
};
