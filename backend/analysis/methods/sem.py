# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "sem"
METHOD_META = {'label': '结构方程模型(SEM)',
 'category': '高级回归&因果分析包',
 'description': '同时估计测量模型和结构模型，适合潜变量与复杂理论检验',
 'order': 110,
 'slots': [{'key': 'measurement_vars',
            'label': '测量题项',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 3,
            'hint': '放入潜变量题项'}],
 'options': [],
 'param_builder': 'direct'}


def _build_factor_map(df, params):
    factor_keys = []
    for key in params.keys():
        match = re.match(r"^factor(\d+)_vars$", str(key))
        if match:
            factor_keys.append((int(match.group(1)), key))
    factor_keys.sort(key=lambda item: item[0])

    factor_map = {}
    if factor_keys:
        for idx, key in factor_keys:
            cols = _resolve_cols(df, params.get(key, []))
            if cols:
                factor_map[f"F{idx}"] = cols
    else:
        measurement_vars = _resolve_cols(df, params.get("measurement_vars", []))
        if measurement_vars:
            factor_map["F1"] = measurement_vars
    return factor_map


def _parse_structural_paths(params, factor_names):
    raw_paths = params.get("structural_paths", [])
    parsed = []
    for item in raw_paths:
        if isinstance(item, dict):
            left = str(item.get("dependent", "")).strip()
            rights = item.get("predictors", []) or []
            rights = [str(value).strip() for value in rights if str(value).strip()]
            if left and rights:
                parsed.append((left, rights))
        elif isinstance(item, str) and "~" in item:
            left, right = item.split("~", 1)
            left = left.strip()
            rights = [value.strip() for value in right.split("+") if value.strip()]
            if left and rights:
                parsed.append((left, rights))
    if parsed:
        return parsed
    if len(factor_names) >= 2:
        return [(factor_names[-1], factor_names[:-1])]
    return []


def run(df, params):
    factor_map = _build_factor_map(df, params)
    if not factor_map:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "SEM 至少需要一组测量题项。"}
    if any(len(items) < 2 for items in factor_map.values()):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "每个潜变量至少需要 2 个测量题项。"}

    variables = []
    for items in factor_map.values():
        variables.extend(items)
    variables = list(dict.fromkeys(variables))

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，结构方程模型需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {
        "factor_map": factor_map,
        "structural_paths": [
            {"dependent": left, "predictors": rights}
            for left, rights in _parse_structural_paths(params, list(factor_map.keys()))
        ],
        "data_file": "sem_input.csv",
    }
    try:
        r_result = run_r_script(
            "sem.R",
            payload=payload,
            temp_files={"sem_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 结构方程模型执行失败：{str(exc)}"}

    if isinstance(r_result, dict) and r_result.get("success"):
        return {
            "name": r_result.get("name") or METHOD_META["label"],
            "headers": r_result.get("headers") or [],
            "rows": r_result.get("rows") or [],
            "description": r_result.get("description") or "SEM 执行完成。",
            "sections": r_result.get("sections") or [],
        }
    if isinstance(r_result, dict) and r_result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(r_result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 结构方程模型未返回有效结果。"}
