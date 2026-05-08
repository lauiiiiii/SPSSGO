# -*- coding: utf-8 -*-
# spssgo
import importlib
import json
import pkgutil

from backend.analysis.categories import METHOD_CATEGORIES
from backend.analysis.common import METADATA_INJECTORS, PARAM_BUILDERS, build_slot_param_example
import backend.analysis.methods as methods_package


EXCLUDED_MODULES = {"__init__"}


def _load_method_modules():
    modules = {}
    for module_info in pkgutil.iter_modules(methods_package.__path__):
        module_name = module_info.name
        if module_name in EXCLUDED_MODULES:
            continue
        module = importlib.import_module(f"{methods_package.__name__}.{module_name}")
        method_key = getattr(module, "METHOD_KEY", module_name)
        modules[method_key] = module
    return modules


def _category_order():
    return {item["key"]: index for index, item in enumerate(METHOD_CATEGORIES)}


def _sorted_method_items(modules):
    category_order = _category_order()
    return sorted(
        modules.items(),
        key=lambda item: (
            category_order.get(item[1].METHOD_META.get("category", ""), len(category_order)),
            item[1].METHOD_META.get("order", 9999),
            item[1].METHOD_META.get("label", item[0]),
        ),
    )


ANALYSIS_MODULES = dict(_sorted_method_items(_load_method_modules()))
METHOD_REGISTRY = {
    method_key: module.run
    for method_key, module in ANALYSIS_MODULES.items()
    if hasattr(module, "run")
}
MISSING_ANALYSIS_DEFAULT_METHODS = {"descriptive", "data_overview"}


def _with_common_options(method_key, meta):
    enriched = dict(meta)
    options = list(enriched.get("options") or [])
    if (
        method_key not in MISSING_ANALYSIS_DEFAULT_METHODS
        and not any(option.get("key") == "include_missing_analysis" for option in options)
    ):
        options.append({
            "key": "include_missing_analysis",
            "label": "输出缺失分析",
            "type": "checkbox",
            "default": False,
        })
    enriched["options"] = options
    return enriched


METHOD_META = {
    method_key: _with_common_options(method_key, module.METHOD_META)
    for method_key, module in ANALYSIS_MODULES.items()
    if hasattr(module, "METHOD_META")
}


def build_execute_params(method_key: str, slot_values: dict) -> dict:
    module = ANALYSIS_MODULES.get(method_key)
    if not module:
        return slot_values

    if hasattr(module, "build_params"):
        return module.build_params(slot_values)

    meta = getattr(module, "METHOD_META", {})
    builder_key = getattr(module, "PARAM_BUILDER", meta.get("param_builder", "direct"))
    builder = PARAM_BUILDERS.get(builder_key, PARAM_BUILDERS["direct"])
    return builder(slot_values)


def inject_method_metadata(method_key: str, params: dict, metadata_map: dict) -> dict:
    module = ANALYSIS_MODULES.get(method_key)
    if not module:
        return params

    if hasattr(module, "inject_metadata"):
        return module.inject_metadata(metadata_map, params)

    injector_key = getattr(module, "METADATA_INJECTOR", "")
    if not injector_key:
        return params
    injector = METADATA_INJECTORS.get(injector_key)
    if not injector:
        return params
    return injector(params, metadata_map)


def build_available_methods_prompt() -> str:
    lines = ["可用的分析方法（method 字段）及其参数：\n"]
    for method_key, meta in METHOD_META.items():
        desc = meta.get("description", "")
        sample = build_slot_param_example(meta)
        lines.append(f'  "{method_key}": {desc}')
        lines.append(f'    参数示例: {json.dumps(sample, ensure_ascii=False)}')
    return "\n".join(lines)
