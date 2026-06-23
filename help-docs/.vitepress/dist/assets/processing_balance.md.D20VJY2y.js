import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"样本均衡","description":"","frontmatter":{},"headers":[],"relativePath":"processing/balance.md","filePath":"processing/balance.md"}');
const _sfc_main = { name: "processing/balance.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "样本均衡",
      tabindex: "-1"
    }, [
      createTextVNode("样本均衡 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#样本均衡",
        "aria-label": 'Permalink to "样本均衡"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-balance", -1),
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
      createBaseVNode("li", null, "输入：选择参与建模的变量，并指定一个定类目标变量作为均衡对象。"),
      createBaseVNode("li", null, "输出：系统会按均衡策略调整不同类别样本数量，使训练数据分布更接近。")
    ], -1)
  ])]);
}
const balance = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  balance as default
};
