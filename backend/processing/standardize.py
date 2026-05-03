import numpy as np
import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "standardize"


def _zero_series(series: pd.Series) -> pd.Series:
    return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)


def _safe_divide(series: pd.Series, denominator) -> pd.Series:
    if denominator in (None, 0) or pd.isna(denominator):
        return _zero_series(series)
    return series / denominator


def _minmax(series: pd.Series) -> pd.Series:
    smin, smax = series.min(), series.max()
    denom = smax - smin
    if denom == 0 or pd.isna(denom):
        return _zero_series(series)
    return (series - smin) / denom


def _zscore(series: pd.Series) -> pd.Series:
    sigma = series.std()
    if sigma == 0 or pd.isna(sigma):
        return _zero_series(series)
    return (series - series.mean()) / sigma


def _sum_normalize(series: pd.Series) -> pd.Series:
    return _safe_divide(series, series.sum())


def _center(series: pd.Series) -> pd.Series:
    return series - series.mean()


def _mean_normalize(series: pd.Series) -> pd.Series:
    return _safe_divide(series, series.mean())


def _interval_scale(series: pd.Series, lower: float, upper: float) -> pd.Series:
    smin, smax = series.min(), series.max()
    denom = smax - smin
    if denom == 0 or pd.isna(denom):
        midpoint = (lower + upper) / 2
        return pd.Series(np.full(len(series), midpoint), index=series.index, dtype=float)
    return lower + ((upper - lower) * (series - smin) / denom)


def _initial_scale(series: pd.Series) -> pd.Series:
    non_zero = series[series != 0]
    if non_zero.empty:
        return _zero_series(series)
    return _safe_divide(series, non_zero.iloc[0])


def _positive_indicator(series: pd.Series) -> pd.Series:
    return _minmax(series)


def _negative_indicator(series: pd.Series) -> pd.Series:
    smin, smax = series.min(), series.max()
    denom = smax - smin
    if denom == 0 or pd.isna(denom):
        return _zero_series(series)
    return (smax - series) / denom


def _middle_indicator(series: pd.Series, best_value: float) -> pd.Series:
    max_distance = (series - best_value).abs().max()
    if max_distance == 0 or pd.isna(max_distance):
        return pd.Series(np.ones(len(series)), index=series.index, dtype=float)
    result = 1 - (series - best_value).abs() / max_distance
    return result.clip(lower=0, upper=1)


def _range_indicator(series: pd.Series, lower: float, upper: float) -> pd.Series:
    margin = max(lower - series.min(), series.max() - upper)
    if margin <= 0 or pd.isna(margin):
        return pd.Series(np.ones(len(series)), index=series.index, dtype=float)

    result = pd.Series(np.ones(len(series)), index=series.index, dtype=float)
    left_mask = series < lower
    right_mask = series > upper
    result.loc[left_mask] = 1 - (lower - series.loc[left_mask]) / margin
    result.loc[right_mask] = 1 - (series.loc[right_mask] - upper) / margin
    return result.clip(lower=0, upper=1)


def _suffix_for_method(std_method: str) -> str:
    suffix_map = {
        "minmax": "minmax",
        "zscore": "zscore",
        "sum": "sum_norm",
        "center": "center",
        "mean": "mean_norm",
        "interval": "interval",
        "initial": "initial",
        "min_value": "min_scale",
        "max_value": "max_scale",
        "positive": "positive",
        "negative": "negative",
        "middle": "middle",
        "range": "range",
    }
    return suffix_map.get(std_method, "std")


def _transform_series(series: pd.Series, params: dict) -> pd.Series:
    std_method = params.get("method", "zscore")
    if std_method == "minmax":
        return _minmax(series)
    if std_method == "zscore":
        return _zscore(series)
    if std_method == "sum":
        return _sum_normalize(series)
    if std_method == "center":
        return _center(series)
    if std_method == "mean":
        return _mean_normalize(series)
    if std_method == "interval":
        return _interval_scale(series, float(params.get("interval_min")), float(params.get("interval_max")))
    if std_method == "initial":
        return _initial_scale(series)
    if std_method == "min_value":
        return _safe_divide(series, series.min())
    if std_method == "max_value":
        return _safe_divide(series, series.max())
    if std_method == "positive":
        return _positive_indicator(series)
    if std_method == "negative":
        return _negative_indicator(series)
    if std_method == "middle":
        return _middle_indicator(series, float(params.get("best_value")))
    if std_method == "range":
        return _range_indicator(series, float(params.get("range_min")), float(params.get("range_max")))
    raise ValueError("未知数据标准化方式")


def handle(df, variables, params):
    std_method = params.get("method", "zscore")
    new_var = params.get("new_var", True)
    suffix = _suffix_for_method(std_method)

    for col in variables:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        result = _transform_series(series, params)
        if new_var:
            df[f"{col}_{suffix}"] = result
        else:
            df[col] = result
    return df, f"数据标准化完成（{std_method}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    variables = params.get("variables", []) or []
    method = params.get("method", "zscore")
    df = load_dataframe(filepath)

    if not variables:
        raise HTTPException(400, "请至少选择 1 个定量变量")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if infer_variable_type(df[col], col) != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量，数据标准化仅支持定量变量")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    valid_methods = {
        "minmax", "zscore", "sum", "center", "mean", "interval",
        "initial", "min_value", "max_value", "positive", "negative",
        "middle", "range",
    }
    if method not in valid_methods:
        raise HTTPException(400, "数据标准化方式不合法")

    try:
        if method == "interval":
            lower = float(params.get("interval_min"))
            upper = float(params.get("interval_max"))
            if lower >= upper:
                raise HTTPException(400, "区间化要求下限小于上限")
        elif method == "middle":
            float(params.get("best_value"))
        elif method == "range":
            lower = float(params.get("range_min"))
            upper = float(params.get("range_max"))
            if lower >= upper:
                raise HTTPException(400, "区间型指标处理要求下限小于上限")
    except HTTPException:
        raise
    except (TypeError, ValueError):
        if method == "interval":
            raise HTTPException(400, "请为区间化填写合法的上下限")
        if method == "middle":
            raise HTTPException(400, "请为中间型指标处理填写合法的理想值")
        if method == "range":
            raise HTTPException(400, "请为区间型指标处理填写合法的理想区间")
