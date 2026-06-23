import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"多重共线性 VIF","description":"","frontmatter":{},"headers":[],"relativePath":"analysis/vif.md","filePath":"analysis/vif.md"}');
const _sfc_main = { name: "analysis/vif.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "多重共线性-vif",
      tabindex: "-1"
    }, [
      createTextVNode("多重共线性 VIF "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#多重共线性-vif",
        "aria-label": 'Permalink to "多重共线性 VIF"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "analysis-vif", -1),
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
      createBaseVNode("li", null, "输入：2 个或以上用于建模的定量自变量。"),
      createBaseVNode("li", null, "输出：每个变量的 VIF 值，用于评估共线性风险。")
    ], -1)
  ])]);
}
const vif = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  vif as default
};
