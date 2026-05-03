import pandas as pd
from fastapi import HTTPException

from .common import existing_columns


METHOD_KEY = "downsample"


def _trimmed_groups(df: pd.DataFrame, factor: int):
    usable_length = (len(df) // factor) * factor
    trimmed = df.iloc[:usable_length].copy()
    group_ids = trimmed.reset_index(drop=True).index // factor
    return trimmed, group_ids


def handle(df, variables, params):
    params = params or {}
    mode = params.get("mode", "direct")
    factor = max(1, int(params.get("factor", 10) or 10))
    cols = existing_columns(df, variables)
    trimmed, group_ids = _trimmed_groups(df, factor)

    if trimmed.empty:
        return df.iloc[0:0].copy(), "数据量不足，未形成完整的降采样分组"

    if mode == "direct":
        position = max(1, min(factor, int(params.get("position", 1) or 1)))
        sampled = trimmed.reset_index(drop=True).groupby(group_ids, sort=False).nth(position - 1)
        return sampled.reset_index(drop=True), f"数据降采样完成（直接采样，N={factor}，位置={position}）"

    aggregate = params.get("aggregate", "mean")
    valid_aggregates = {"mean", "median", "min", "max", "sum"}
    if aggregate not in valid_aggregates:
        raise ValueError("稀释采样方法不合法")

    subset = trimmed[cols].reset_index(drop=True)
    grouped = subset.groupby(group_ids, sort=False)
    sampled = getattr(grouped, aggregate)()
    return sampled.reset_index(drop=True), f"数据降采样完成（稀释采样，N={factor}，方法={aggregate}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    variables = params.get("variables", []) or []
    mode = params.get("mode", "direct")
    df = load_dataframe(filepath)

    if not variables:
        raise HTTPException(400, "请至少选择 1 个定量变量")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if infer_variable_type(df[col], col) != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量，数据降采样仅支持定量变量")

    try:
        factor = int(params.get("factor", 10) or 10)
    except (TypeError, ValueError):
        raise HTTPException(400, "降采样因子必须为整数")
    if factor < 1:
        raise HTTPException(400, "降采样因子必须大于等于 1")

    if mode not in {"direct", "dilution"}:
        raise HTTPException(400, "数据降采样方式不合法")

    if mode == "direct":
        try:
            position = int(params.get("position", 1) or 1)
        except (TypeError, ValueError):
            raise HTTPException(400, "采样位置必须为整数")
        if position < 1 or position > factor:
            raise HTTPException(400, "采样位置必须在 1 到降采样因子之间")
    else:
        if params.get("aggregate", "mean") not in {"mean", "median", "min", "max", "sum"}:
            raise HTTPException(400, "稀释采样方法不合法")
