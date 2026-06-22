# -*- coding: utf-8 -*-
# AHP 快速版入口：这里只做参数整理和 R bridge，矩阵权重口径固定放到 r_scripts/ahp_simplified.R。
# data_auto 是历史兼容入口，标准专家判断仍以 matrix 模式为准。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script


def inject_metadata(metadata_map, params):
    """注入变量标题，让 R 脚本用题目名而非变量名显示。"""
    enriched = dict(params or {})
    variables = _as_list(enriched.get("variables", []))
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    return enriched

METHOD_KEY = "ahp_simplified"
METHOD_META = {
    "label": "层次分析法（AHP快速版）",
    "category": "综合评价",
    "description": "支持手填判断矩阵或按变量自动估权，快速计算 AHP 权重和一致性检验",
    "order": 20,
    "slots": [
        {
            "key": "variables",
            "label": "准则指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 0,
            "required": False,
            "hint": "数据自动估权模式下放入用于构造 AHP 权重的准则变量",
        },
    ],
    "options": [
        {
            "key": "input_mode",
            "label": "输入方式",
            "choices": [
                {"value": "matrix", "label": "手填判断矩阵"},
                {"value": "data_auto", "label": "按变量自动估权"},
            ],
            "default": "matrix",
        },
        {
            "key": "weight_method",
            "label": "计算方法",
            "choices": [
                {"value": "sum_product", "label": "和积法"},
                {"value": "root", "label": "方根法"},
                {"value": "eigen", "label": "特征向量法"},
            ],
            "default": "sum_product",
        },
    ],
    "param_builder": "direct",
}


def _error(message):
    return {
        "name": METHOD_META["label"],
        "headers": [],
        "rows": [],
        "description": message,
    }


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _normalize_input_mode(value):
    return "data_auto" if value == "data_auto" else "matrix"


def _has_matrix_payload(params):
    criteria = _as_list(params.get("criteria", []))
    matrix = params.get("matrix")
    return len(criteria) >= 2 and isinstance(matrix, list) and len(matrix) == len(criteria)


def run(df, params):
    """
    AHP 快速版入口。

    @param df: 当前数据集；仅 data_auto 模式会读取变量数据
    @param params: input_mode、criteria、matrix、variables、weight_method
    @return: R 脚本返回的权重、一致性检验和判断矩阵 sections
    """
    params = params or {}
    input_mode = _normalize_input_mode(params.get("input_mode", "matrix"))
    weight_method = params.get("weight_method") or "sum_product"

    if input_mode == "data_auto":
        variables = _resolve_cols(df, _as_list(params.get("variables", [])))
        if len(variables) < 2:
            # 旧前端状态可能残留 data_auto，但实际已经填了矩阵；这里必须兜底，不然手填矩阵也会被变量校验卡住。
            if _has_matrix_payload(params):
                input_mode = "matrix"
            else:
                return _error("AHP 快速版数据自动估权至少需要 2 个准则变量。")

    if input_mode == "data_auto":
        if not is_r_runtime_available():
            return _error("R 运行环境不可用，AHP 快速版需要 R 引擎执行。")

        csv_buffer = StringIO()
        df[variables].to_csv(csv_buffer, index=False)
        payload = {
            "input_mode": input_mode,
            "variables": variables,
            "variable_labels": params.get("variable_labels", {}),
            "weight_method": weight_method,
            "include_missing_analysis": params.get("include_missing_analysis", False),
            "data_file": "ahp_simplified_input.csv",
        }
        temp_files = {"ahp_simplified_input.csv": csv_buffer.getvalue()}
    else:
        if not is_r_runtime_available():
            return _error("R 运行环境不可用，AHP 快速版需要 R 引擎执行。")
        payload = {
            "input_mode": input_mode,
            "criteria": _as_list(params.get("criteria", [])),
            "matrix": params.get("matrix"),
            "weight_method": weight_method,
        }
        temp_files = None

    try:
        result = run_r_script(
            "ahp_simplified.R",
            payload=payload,
            temp_files=temp_files,
        )
    except RExecutionError as exc:
        return _error(f"R AHP 快速版执行失败：{str(exc)}")

    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or METHOD_META["label"],
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "AHP 快速版完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return _error(str(result["error"]))
    return _error("R AHP 快速版未返回有效结果。")
