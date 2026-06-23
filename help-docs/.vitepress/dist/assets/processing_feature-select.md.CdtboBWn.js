import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"特征筛选","description":"","frontmatter":{},"headers":[],"relativePath":"processing/feature-select.md","filePath":"processing/feature-select.md"}');
const _sfc_main = { name: "processing/feature-select.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "特征筛选",
      tabindex: "-1"
    }, [
      createTextVNode("特征筛选 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#特征筛选",
        "aria-label": 'Permalink to "特征筛选"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-feature-select", -1),
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
      createBaseVNode("li", null, "输入：多个候选特征变量，并按不同筛选方法设置目标变量或阈值。"),
      createBaseVNode("li", null, "输出：系统会给出保留/剔除建议，帮助你缩小特征集。")
    ], -1)
  ])]);
}
const featureSelect = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  featureSelect as default
};
