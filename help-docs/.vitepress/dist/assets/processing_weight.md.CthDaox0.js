import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"样本加权","description":"","frontmatter":{},"headers":[],"relativePath":"processing/weight.md","filePath":"processing/weight.md"}');
const _sfc_main = { name: "processing/weight.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "样本加权",
      tabindex: "-1"
    }, [
      createTextVNode("样本加权 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#样本加权",
        "aria-label": 'Permalink to "样本加权"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-weight", -1),
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
      createBaseVNode("li", null, "输入：选择待分析变量，并指定一个权重变量作为加权依据。"),
      createBaseVNode("li", null, "输出：后续统计中，不同样本会按权重值产生不同影响。")
    ], -1)
  ])]);
}
const weight = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  weight as default
};
