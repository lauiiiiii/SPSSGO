# -*- coding: utf-8 -*-
import importlib
import pkgutil

import backend.processing as processing_package


EXCLUDED_MODULES = {"__init__", "common", "registry"}


def _load_processing_modules():
    modules = {}
    for module_info in pkgutil.iter_modules(processing_package.__path__):
        module_name = module_info.name
        if module_name in EXCLUDED_MODULES:
            continue
        module = importlib.import_module(f"{__package__}.{module_name}")
        method_key = getattr(module, "METHOD_KEY", module_name)
        modules[method_key] = module
    return modules


PROCESSING_MODULES = _load_processing_modules()
PROCESS_HANDLERS = {
    method_key: module.handle
    for method_key, module in PROCESSING_MODULES.items()
    if hasattr(module, "handle")
}
PROCESS_REQUEST_VALIDATORS = {
    method_key: module.validate_request
    for method_key, module in PROCESSING_MODULES.items()
    if hasattr(module, "validate_request")
}
PROCESS_METADATA_HANDLERS = {
    method_key: module.persist_metadata
    for method_key, module in PROCESSING_MODULES.items()
    if hasattr(module, "persist_metadata")
}


def run_process_method(df, method: str, params: dict):
    handler = PROCESS_HANDLERS.get(method)
    if not handler:
        raise ValueError(f"未知处理方法: {method}")
    variables = params.get("variables", [])
    return handler(df, variables, params)


async def validate_process_request(method: str, **context):
    validator = PROCESS_REQUEST_VALIDATORS.get(method)
    if not validator:
        return
    await validator(**context)


async def persist_process_metadata(session_id: str, method: str, params: dict):
    handler = PROCESS_METADATA_HANDLERS.get(method)
    if not handler:
        return
    await handler(session_id, params)
