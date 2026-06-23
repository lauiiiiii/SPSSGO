import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"无效样本处理","description":"","frontmatter":{},"headers":[],"relativePath":"processing/invalid-sample.md","filePath":"processing/invalid-sample.md"}');
const _sfc_main = { name: "processing/invalid-sample.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "无效样本处理",
      tabindex: "-1"
    }, [
      createTextVNode("无效样本处理 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#无效样本处理",
        "aria-label": 'Permalink to "无效样本处理"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-invalid-sample", -1),
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
      createBaseVNode("li", null, "输入：至少 2 个变量，并设置无效识别规则，如重复比例、缺失比例等。"),
      createBaseVNode("li", null, "输出：系统会删除无效样本，或新增一列有效/无效标记变量。")
    ], -1)
  ])]);
}
const invalidSample = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  invalidSample as default
};
