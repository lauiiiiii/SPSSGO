# -*- coding: utf-8 -*-
import re
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)

from backend.database import get_variable_metadata_map
from backend.analysis import inject_method_metadata
from backend.processing.registry import persist_process_metadata

_QUESTION_NAME_RE = re.compile(r"^q\d+(?:[_-]\d+|[_-]fill)?$", re.IGNORECASE)
_CATEGORICAL_NAME_HINTS = (
    "q", "题", "是否", "性别", "职业", "学历", "婚姻", "地区", "城市", "省份", "满意",
    "同意", "频率", "等级", "年级", "专业", "院系", "类别", "类型", "层级", "状态",
    "选项", "分组", "量表",
)
_NUMERIC_NAME_HINTS = (
    "年龄", "收入", "金额", "工资", "薪资", "分数", "得分", "总分", "均分", "次数", "时长",
    "时间", "身高", "体重", "温度", "距离", "数量", "销量", "价格", "单价", "成本",
    "比例", "占比", "rate", "ratio", "price", "cost", "age", "score", "income",
    "amount", "weight", "height", "time", "duration", "count", "num",
)


def infer_variable_type(series: pd.Series, column_name: Any) -> str:
    non_null = series.dropna()
    non_null_count = int(non_null.shape[0])
    nunique = int(non_null.nunique())
    unique_ratio = (nunique / non_null_count) if non_null_count else 0.0

    if is_bool_dtype(series):
        return "categorical"

    normalized = str(column_name).strip().lower()
    if is_numeric_dtype(series):
        return "numeric"

    if is_categorical_dtype(series) or is_object_dtype(series) or is_string_dtype(series):
        if nunique == 0:
            return "categorical"
        if nunique <= 50 and unique_ratio <= 0.5:
            return "categorical"
        if _QUESTION_NAME_RE.match(normalized) or any(hint in normalized for hint in _CATEGORICAL_NAME_HINTS):
            return "categorical"
        return "text"

    return "text"


def sort_label_values(values: list[Any]) -> list[str]:
    def sort_key(value: Any):
        text = "" if value is None else str(value)
        try:
            return (0, float(text))
        except (TypeError, ValueError):
            return (1, text)

    return [str(v) for v in sorted(values, key=sort_key)]


def recommended_auto_group_count(sample_size: int) -> int:
    if sample_size < 50:
        return 5
    if sample_size <= 100:
        return 8
    if sample_size <= 250:
        return 10
    return 15


async def persist_processing_metadata(session_id: str, method: str, params: dict):
    await persist_process_metadata(session_id, method, params)


def normalized_label_dict(value_labels: dict | None) -> dict:
    if not value_labels:
        return {}
    return {str(k): v for k, v in value_labels.items() if v not in ("", None)}


async def inject_analysis_metadata(session_id: str, method_key: str, params: dict) -> dict:
    metadata_map = await get_variable_metadata_map(session_id)
    return inject_method_metadata(method_key, params, metadata_map)

