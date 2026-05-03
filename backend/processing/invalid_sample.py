import pandas as pd
from fastapi import HTTPException

from .common import existing_columns


METHOD_KEY = "invalid_sample"


def handle(df, variables, params):
    mode = params.get("mode", "rule")
    action = params.get("action", "mark")
    cols = existing_columns(df, variables)
    subset = df[cols]
    invalid_mask = pd.Series(False, index=df.index)

    if mode == "rule":
        if params.get("same_digit", False):
            pct = params.get("same_digit_pct", 80) / 100.0
            for idx, row in subset.iterrows():
                vals = row.dropna()
                if len(vals) > 0:
                    most_common_count = vals.value_counts().iloc[0]
                    if most_common_count / len(vals) >= pct:
                        invalid_mask.loc[idx] = True
        if params.get("missing", False):
            mpct = params.get("missing_pct", 50) / 100.0
            missing_ratio = subset.isna().sum(axis=1) / len(cols)
            invalid_mask = invalid_mask | (missing_ratio >= mpct)

    invalid_count = int(invalid_mask.sum())

    if action == "delete":
        df = df.loc[~invalid_mask].reset_index(drop=True)
        return df, f"已删除 {invalid_count} 条无效样本"

    mark_col = "valid_flag"
    if mark_col in df.columns:
        df = df.drop(columns=[mark_col])
    df.insert(0, mark_col, (~invalid_mask).astype(int))
    return df, f"已标记 {invalid_count} 条无效样本（首列 {mark_col}：1 有效 / 0 无效）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    if len(variables) < 2:
        raise HTTPException(400, "请至少选择 2 个变量")

    df = load_dataframe(filepath)
    mode = params.get("mode", "rule")
    same_digit = bool(params.get("same_digit", False))
    missing = bool(params.get("missing", False))
    same_digit_pct = params.get("same_digit_pct", 80)
    missing_pct = params.get("missing_pct", 50)
    action = params.get("action", "mark")

    if mode != "rule":
        raise HTTPException(400, "当前版本仅支持规则判断")
    if not same_digit and not missing:
        raise HTTPException(400, "请至少选择一种无效样本识别规则")
    if action not in {"delete", "mark"}:
        raise HTTPException(400, "无效样本处理方式不合法")

    try:
        same_digit_pct = float(same_digit_pct)
        missing_pct = float(missing_pct)
    except (TypeError, ValueError):
        raise HTTPException(400, "无效样本识别阈值必须为数值")

    if not 0 <= same_digit_pct <= 100:
        raise HTTPException(400, "相同数据出现比例必须在 0 到 100 之间")
    if not 0 <= missing_pct <= 100:
        raise HTTPException(400, "缺失比例必须在 0 到 100 之间")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        var_type = infer_variable_type(df[col], col)
        if var_type not in {"numeric", "categorical"}:
            raise HTTPException(400, f"变量 {col} 不是定量或定类变量")
