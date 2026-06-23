import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"虚拟变量转换","description":"","frontmatter":{},"headers":[],"relativePath":"processing/dummy.md","filePath":"processing/dummy.md"}');
const _sfc_main = { name: "processing/dummy.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "虚拟变量转换",
      tabindex: "-1"
    }, [
      createTextVNode("虚拟变量转换 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#虚拟变量转换",
        "aria-label": 'Permalink to "虚拟变量转换"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-dummy", -1),
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
      createBaseVNode("li", null, "输入：1 个无空值定类变量，并选择独热编码或哑变量化方式。"),
      createBaseVNode("li", null, "输出：系统会生成若干列 0/1 变量，让原始分类信息可以进入回归或机器学习模型。")
    ], -1)
  ])]);
}
const dummy = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  dummy as default
};
