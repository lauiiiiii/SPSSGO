# -*- coding: utf-8 -*-
# Kendall一致性检验入口：这里只做字段整理和 R bridge，Kendall W 口径放在 R 脚本里。
# 行代表评价者/专家，列代表被评价对象；别改回按列排名，不然会和 SPSSPRO/SPSSAU 对不上。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "kendall_consistency"
METHOD_META = {
    "label": "Kendall一致性检验",
    "category": "数据检验",
    "description": "评估多位评价者对同一批评价对象排序结果的一致性程度",
    "order": 70,
    "slots": [
        {
            "key": "variables",
            "label": "评价对象变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入被评价对象/指标列；每行代表一位评价者或专家的评分",
        },
    ],
    "options": [],
    "param_builder": "direct",
}


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def run(df, params):
    """
    Kendall 一致性检验入口。

    @param df: 原始数据，行是评价者/专家，列是被评价对象
    @param params: variables 为两个及以上评价对象变量
    @return: R 脚本返回的 Kendall's W 主表、解释和参考文献
    """
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Kendall一致性检验至少需要 2 个评价对象变量。"}
    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，Kendall一致性检验需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {"variables": variables, "data_file": "kendall_consistency_input.csv"}
    try:
        result = run_r_script(
            "kendall_consistency.R",
            payload=payload,
            temp_files={"kendall_consistency_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R Kendall一致性检验执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or METHOD_META["label"],
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "Kendall一致性检验完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R Kendall一致性检验未返回有效结果。"}
