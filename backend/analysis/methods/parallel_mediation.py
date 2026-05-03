# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "parallel_mediation"
METHOD_META = {'label': '平行中介效应',
 'category': '高级回归&因果分析包',
 'description': '检验多个中介变量是否并行传递自变量对因变量的影响',
 'order': 120,
 'slots': [{'key': 'x', 'label': '自变量(X)', 'type': 'single', 'accept': 'numeric', 'hint': '放入自变量'},
           {'key': 'mediators',
            'label': '中介变量(M)',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入并行中介变量'},
           {'key': 'y', 'label': '因变量(Y)', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    """
    平行中介入口：保留 Python 参数入口，R 负责 PROCESS/lavaan 口径计算。
    """
    x = params.get("x", "")
    y = params.get("y", "")
    mediators = _resolve_cols(df, params.get("mediators", []))
    required = [x, y] + mediators
    missing = [variable for variable in required if variable not in df.columns]
    if missing:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"以下变量不存在：{', '.join(missing)}。"}
    if len(mediators) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "平行中介至少需要 2 个中介变量。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，平行中介效应需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[required].to_csv(csv_buffer, index=False)
    payload = {"x": x, "y": y, "mediators": mediators, "data_file": "parallel_mediation_input.csv"}
    try:
        result = run_r_script(
            "parallel_mediation.R",
            payload=payload,
            temp_files={"parallel_mediation_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 平行中介效应执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 平行中介效应未返回有效结果。"}
