import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.tree import DecisionTreeRegressor

from .common import existing_columns


METHOD_KEY = "missing"


def _is_numeric_series(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def _fill_stat(df: pd.DataFrame, cols: list[str], fill_method: str):
    for col in cols:
        if col not in df.columns:
            continue
        series = df[col]
        numeric_series = pd.to_numeric(series, errors="coerce")
        is_numeric = _is_numeric_series(series)

        if fill_method == "mean":
            df[col] = series.fillna(numeric_series.mean())
        elif fill_method == "median":
            df[col] = series.fillna(numeric_series.median())
        elif fill_method == "mode":
            mode_values = series.mode(dropna=True)
            fill_value = mode_values.iloc[0] if len(mode_values) else ""
            df[col] = series.fillna(fill_value)
        elif fill_method == "plus_3sigma":
            fill_value = numeric_series.mean() + 3 * numeric_series.std()
            df[col] = numeric_series.fillna(fill_value) if is_numeric else series
        elif fill_method == "minus_3sigma":
            fill_value = numeric_series.mean() - 3 * numeric_series.std()
            df[col] = numeric_series.fillna(fill_value) if is_numeric else series
    return df


def _fill_rule(df: pd.DataFrame, cols: list[str], fill_method: str, custom_val):
    if fill_method == "drop_all_missing_row":
        return df.dropna(how="all", subset=cols).reset_index(drop=True)

    for col in cols:
        if col not in df.columns:
            continue
        if fill_method == "ffill":
            df[col] = df[col].ffill()
        elif fill_method == "bfill":
            df[col] = df[col].bfill()
        elif fill_method == "custom":
            try:
                value = float(custom_val)
            except (TypeError, ValueError):
                value = custom_val
            df[col] = df[col].fillna(value)
    return df


def _fill_interpolate(df: pd.DataFrame, cols: list[str], fill_method: str):
    method_map = {
        "nearest": "nearest",
        "zero": "zero",
        "linear": "linear",
        "quadratic": "quadratic",
        "cubic": "cubic",
    }
    interp_method = method_map[fill_method]

    for col in cols:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        interpolated = series.interpolate(method=interp_method, limit_direction="both")
        df[col] = interpolated
    return df


def _numeric_fill_frame(df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, list[str]]:
    numeric_cols = []
    work = pd.DataFrame(index=df.index)
    for col in cols:
        if col not in df.columns:
            continue
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        work[col] = numeric_series
        numeric_cols.append(col)
    return work, numeric_cols


def _fill_model(df: pd.DataFrame, cols: list[str], fill_method: str, knn_k: int):
    work, numeric_cols = _numeric_fill_frame(df, cols)
    if not numeric_cols:
        return df

    if fill_method == "knn":
      imputer = KNNImputer(n_neighbors=knn_k)
    elif fill_method == "least_squares":
      estimator = LinearRegression()
      imputer = IterativeImputer(estimator=estimator, random_state=42)
    elif fill_method == "bayesian":
      estimator = BayesianRidge()
      imputer = IterativeImputer(estimator=estimator, random_state=42)
    elif fill_method == "decision_tree":
      estimator = DecisionTreeRegressor(max_depth=6, random_state=42)
      imputer = IterativeImputer(estimator=estimator, random_state=42)
    else:
      return df

    filled = imputer.fit_transform(work[numeric_cols])
    for index, col in enumerate(numeric_cols):
        df[col] = filled[:, index]
    return df


def _drop_mark(df: pd.DataFrame, cols: list[str], drop_mode: str, threshold: float, drop_action: str):
    if drop_mode == "row_ratio":
        mask = (df[cols].isna().sum(axis=1) / len(cols)) >= (threshold / 100.0)
        if drop_action == "delete":
            return df.loc[~mask].reset_index(drop=True), f"已按行缺失比例剔除 {int(mask.sum())} 行数据"
        result = df.copy()
        result.insert(0, "missing_row_flag", (~mask).astype(int))
        return result, f"已按行缺失比例标记 {int(mask.sum())} 行数据"

    if drop_mode == "row_count":
        mask = df[cols].isna().sum(axis=1) >= int(threshold)
        if drop_action == "delete":
            return df.loc[~mask].reset_index(drop=True), f"已按行缺失个数剔除 {int(mask.sum())} 行数据"
        result = df.copy()
        result.insert(0, "missing_row_flag", (~mask).astype(int))
        return result, f"已按行缺失个数标记 {int(mask.sum())} 行数据"

    if drop_mode == "col_ratio":
        missing_ratio = (df[cols].isna().sum(axis=0) / len(df)) * 100
        drop_cols = missing_ratio[missing_ratio >= threshold].index.tolist()
    else:
        missing_count = df[cols].isna().sum(axis=0)
        drop_cols = missing_count[missing_count >= int(threshold)].index.tolist()

    if drop_action == "delete":
        return df.drop(columns=drop_cols), f"已剔除 {len(drop_cols)} 列变量"

    result = df.copy()
    flag_map = {col: (0 if col in drop_cols else 1) for col in cols}
    result.insert(0, "missing_col_flag", [str(flag_map)] * len(result))
    return result, f"已标记 {len(drop_cols)} 列变量"


def handle(df, variables, params):
    params = params or {}
    action = params.get("action", "fill")
    cols = existing_columns(df, variables)

    if action == "drop_mark":
        return _drop_mark(
            df,
            cols,
            params.get("drop_mode", "row_ratio"),
            float(params.get("drop_threshold", 50) or 50),
            params.get("drop_action", "delete"),
        )

    fill_method = params.get("fill", "mean")
    fill_category = params.get("fill_category", "stat")
    custom_val = params.get("custom_val", "")
    knn_k = int(params.get("knn_k", 5) or 5)

    if fill_category == "stat":
        df = _fill_stat(df, cols, fill_method)
    elif fill_category == "rule":
        df = _fill_rule(df, cols, fill_method, custom_val)
    elif fill_category == "interpolate":
        df = _fill_interpolate(df, cols, fill_method)
    elif fill_category == "model":
        df = _fill_model(df, cols, fill_method, knn_k)

    return df, f"缺失值处理完成（{fill_method}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    variables = params.get("variables", []) or []
    action = params.get("action", "fill")
    fill_method = params.get("fill", "mean")
    fill_category = params.get("fill_category", "stat")
    df = load_dataframe(filepath)

    if not variables:
        raise HTTPException(400, "请至少选择 1 个变量")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")

    if action == "drop_mark":
        drop_mode = params.get("drop_mode", "row_ratio")
        drop_action = params.get("drop_action", "delete")
        if drop_mode not in {"row_ratio", "row_count", "col_ratio", "col_count"}:
            raise HTTPException(400, "剔除标记规则不合法")
        if drop_action not in {"delete", "mark"}:
            raise HTTPException(400, "剔除标记动作不合法")
        try:
            threshold = float(params.get("drop_threshold", 50))
        except (TypeError, ValueError):
            raise HTTPException(400, "剔除阈值不合法")
        if "ratio" in drop_mode and not 0 <= threshold <= 100:
            raise HTTPException(400, "缺失比例阈值必须在 0 到 100 之间")
        if "count" in drop_mode and threshold < 1:
            raise HTTPException(400, "缺失个数阈值必须大于等于 1")
        return

    if fill_category not in {"stat", "rule", "interpolate", "model"}:
        raise HTTPException(400, "缺失值填充类型不合法")

    type_map = {col: infer_variable_type(df[col], col) for col in variables}

    if fill_category == "stat":
        valid_methods = {"mean", "median", "mode", "plus_3sigma", "minus_3sigma"}
        if fill_method not in valid_methods:
            raise HTTPException(400, "统计量填充方式不合法")
        for col in variables:
            var_type = type_map[col]
            if var_type == "categorical" and fill_method != "mode":
                raise HTTPException(400, f"定类变量 {col} 的统计填充仅支持众数填充")
            if var_type != "categorical" and fill_method == "mode":
                continue
    elif fill_category == "rule":
        valid_methods = {"ffill", "bfill", "drop_all_missing_row", "custom"}
        if fill_method not in valid_methods:
            raise HTTPException(400, "规则填充方式不合法")
        if fill_method == "custom" and params.get("custom_val", "") in ("", None):
            raise HTTPException(400, "固定值 M 填充时请输入自定义值")
    elif fill_category == "interpolate":
        valid_methods = {"nearest", "zero", "linear", "quadratic", "cubic"}
        if fill_method not in valid_methods:
            raise HTTPException(400, "插值填充方式不合法")
        for col in variables:
            if type_map[col] != "numeric":
                raise HTTPException(400, f"插值填充仅支持定量变量，变量 {col} 不符合要求")
    elif fill_category == "model":
        valid_methods = {"least_squares", "bayesian", "decision_tree", "knn"}
        if fill_method not in valid_methods:
            raise HTTPException(400, "模型填充方式不合法")
        for col in variables:
            if type_map[col] != "numeric":
                raise HTTPException(400, f"模型填充仅支持定量变量，变量 {col} 不符合要求")
        if fill_method == "knn":
            try:
                knn_k = int(params.get("knn_k", 5))
            except (TypeError, ValueError):
                raise HTTPException(400, "k 近邻填充的 k 值不合法")
            if knn_k < 1:
                raise HTTPException(400, "k 值必须大于等于 1")
