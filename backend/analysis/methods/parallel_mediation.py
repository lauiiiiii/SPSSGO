# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "parallel_mediation"
METHOD_META = {'label': '平行中介效应',
 'category': '回归&因果分析包',
 'description': '检验多个中介变量是否并行传递自变量对因变量的影响',
 'order': 45,
 'hidden': True,
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


def _as_list(value):
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            items.extend(_as_list(item))
        return items
    return []


def _unique(values):
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def run(df, params):
    """
    平行中介入口：历史隐藏入口也必须保留多 X，别再退回单 X 旧口径。
    """
    x_variables = _resolve_cols(df, _as_list(params.get("x", "")))
    y_variables = _resolve_cols(df, _as_list(params.get("y", "")))
    y = y_variables[0] if y_variables else ""
    mediators = _resolve_cols(df, _as_list(params.get("mediators", [])))
    required = _unique(x_variables + y_variables + mediators)
    missing = [variable for variable in _unique(_as_list(params.get("x", "")) + _as_list(params.get("y", "")) + _as_list(params.get("mediators", []))) if variable not in df.columns]
    if missing:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"以下变量不存在：{', '.join(missing)}。"}
    if not x_variables:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "平行中介至少需要 1 个自变量。"}
    if not y:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "平行中介需要 1 个因变量。"}
    if len(mediators) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "平行中介至少需要 2 个中介变量。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，平行中介效应需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[required].to_csv(csv_buffer, index=False)
    payload = {
        "x": x_variables,
        "y": y,
        "mediators": mediators,
        "controls": [],
        "data_file": "parallel_mediation_input.csv",
        "bootstrap": True,
        "bootstrap_reps": 1000,
        "bootstrap_method": "percentile",
        "input_config": {"y": y, "x": x_variables, "mediators": mediators, "controls": []},
    }
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
