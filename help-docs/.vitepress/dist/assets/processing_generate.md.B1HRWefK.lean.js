import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"生成变量","description":"","frontmatter":{},"headers":[],"relativePath":"processing/generate.md","filePath":"processing/generate.md"}');
const _sfc_main = { name: "processing/generate.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "生成变量",
      tabindex: "-1"
    }, [
      createTextVNode("生成变量 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#生成变量",
        "aria-label": 'Permalink to "生成变量"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-generate", -1),
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
      createBaseVNode("li", null, "输入：选择基础变量，填写新变量名称和生成表达式。"),
      createBaseVNode("li", null, "输出：系统新增一个计算后的变量，供后续统计分析继续使用。")
    ], -1)
  ])]);
}
const generate = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  generate as default
};
