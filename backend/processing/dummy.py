import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "dummy"


def handle(df, variables, params):
    mode = params.get("mode", "dummy")
    if not variables:
        return df, "处理完成"

    col = variables[0]
    if col not in df.columns:
        return df, "处理完成"

    if mode == "dummy":
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
    else:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)

    df = df.drop(columns=[col])
    df = pd.concat([df, dummies.astype(int)], axis=1)
    return df, "虚拟变量转换完成"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    mode = params.get("mode", "dummy")
    if len(variables) != 1:
        raise HTTPException(400, "虚拟变量转换要求且仅支持 1 个定类变量")
    if mode not in {"dummy", "onehot"}:
        raise HTTPException(400, "虚拟变量转换方式不合法")

    df = load_dataframe(filepath)
    col = variables[0]
    if col not in df.columns:
        raise HTTPException(404, f"变量 {col} 不存在")
    if infer_variable_type(df[col], col) != "categorical":
        raise HTTPException(400, "虚拟变量转换仅支持定类变量")
    if int(df[col].isna().sum()) > 0:
        raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")
