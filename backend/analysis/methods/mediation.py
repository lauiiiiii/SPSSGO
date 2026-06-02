# -*- coding: utf-8 -*-
# 这里只放中介效应入口和 R bridge 打包，输出口径对齐平行中介。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "mediation"
METHOD_META = {'label': '中介效应',
 'category': '回归&因果分析包',
 'description': '用于探究是否是哪些变量影响 X-->Y 这个流程的因素。',
 'order': 40,
 'slots': [{'key': 'y', 'label': '变量Y', 'type': 'single', 'accept': 'numeric', 'hint': '拖入因变量Y'},
           {'key': 'x', 'label': '变量X', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '拖入变量X'},
           {'key': 'mediators',
            'label': '中介变量M',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '拖入中介变量M'},
           {'key': 'controls',
            'label': '控制变量',
           'type': 'multiple',
           'accept': 'numeric',
           'min': 0,
           'hint': '拖入控制变量'}],
 'options': [{'key': 'bootstrap_reps',
              'label': 'bootstrap抽样次数',
              'type': 'select',
              'default': 'auto',
              'choices': [{'value': 'auto', 'label': '自动'},
                          {'value': '1000', 'label': '1000'},
                          {'value': '500', 'label': '500'},
                          {'value': '2000', 'label': '2000'},
                          {'value': '5000', 'label': '5000'}]},
             {'key': 'bootstrap_method',
              'label': 'bootstrap类型',
              'type': 'select',
              'default': 'percentile',
              'choices': [{'value': 'percentile', 'label': '百分位bootstrap法'},
                          {'value': 'bias_corrected', 'label': '偏差校正bootstrap法'}]}],
 'param_builder': 'direct'}


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


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


def _as_reps(value):
    if value in (None, "", "auto", "default"):
        return 1000
    try:
        reps = int(value)
    except (TypeError, ValueError):
        return 1000
    return reps if reps >= 100 else 1000


def _bootstrap_method(value):
    value = str(value or "percentile").strip()
    return value if value in {"percentile", "bias_corrected"} else "percentile"


def mediation_analysis(df, params):
    """
    中介效应入口：Python 只做字段校验和数据打包，计算固定交给平行中介 R 口径。

    @param df: 数据 DataFrame
    @param params: 包含 x, mediators/m, y 的参数字典
    @return: 含 sections 的结果字典
    """
    raw_x = _as_list(params.get("x", ""))
    raw_y = _as_list(params.get("y", ""))
    raw_mediators = _as_list(params.get("mediators", params.get("m", [])))
    raw_controls = _as_list(params.get("controls", []))
    x_variables = _resolve_cols(df, raw_x)
    x = x_variables[0] if x_variables else ""
    y_variables = _resolve_cols(df, raw_y)
    y = y_variables[0] if y_variables else ""
    mediators = _resolve_cols(df, raw_mediators)
    controls = _resolve_cols(df, raw_controls)
    required = _unique(x_variables + y_variables + mediators + controls)
    missing = [variable for variable in _unique(raw_x + raw_y + raw_mediators + raw_controls) if variable not in df.columns]
    if missing:
        return _error(f"以下变量不存在：{', '.join(missing)}。")
    if not x:
        return _error("中介效应至少需要 1 个自变量 X。")
    if not y:
        return _error("中介效应需要 1 个因变量 Y。")
    if not mediators:
        return _error("中介效应至少需要 1 个中介变量。")

    if not is_r_runtime_available():
        return _error("R 运行环境不可用，中介效应需要 R 引擎执行。")

    csv_buffer = StringIO()
    df[required].to_csv(csv_buffer, index=False)
    input_name = "parallel_mediation_input.csv"
    payload = {
        "x": x_variables,
        "y": y,
        "mediators": mediators,
        "controls": controls,
        "data_file": input_name,
        "display_name": METHOD_META["label"],
        "bootstrap": True,
        "bootstrap_reps": _as_reps(params.get("bootstrap_reps")),
        "bootstrap_method": _bootstrap_method(params.get("bootstrap_method")),
        "input_config": {
            "y": y,
            "x": x_variables,
            "mediators": mediators,
            "controls": controls,
        },
    }
    try:
        result = run_r_script(
            "parallel_mediation.R",
            payload=payload,
            temp_files={input_name: csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return _error(f"R 中介效应执行失败：{str(exc)}")

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return _error(str(result["error"]))
    return _error("R 中介效应未返回有效结果。")

run = mediation_analysis
