# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "serial_mediation"
METHOD_META = {'label': '链式中介',
 'category': '回归&因果分析包',
 'description': '检验多个中介变量按顺序传递影响的链式作用',
 'order': 50,
 'slots': [{'key': 'y', 'label': '变量Y', 'type': 'single', 'accept': 'numeric', 'hint': '拖入因变量Y'},
           {'key': 'x', 'label': '变量X', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '拖入变量X'},
           {'key': 'mediators',
            'label': '链式中介变量M',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '按链式顺序拖入中介变量M'},
           {'key': 'controls', 'label': '控制变量', 'type': 'multiple', 'accept': 'numeric', 'min': 0, 'hint': '拖入控制变量'}],
 'options': [
     {
         'key': 'bootstrap_reps',
         'label': 'bootstrap抽样次数',
         'type': 'select',
         'default': 'auto',
         'choices': [
             {'value': 'auto', 'label': '自动'},
             {'value': '1000', 'label': '1000'},
             {'value': '500', 'label': '500'},
             {'value': '2000', 'label': '2000'},
             {'value': '5000', 'label': '5000'},
         ],
     },
     {
         'key': 'bootstrap_method',
         'label': 'bootstrap类型',
         'type': 'select',
         'default': 'percentile',
         'choices': [
             {'value': 'percentile', 'label': '百分位bootstrap法'},
             {'value': 'bias_corrected', 'label': '偏差校正bootstrap法'},
         ],
     },
 ],
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
    链式中介入口：中介顺序由前端参数决定，R 脚本复用中介效应的回归表和 Bootstrap 口径。
    """
    x_variables = _resolve_cols(df, _as_list(params.get("x", "")))
    y_variables = _resolve_cols(df, _as_list(params.get("y", "")))
    y = y_variables[0] if y_variables else ""
    mediators = _resolve_cols(df, _as_list(params.get("mediators", [])))
    controls = _resolve_cols(df, _as_list(params.get("controls", [])))
    required = _unique(x_variables + y_variables + mediators + controls)
    requested = _unique(_as_list(params.get("x", "")) + _as_list(params.get("y", "")) + _as_list(params.get("mediators", [])) + _as_list(params.get("controls", [])))
    missing = [variable for variable in requested if variable not in df.columns]
    if missing:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"以下变量不存在：{', '.join(missing)}。"}
    if not x_variables:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "链式中介至少需要 1 个自变量。"}
    if not y:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "链式中介需要 1 个因变量。"}
    if len(mediators) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "链式中介至少需要 2 个中介变量。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，链式中介需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[required].to_csv(csv_buffer, index=False)
    payload = {
        "x": x_variables,
        "y": y,
        "mediators": mediators,
        "controls": controls,
        "data_file": "serial_mediation_input.csv",
        "bootstrap": True,
        "bootstrap_reps": params.get("bootstrap_reps", "auto"),
        "bootstrap_method": params.get("bootstrap_method", "percentile"),
        "display_name": METHOD_META["label"],
        "input_config": {"y": y, "x": x_variables, "mediators": mediators, "controls": controls},
    }
    try:
        result = run_r_script(
            "serial_mediation.R",
            payload=payload,
            temp_files={"serial_mediation_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 链式中介执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 链式中介未返回有效结果。"}
