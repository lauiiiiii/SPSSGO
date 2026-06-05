# -*- coding: utf-8 -*-
# 调节中介方法入口：只做变量校验和 R bridge 打包，统计口径放在 R 脚本里。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "moderated_mediation"
METHOD_META = {
    "label": "调节中介",
    "category": "回归&因果分析包",
    "description": "检验调节变量 Z 是否改变 X 通过中介变量 M 影响 Y 的间接效应",
    "order": 60,
    "slots": [
        {"key": "y", "label": "因变量Y", "type": "single", "accept": "numeric", "hint": "拖入因变量Y"},
        {"key": "x", "label": "自变量X", "type": "single", "accept": "numeric", "hint": "拖入自变量X"},
        {"key": "mediators", "label": "中介变量M", "type": "multiple", "accept": "numeric", "min": 1, "hint": "拖入中介变量M"},
        {"key": "z", "label": "调节变量Z", "type": "single", "accept": "numeric", "hint": "拖入调节变量Z"},
        {"key": "controls", "label": "控制变量", "type": "multiple", "accept": "numeric", "min": 0, "hint": "拖入控制变量"},
    ],
    "options": [
        {"key": "moderate_x_m", "label": "X→M", "type": "checkbox", "default": True},
        {"key": "moderate_m_y", "label": "M→Y", "type": "checkbox", "default": False},
        {"key": "moderate_x_y", "label": "X→Y", "type": "checkbox", "default": False},
        {
            "key": "moderator_levels",
            "label": "调节水平值",
            "type": "select",
            "default": "mean_sd",
            "choices": [
                {"value": "mean_sd", "label": "均值±1SD"},
                {"value": "quantile", "label": "分位数"},
            ],
        },
        {
            "key": "bootstrap_reps",
            "label": "bootstrap抽样次数",
            "type": "select",
            "default": "auto",
            "choices": [
                {"value": "auto", "label": "自动"},
                {"value": "1000", "label": "1000"},
                {"value": "500", "label": "500"},
                {"value": "2000", "label": "2000"},
                {"value": "5000", "label": "5000"},
            ],
        },
        {
            "key": "bootstrap_method",
            "label": "bootstrap类型",
            "type": "select",
            "default": "percentile",
            "choices": [
                {"value": "percentile", "label": "百分位bootstrap法"},
                {"value": "bias_corrected", "label": "偏差校正bootstrap法"},
            ],
        },
    ],
    "param_builder": "direct",
}


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


def _truthy(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on", "是"}


def _model_from_paths(paths):
    x_m = bool(paths.get("x_m"))
    m_y = bool(paths.get("m_y"))
    x_y = bool(paths.get("x_y"))
    mapping = {
        (False, False, True): "5",
        (True, False, False): "7",
        (True, False, True): "8",
        (False, True, False): "14",
        (False, True, True): "15",
        (True, True, False): "58",
        (True, True, True): "59",
    }
    return mapping.get((x_m, m_y, x_y), "")


def _bootstrap_method(value):
    value = str(value or "percentile").strip()
    return value if value in {"percentile", "bias_corrected"} else "percentile"


def run(df, params):
    """
    调节中介入口：多个 M 按平行中介处理，模型编号由路径勾选项映射得到。
    """
    raw_x = _as_list(params.get("x", ""))
    raw_y = _as_list(params.get("y", ""))
    raw_z = _as_list(params.get("z", ""))
    raw_mediators = _as_list(params.get("mediators", params.get("m", [])))
    raw_controls = _as_list(params.get("controls", []))
    x_values = _resolve_cols(df, raw_x)
    y_values = _resolve_cols(df, raw_y)
    z_values = _resolve_cols(df, raw_z)
    x = x_values[0] if x_values else ""
    y = y_values[0] if y_values else ""
    z = z_values[0] if z_values else ""
    mediators = _resolve_cols(df, raw_mediators)
    controls = _resolve_cols(df, raw_controls)
    requested = _unique(raw_x + raw_y + raw_z + raw_mediators + raw_controls)
    missing = [variable for variable in requested if variable not in df.columns]
    if missing:
        return _error(f"以下变量不存在：{', '.join(missing)}。")
    if not x:
        return _error("调节中介需要 1 个自变量 X。")
    if not y:
        return _error("调节中介需要 1 个因变量 Y。")
    if not z:
        return _error("调节中介需要 1 个调节变量 Z。")
    if not mediators:
        return _error("调节中介至少需要 1 个中介变量 M。")

    moderated_paths = {
        "x_m": _truthy(params.get("moderate_x_m", True)),
        "m_y": _truthy(params.get("moderate_m_y", False)),
        "x_y": _truthy(params.get("moderate_x_y", False)),
    }
    model = str(params.get("model") or _model_from_paths(moderated_paths)).replace("Model", "").strip()
    if not model:
        return _error("调节中介至少需要选择一条被 Z 调节的路径。")

    if not is_r_runtime_available():
        return _error("R 运行环境不可用，调节中介需要 R 引擎执行。")

    required = _unique([x, y, z] + mediators + controls)
    csv_buffer = StringIO()
    df[required].to_csv(csv_buffer, index=False)
    input_name = "moderated_mediation_input.csv"
    payload = {
        "x": x,
        "y": y,
        "z": z,
        "mediators": mediators,
        "controls": controls,
        "model": model,
        "moderated_paths": moderated_paths,
        "moderator_levels": params.get("moderator_levels") or "mean_sd",
        "bootstrap_reps": params.get("bootstrap_reps", "auto"),
        "bootstrap_method": _bootstrap_method(params.get("bootstrap_method")),
        "data_file": input_name,
    }
    try:
        result = run_r_script(
            "moderated_mediation.R",
            payload=payload,
            temp_files={input_name: csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return _error(f"R 调节中介执行失败：{str(exc)}")

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return _error(str(result["error"]))
    return _error("R 调节中介未返回有效结果。")
