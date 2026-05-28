# -*- coding: utf-8 -*-
# 这里只放线性回归入口和 R bridge 打包，统计口径固定交给 r_scripts/multiple_regression.R。
from io import StringIO

from backend.analysis.common import _resolve_cols, normalized_label_dict, pd
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "multiple_regression"
METHOD_META = {
    "label": "线性回归（最小二乘法）",
    "category": "回归&因果分析包",
    "description": "一元/多元线性回归，用最小二乘法分析 X 对 Y 的线性影响",
    "slots": [
        {
            "key": "dependent",
            "label": "因变量(Y)",
            "type": "single",
            "accept": "numeric",
            "hint": "放入单个定量因变量",
        },
        {
            "key": "predictors",
            "label": "自变量(X)",
            "type": "multiple",
            "accept": "any",
            "acceptLabel": "定量/定类",
            "min": 1,
            "hint": "放入一个或多个定量/定类自变量",
        },
    ],
    "options": [],
    "param_builder": "regression",
}


def _error(message):
    return {
        "name": METHOD_META["label"],
        "headers": [],
        "rows": [],
        "description": message,
    }


def _as_list(value):
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item not in ("", None)]
    return []


def _type_from_metadata(meta, series):
    raw_type = str((meta or {}).get("var_type") or "").strip().lower()
    if raw_type in {"categorical", "category", "nominal", "ordinal", "定类", "分类"}:
        return "categorical"
    if raw_type in {"numeric", "number", "quantitative", "scale", "定量", "数值"}:
        return "numeric"
    if (meta or {}).get("value_labels"):
        return "categorical"
    return "numeric" if pd.api.types.is_numeric_dtype(series) else "categorical"


def _non_empty_mask(series):
    text = series.astype(str).str.strip().str.lower()
    return series.notna() & ~text.isin({"", "nan", "na", "null", "none", "<na>"})


def _build_variable_meta(df, params, variables):
    injected = params.get("variable_meta") or {}
    result = {}
    for variable in variables:
        meta = injected.get(variable, {}) if isinstance(injected, dict) else {}
        result[variable] = {
            "display_name": meta.get("display_name") or variable,
            "var_type": meta.get("var_type") or _type_from_metadata(meta, df[variable]),
            "value_labels": normalized_label_dict(meta.get("value_labels", {})),
        }
    return result


def _validate_inputs(df, dependent, predictors, variable_meta):
    if dependent not in df.columns:
        return f"因变量 {dependent} 不存在。"
    if not predictors:
        return "至少需要 1 个自变量。"
    missing = [variable for variable in predictors if variable not in df.columns]
    if missing:
        return f"以下自变量不存在：{'、'.join(missing)}。"
    duplicates = sorted({variable for variable in predictors if predictors.count(variable) > 1})
    if duplicates:
        return f"自变量不能重复选择：{'、'.join(duplicates)}。"
    if dependent in predictors:
        return "因变量和自变量不能是同一个变量。"

    y_numeric = pd.to_numeric(df[dependent], errors="coerce")
    if y_numeric.notna().sum() == 0:
        return "因变量必须为定量变量，当前因变量无法转换为数值。"

    valid_mask = y_numeric.notna()
    for predictor in predictors:
        if _type_from_metadata(variable_meta.get(predictor, {}), df[predictor]) == "categorical":
            valid_mask &= _non_empty_mask(df[predictor])
        else:
            valid_mask &= pd.to_numeric(df[predictor], errors="coerce").notna()

    valid_count = int(valid_mask.sum())
    if valid_count < max(3, len(predictors) + 2):
        return "线性回归有效样本不足。"
    if y_numeric[valid_mask].nunique(dropna=True) <= 1:
        return "因变量在有效样本中没有变异，无法进行线性回归。"

    constant_predictors = []
    for predictor in predictors:
        if _type_from_metadata(variable_meta.get(predictor, {}), df[predictor]) == "categorical":
            unique_count = df.loc[valid_mask, predictor].astype(str).str.strip().nunique(dropna=True)
        else:
            unique_count = pd.to_numeric(df.loc[valid_mask, predictor], errors="coerce").nunique(dropna=True)
        if unique_count <= 1:
            constant_predictors.append(predictor)
    if constant_predictors:
        return f"以下自变量在有效样本中没有变异，无法进行稳定回归估计：{'、'.join(constant_predictors)}。"
    return ""


def inject_metadata(metadata_map, params):
    enriched = dict(params or {})
    variables = _as_list(enriched.get("predictors"))
    dependent = enriched.get("dependent", "")
    if dependent:
        variables = [dependent] + variables
    enriched["variable_meta"] = {
        variable: {
            "display_name": (metadata_map.get(variable, {}) or {}).get("display_name") or variable,
            "var_type": (metadata_map.get(variable, {}) or {}).get("var_type") or "",
            "value_labels": normalized_label_dict((metadata_map.get(variable, {}) or {}).get("value_labels", {})),
        }
        for variable in variables
        if variable
    }
    return enriched


def multiple_regression(df, params):
    """
    线性回归（最小二乘法）入口。

    @param df: 数据 DataFrame
    @param params: dependent、predictors、变量元数据和公共缺失分析开关
    @return: 含 sections 的结果字典
    """
    params = params or {}
    dependent = params.get("dependent", "")
    requested_predictors = _as_list(params.get("predictors"))
    predictors = _resolve_cols(df, requested_predictors)
    missing_predictors = [item for item in requested_predictors if item not in predictors]
    predictors = predictors + missing_predictors
    if dependent in df.columns:
        variables = [dependent] + [predictor for predictor in predictors if predictor in df.columns]
    else:
        variables = [predictor for predictor in predictors if predictor in df.columns]
    variable_meta = _build_variable_meta(df, params, variables)

    validation_error = _validate_inputs(df, dependent, predictors, variable_meta)
    if validation_error:
        return _error(validation_error)

    if not is_r_runtime_available():
        return _error("R 运行环境不可用，线性回归需要 R 引擎执行。")

    csv_buffer = StringIO()
    df[[dependent] + predictors].to_csv(csv_buffer, index=False)
    payload = {
        "dependent": dependent,
        "predictors": predictors,
        "variable_meta": variable_meta,
        "include_missing_analysis": params.get("include_missing_analysis", False),
        "data_file": "multiple_regression_input.csv",
    }
    try:
        result = run_r_script(
            "multiple_regression.R",
            payload=payload,
            temp_files={"multiple_regression_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return _error(f"R 线性回归执行失败：{str(exc)}")

    if isinstance(result, dict) and result.get("success"):
        result["name"] = result.get("name") or METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return _error(str(result["error"]))
    return _error("R 线性回归未返回有效结果。")


run = multiple_regression
