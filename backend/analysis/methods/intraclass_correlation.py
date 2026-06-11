# -*- coding: utf-8 -*-
# 组内相关系数入口：这里只做字段整理和 R bridge，ICC 模型、CI 和报告口径放在 R 脚本里。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "intraclass_correlation"
METHOD_META = {
    "label": "ICC组内相关系数",
    "category": "数据检验",
    "description": "评估多个评价者或重复测量之间的一致性可靠性",
    "order": 75,
    "slots": [
        {
            "key": "variables",
            "label": "评价变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入多个评价者或重复测量变量；ID列若被拖入也会按普通定量列参与计算",
        },
    ],
    "options": [
        {
            "key": "icc_type",
            "label": "ICC类型",
            "choices": [
                "双向混合/随机 绝对一致性",
                "双向混合/随机 一致性",
                "单向随机 绝对一致性",
            ],
            "default": "双向混合/随机 绝对一致性",
            "hint": "选择ICC模型类型：绝对一致、一致性或单向随机。",
        },
    ],
    "param_builder": "direct",
}


def run(df, params):
    """
    组内相关系数入口：R 负责选定 ICC 口径、CI 和报告输出，Python 只处理字段和失败信息。
    """
    variables = _resolve_cols(df, params.get("variables", []))
    icc_type = params.get("icc_type") or "双向混合/随机 绝对一致性"
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "ICC 至少需要 2 个变量。"}
    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，组内相关系数需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {"variables": variables, "icc_type": icc_type, "data_file": "intraclass_correlation_input.csv"}
    try:
        result = run_r_script(
            "intraclass_correlation.R",
            payload=payload,
            temp_files={"intraclass_correlation_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 组内相关系数执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 组内相关系数未返回有效结果。"}
