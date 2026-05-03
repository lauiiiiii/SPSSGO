# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "exploratory_factor_analysis"
METHOD_META = {'label': '因子分析（探索性）',
 'category': '综合评价',
 'description': '通过探索性因子分析识别潜在结构与指标归类',
 'order': 30,
 'slots': [{'key': 'variables', 'label': '分析变量', 'type': 'multiple', 'accept': 'numeric', 'min': 3, 'hint': '放入探索性因子分析变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "探索性因子分析至少需要 3 个变量。"}
    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，探索性因子分析需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {
        "items": variables,
        "scale_name": params.get("scale_name", "量表"),
        "data_file": "efa_input.csv",
    }
    try:
        result = run_r_script(
            "exploratory_factor_analysis.R",
            payload=payload,
            temp_files={"efa_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 探索性因子分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        if result.get("sections"):
            result["sections"].insert(0, _sec_advice("当前方法使用 R 执行探索性因子分析，并输出 KMO、Bartlett、特征值和旋转载荷矩阵。", "方法说明"))
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 探索性因子分析未返回有效结果。"}
