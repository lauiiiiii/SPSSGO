import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "sliding_window"


def handle(df, variables, params):
    window_size = int(params.get("window_size", 3))
    if not variables:
        return df, "处理完成"

    col = variables[0]
    if col not in df.columns:
        return df, "处理完成"

    s = pd.to_numeric(df[col], errors="coerce")
    result = df.copy()

    for step in range(1, window_size + 1):
        result[f"X{step}"] = s.shift(window_size - step + 1)
    result["Y"] = s

    return result, f"滑窗转换完成（步阶={window_size}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    if len(variables) != 1:
        raise HTTPException(400, "时序数据滑窗转换要求且仅支持 1 个定量变量")

    try:
        window_size = int(params.get("window_size", 3))
    except (TypeError, ValueError):
        raise HTTPException(400, "步阶必须为整数")
    if window_size < 1:
        raise HTTPException(400, "步阶必须大于等于 1")

    df = load_dataframe(filepath)
    col = variables[0]
    if col not in df.columns:
        raise HTTPException(404, f"变量 {col} 不存在")
    if infer_variable_type(df[col], col) != "numeric":
        raise HTTPException(400, "时序数据滑窗转换仅支持定量变量")
    if int(df[col].isna().sum()) > 0:
        raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")
