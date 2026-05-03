import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "winsorize"


def handle(df, variables, params):
    mode = params.get("mode", "winsorize")
    trim_action = params.get("trim_action", "null")
    pct = params.get("percent", 5) / 100.0
    row_delete_mask = pd.Series(False, index=df.index)

    for col in variables:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        extreme_mask = (s < lo) | (s > hi)

        if mode == "winsorize":
            df[col] = s.clip(lo, hi)
        elif trim_action == "null":
            df.loc[extreme_mask, col] = pd.NA
        else:
            row_delete_mask = row_delete_mask | extreme_mask

    if mode == "trim" and trim_action == "row_delete":
        df = df.loc[~row_delete_mask].reset_index(drop=True)

    label = "缩尾" if mode == "winsorize" else "截尾"
    return df, f"{label}处理完成（{params.get('percent', 5)}%）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    mode = params.get("mode", "winsorize")
    trim_action = params.get("trim_action", "null")
    percent = params.get("percent", 5)

    if not variables:
        raise HTTPException(400, "请至少选择 1 个定量变量")

    try:
        percent = float(percent)
    except (TypeError, ValueError):
        raise HTTPException(400, "百分位必须为数值")

    if not 0 < percent < 50:
        raise HTTPException(400, "百分位必须大于 0 且小于 50")
    if mode not in {"winsorize", "trim"}:
        raise HTTPException(400, "缩尾/截尾处理方式不合法")
    if mode == "trim" and trim_action not in {"null", "row_delete"}:
        raise HTTPException(400, "截尾处理方式不合法")

    df = load_dataframe(filepath)
    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if infer_variable_type(df[col], col) != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")
