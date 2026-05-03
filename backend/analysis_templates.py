# -*- coding: utf-8 -*-
# spssgo
"""
兼容层：保留旧导入路径，实际实现已迁移到 backend.analysis。
"""

from backend.analysis import (
    METHOD_CATEGORIES,
    METHOD_META,
    METHOD_REGISTRY,
    build_available_methods_prompt,
    build_execute_params,
    inject_method_metadata,
)

__all__ = [
    "METHOD_CATEGORIES",
    "METHOD_META",
    "METHOD_REGISTRY",
    "build_available_methods_prompt",
    "build_execute_params",
    "inject_method_metadata",
]
