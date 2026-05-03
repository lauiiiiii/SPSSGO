# -*- coding: utf-8 -*-
"""
代码执行安全预检，只管黑名单检查，别把执行器和结果解析塞进来。
"""
from __future__ import annotations

from backend.config import PYTHON_BLACKLIST_PATTERNS


def check_code_safety(code: str) -> tuple[bool, str]:
    """预检代码安全性，返回 (是否安全, 原因)。"""
    for pattern in PYTHON_BLACKLIST_PATTERNS:
        if pattern in code:
            return False, f"代码包含禁止的操作: {pattern}"
    return True, ""
