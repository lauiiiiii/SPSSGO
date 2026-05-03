# -*- coding: utf-8 -*-
"""代码执行结果解析，只管 stdout/stderr 转结构化结果，别把执行器流程塞进来。"""
from __future__ import annotations

import json

RESULT_MARKER = "===ANALYSIS_RESULT_JSON==="


def parse_execution_result(stdout: str, stderr: str, returncode: int, *, audit: dict | None = None) -> dict:
    audit = dict(audit or {})
    if returncode != 0:
        return {
            "success": False,
            "error": trim_output(stderr or stdout or "代码执行失败"),
            "results": [],
            "audit": audit,
        }

    if RESULT_MARKER not in stdout:
        return {
            "success": False,
            "error": "代码未输出分析结果。请确保将结果添加到 RESULT 列表中。\nstdout: " + trim_output(stdout, limit=1000),
            "results": [],
            "audit": audit,
        }

    json_str = stdout.split(RESULT_MARKER, 1)[1].strip()
    try:
        results = json.loads(json_str)
    except json.JSONDecodeError as exc:
        return {"success": False, "error": f"结果JSON解析失败: {exc}", "results": [], "audit": audit}
    return {"success": True, "error": "", "results": results, "audit": audit}


def trim_output(content: str, *, limit: int = 2000) -> str:
    if len(content) <= limit:
        return content
    return content[-limit:]
