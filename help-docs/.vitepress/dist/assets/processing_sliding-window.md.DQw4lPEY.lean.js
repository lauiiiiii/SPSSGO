import { _ as _export_sfc, o as openBlock, c as createElementBlock, j as createBaseVNode, a as createTextVNode } from "./chunks/framework.BsdvCmHD.js";
const __pageData = JSON.parse('{"title":"时序数据滑窗转换","description":"","frontmatter":{},"headers":[],"relativePath":"processing/sliding-window.md","filePath":"processing/sliding-window.md"}');
const _sfc_main = { name: "processing/sliding-window.md" };
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("div", null, [..._cache[0] || (_cache[0] = [
    createBaseVNode("h1", {
      id: "时序数据滑窗转换",
      tabindex: "-1"
    }, [
      createTextVNode("时序数据滑窗转换 "),
      createBaseVNode("a", {
        class: "header-anchor",
        href: "#时序数据滑窗转换",
        "aria-label": 'Permalink to "时序数据滑窗转换"'
      }, "​")
    ], -1),
    createBaseVNode("p", null, "processing-sliding-window", -1),
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
      createBaseVNode("li", null, "输入：1 个无空值定量时间序列变量，并设定滑窗步阶。"),
      createBaseVNode("li", null, "输出：原时间序列会被转换为带有历史窗口特征的数据表，用于回归或预测建模。")
    ], -1)
  ])]);
}
const slidingWindow = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
export {
  __pageData,
  slidingWindow as default
};
