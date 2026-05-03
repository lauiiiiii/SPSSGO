import numpy as np
import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "outlier"


def handle(df, variables, params):
    detect = params.get("detect", "auto")
    outlier_method = params.get("method", "3sigma")
    action = params.get("action", "null")
    replace_with = params.get("replace_with", "")
    custom_val = params.get("custom_val", "")
    min_val = params.get("min_val")
    max_val = params.get("max_val")

    for col in variables:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if detect == "auto":
            if outlier_method == "3sigma":
                mu, sigma = s.mean(), s.std()
                mask = (s < mu - 3 * sigma) | (s > mu + 3 * sigma)
            elif outlier_method == "iqr":
                q1, q3 = s.quantile(0.25), s.quantile(0.75)
                iqr = q3 - q1
                mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
            elif outlier_method == "mad":
                med = s.median()
                mad = (s - med).abs().median() * 1.4826
                mask = (s - med).abs() > 3 * mad
            else:
                mask = pd.Series(False, index=s.index)
        else:
            lo = float(min_val) if min_val is not None else -np.inf
            hi = float(max_val) if max_val is not None else np.inf
            mask = (s < lo) | (s > hi)

        if action == "null":
            df.loc[mask, col] = np.nan
        elif action == "replace":
            clean = s[~mask]
            if replace_with == "mean":
                rv = clean.mean()
            elif replace_with == "median":
                rv = clean.median()
            elif replace_with == "mode":
                mode_values = clean.mode()
                rv = mode_values.iloc[0] if len(mode_values) else clean.mean()
            elif replace_with == "zero":
                rv = 0
            elif replace_with == "random":
                rv = clean.sample(n=1).iloc[0] if len(clean) else 0
            elif replace_with == "custom":
                try:
                    rv = float(custom_val)
                except (ValueError, TypeError):
                    rv = custom_val
            else:
                rv = np.nan
            df.loc[mask, col] = rv

    return df, f"异常值处理完成（{outlier_method if detect == 'auto' else 'custom'}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    if not variables:
        raise HTTPException(400, "请至少选择 1 个定量变量")

    df = load_dataframe(filepath)
    detect = params.get("detect", "auto")
    action = params.get("action", "null")
    replace_with = params.get("replace_with", "")
    min_val = params.get("min_val")
    max_val = params.get("max_val")
    custom_val = params.get("custom_val", "")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        var_type = infer_variable_type(df[col], col)
        if var_type != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量，异常值处理仅支持定量变量")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    if detect == "custom":
        if min_val in (None, "") or max_val in (None, ""):
            raise HTTPException(400, "自定义识别时请填写最小值和最大值")
        try:
            if float(min_val) >= float(max_val):
                raise HTTPException(400, "自定义范围的最小值必须小于最大值")
        except HTTPException:
            raise
        except (TypeError, ValueError):
            raise HTTPException(400, "自定义范围必须为数值")

    if action == "replace":
        if not replace_with:
            raise HTTPException(400, "请选择异常值替换方式")
        if replace_with == "custom" and custom_val in ("", None):
            raise HTTPException(400, "自定义替换时请输入替换值")
