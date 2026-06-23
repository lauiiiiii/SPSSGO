import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"数据编码","description":"","frontmatter":{},"headers":[],"relativePath":"processing/encode.md","filePath":"processing/encode.md"}');
const _sfc_main = { name: "processing/encode.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "数据编码",
      tabindex: "-1"
    }, [
      createTextVNode("数据编码 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#数据编码",
        "aria-label": 'Permalink to "数据编码"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-encode", -1),
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
      createBaseVNode("li", null, "输入：1 个定量变量或定类变量，并选择新编码、范围编码或自动分组等方式。"),
      createBaseVNode("li", null, "输出：生成重新编码后的变量结果，可用于后续分组比较、交叉分析或建模。")
    ], -1)
  ])]);
}
const encode = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  encode as default
};
