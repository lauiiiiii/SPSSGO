import numpy as np
import pandas as pd


def existing_columns(df: pd.DataFrame, variables: list[str] | None) -> list[str]:
    if not variables:
        return list(df.columns)
    return [col for col in variables if col in df.columns]


def coerce_scalar(value):
    try:
        return float(value) if '.' in str(value) else int(value)
    except (ValueError, TypeError):
        return value


def sort_mixed_values(values: list) -> list:
    return sorted(
        values,
        key=lambda value: (0, float(value)) if str(value).replace('.', '', 1).isdigit() else (1, str(value)),
    )


def process_not_supported_message() -> str:
    return '自定义处理暂不支持自动执行，请使用数据分析中的 AI 助手'

