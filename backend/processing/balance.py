import pandas as pd
from fastapi import HTTPException


METHOD_KEY = "balance"


def _oversample_frame(df: pd.DataFrame, target: str):
    counts = df[target].value_counts()
    max_count = counts.max()
    frames = []
    for val, count in counts.items():
        subset = df[df[target] == val]
        if count < max_count:
            frames.append(subset.sample(n=max_count, replace=True, random_state=42))
        else:
            frames.append(subset)
    return pd.concat(frames, ignore_index=True)


def _undersample_frame(df: pd.DataFrame, target: str):
    counts = df[target].value_counts()
    min_count = counts.min()
    frames = [df[df[target] == val].sample(n=min_count, random_state=42) for val in counts.index]
    return pd.concat(frames, ignore_index=True)


def _mixed_sample_frame(df: pd.DataFrame, target: str):
    counts = df[target].value_counts()
    target_count = int(round(counts.mean()))
    frames = []
    for val, count in counts.items():
        subset = df[df[target] == val]
        if count < target_count:
            frames.append(subset.sample(n=target_count, replace=True, random_state=42))
        elif count > target_count:
            frames.append(subset.sample(n=target_count, random_state=42))
        else:
            frames.append(subset)
    return pd.concat(frames, ignore_index=True)


def handle(df, variables, params):
    target = params.get("target", "")
    b_method = params.get("method", "oversample")

    if not target or target not in df.columns:
        return df, "处理完成"

    if b_method == "oversample":
        df = _oversample_frame(df, target)
    elif b_method == "undersample":
        df = _undersample_frame(df, target)
    elif b_method == "mixed":
        df = _mixed_sample_frame(df, target)
    else:
        raise ValueError("未知样本均衡方式")

    return df, f"样本均衡完成（{b_method}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    target = (params or {}).get("target", "")
    method = (params or {}).get("method", "oversample")

    if not variables:
        raise HTTPException(400, "请至少选择 1 个变量")
    if not target:
        raise HTTPException(400, "请选择目标变量（分类变量）")
    if method not in {"oversample", "undersample", "mixed"}:
        raise HTTPException(400, "样本均衡方式不合法")

    df = load_dataframe(filepath)
    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    if target not in df.columns:
        raise HTTPException(404, f"目标变量 {target} 不存在")
    if int(df[target].isna().sum()) > 0:
        raise HTTPException(400, f"目标变量 {target} 含有空值，请先进行缺失值处理")
    target_type = infer_variable_type(df[target], target)
    if target_type != "categorical":
        raise HTTPException(400, "目标变量必须为定类变量")
