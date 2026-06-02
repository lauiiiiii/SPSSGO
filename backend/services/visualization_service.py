# -*- coding: utf-8 -*-
"""可视化绘图数据聚合，只吐图表协议，别在这里保存项目或分析结果。"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd
from fastapi import HTTPException

from backend.file_parser import parse_data_file
from backend.services.session_data_service import materialized_session_data, resolve_session_data_source
from backend.services.variable_metadata_service import infer_variable_type

CATEGORY_CHART_TYPES = {"bar", "horizontal_bar", "pie", "donut"}
NUMERIC_CHART_TYPES = {"histogram", "boxplot"}
XY_NUMERIC_CHART_TYPES = {"line", "scatter"}
GROUPED_CHART_TYPES = {"grouped_bar", "grouped_boxplot"}
SUPPORTED_CHART_TYPES = CATEGORY_CHART_TYPES | NUMERIC_CHART_TYPES | XY_NUMERIC_CHART_TYPES | GROUPED_CHART_TYPES
MAX_SCATTER_POINTS = 1200


async def preview_visualization(session_id: str, payload: dict[str, Any], *, allow_legacy_fallback: bool = False) -> dict[str, Any]:
    chart_type = str(payload.get("chart_type") or "").strip()
    if chart_type not in SUPPORTED_CHART_TYPES:
        raise HTTPException(400, "不支持的图形类型")

    variables = payload.get("variables") or {}
    options = payload.get("options") or {}
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    with materialized_session_data(data_source) as data_file:
        df, _ = parse_data_file(data_file)
        if df.empty or not len(df.columns):
            raise HTTPException(400, "当前数据为空，无法绘图")
        chart, warnings = _build_chart(df, chart_type, variables, options)
        return {"success": True, "chart": chart, "warnings": warnings}


def _build_chart(df: pd.DataFrame, chart_type: str, variables: dict[str, Any], options: dict[str, Any]):
    if chart_type in CATEGORY_CHART_TYPES:
        return _build_category_chart(df, chart_type, _var(variables, "x"), options)
    if chart_type in NUMERIC_CHART_TYPES:
        return _build_numeric_chart(df, chart_type, _var(variables, "x"), options)
    if chart_type in XY_NUMERIC_CHART_TYPES:
        return _build_xy_numeric_chart(df, chart_type, _var(variables, "x"), _var(variables, "y"), options)
    return _build_grouped_chart(df, chart_type, _var(variables, "group"), _var(variables, "y"), options)


def _var(variables: dict[str, Any], key: str) -> str:
    value = variables.get(key)
    return str(value).strip() if value is not None else ""


def _require_column(df: pd.DataFrame, column: str, label: str) -> None:
    if not column:
        raise HTTPException(400, f"请选择{label}")
    if column not in df.columns:
        raise HTTPException(400, f"变量不存在：{column}")


def _is_numeric(series: pd.Series, name: str) -> bool:
    return infer_variable_type(series, name) == "numeric"


def _require_numeric(df: pd.DataFrame, column: str, label: str) -> pd.Series:
    _require_column(df, column, label)
    series = df[column]
    if not _is_numeric(series, column):
        raise HTTPException(400, f"{label}必须是定量变量")
    return pd.to_numeric(series, errors="coerce")


def _require_category(df: pd.DataFrame, column: str, label: str) -> pd.Series:
    _require_column(df, column, label)
    series = df[column]
    if _is_numeric(series, column):
        raise HTTPException(400, f"{label}必须是定类或字符变量")
    return series


def _clean_category_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _title(options: dict[str, Any], fallback: str) -> str:
    value = str(options.get("title") or "").strip()
    return value or fallback


def _valid_warning(total: int, valid: int) -> list[str]:
    return [f"有效样本量 N={valid}，已剔除缺失 {total - valid} 行。"]


def _build_category_chart(df: pd.DataFrame, chart_type: str, column: str, options: dict[str, Any]):
    series = _require_category(df, column, "分类变量")
    valid = series.dropna()
    if valid.empty:
        raise HTTPException(400, "分类变量没有有效样本")
    labels = valid.map(_clean_category_value)
    counts_series = labels.value_counts(sort=False)
    if options.get("sort", "count_desc") != "original":
        counts_series = counts_series.sort_values(ascending=False)
    counts = [int(value) for value in counts_series.tolist()]
    total = int(sum(counts))
    percents = [round(value / total * 100, 4) if total else 0 for value in counts]
    mode_map = {
        "bar": "bar",
        "horizontal_bar": "horizontalBar",
        "pie": "pie",
        "donut": "donut",
    }
    data = {
        "labels": [str(label) for label in counts_series.index.tolist()],
        "counts": counts,
        "percents": percents,
        "total": total,
        "variable": column,
        "defaultMode": mode_map[chart_type],
        "defaultShowDataLabels": bool(options.get("show_labels", True)),
    }
    return {
        "chartType": "category_distribution",
        "title": _title(options, f"{column}分布图"),
        "data": data,
    }, _valid_warning(len(df), len(valid))


def _build_numeric_chart(df: pd.DataFrame, chart_type: str, column: str, options: dict[str, Any]):
    series = _require_numeric(df, column, "定量变量").dropna()
    if series.empty:
        raise HTTPException(400, "定量变量没有有效样本")
    if chart_type == "histogram":
        return _histogram_chart(column, series, options), _valid_warning(len(df), len(series))
    return _boxplot_chart(column, series, options), _valid_warning(len(df), len(series))


def _histogram_chart(column: str, series: pd.Series, options: dict[str, Any]) -> dict[str, Any]:
    values = series.astype(float)
    bins = _normalize_bins(options.get("bins"), len(values))
    counts, edges = _histogram(values.tolist(), bins)
    return {
        "chartType": "histogram",
        "title": _title(options, f"{column}直方图"),
        "varName": column,
        "data": {
            "binEdges": edges,
            "counts": counts,
        },
    }


def _normalize_bins(value: Any, n: int) -> int:
    if value in (None, "", "auto"):
        return min(max(math.ceil(math.sqrt(max(n, 1))), 5), 30)
    try:
        return min(max(int(value), 3), 60)
    except (TypeError, ValueError):
        return min(max(math.ceil(math.sqrt(max(n, 1))), 5), 30)


def _histogram(values: list[float], bins: int):
    low = min(values)
    high = max(values)
    if low == high:
        low -= 0.5
        high += 0.5
    width = (high - low) / bins
    counts = [0] * bins
    for value in values:
        index = min(int((value - low) / width), bins - 1)
        counts[index] += 1
    edges = [low + width * index for index in range(bins + 1)]
    return counts, edges


def _boxplot_chart(column: str, series: pd.Series, options: dict[str, Any]) -> dict[str, Any]:
    return {
        "chartType": "boxplot",
        "title": _title(options, f"{column}箱线图"),
        "varName": column,
        "data": _box_stats(series),
    }


def _box_stats(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    q1 = float(values.quantile(0.25))
    median = float(values.quantile(0.5))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr
    inlier = values[(values >= low_bound) & (values <= high_bound)]
    outliers = values[(values < low_bound) | (values > high_bound)]
    return {
        "whiskerLow": _round(float(inlier.min() if not inlier.empty else values.min())),
        "q1": _round(q1),
        "median": _round(median),
        "q3": _round(q3),
        "whiskerHigh": _round(float(inlier.max() if not inlier.empty else values.max())),
        "outliers": [_round(float(value)) for value in outliers.tolist()],
    }


def _build_xy_numeric_chart(df: pd.DataFrame, chart_type: str, x_column: str, y_column: str, options: dict[str, Any]):
    x_series = _require_numeric(df, x_column, "变量X")
    y_series = _require_numeric(df, y_column, "变量Y")
    clean = pd.DataFrame({"x": x_series, "y": y_series}).dropna()
    if clean.empty:
        raise HTTPException(400, "变量X和变量Y没有成对有效样本")
    if chart_type == "line":
        clean = clean.sort_values("x")
        labels = [_format_number(value) for value in clean["x"].tolist()]
        values = [_round(float(value)) for value in clean["y"].tolist()]
        chart = {
            "chartType": "metric_comparison",
            "title": _title(options, f"{x_column}与{y_column}折线图"),
            "data": {
                "metric": y_column,
                "labels": labels,
                "values": values,
                "defaultMode": "line",
                "displayTitle": _title(options, f"{x_column}与{y_column}折线图"),
            },
        }
        return chart, _valid_warning(len(df), len(clean))
    chart = {
        "chartType": "scatter_plot",
        "title": _title(options, f"{x_column}与{y_column}散点图"),
        "data": {
            "xLabel": x_column,
            "yLabel": y_column,
            "points": _sample_points(clean),
            "total": int(len(clean)),
        },
    }
    warnings = _valid_warning(len(df), len(clean))
    if len(clean) > MAX_SCATTER_POINTS:
        warnings.append(f"散点图最多展示 {MAX_SCATTER_POINTS} 个点，已按顺序抽样。")
    return chart, warnings


def _sample_points(clean: pd.DataFrame) -> list[dict[str, float]]:
    if len(clean) <= MAX_SCATTER_POINTS:
        sampled = clean
    else:
        indexes = [round(index * (len(clean) - 1) / (MAX_SCATTER_POINTS - 1)) for index in range(MAX_SCATTER_POINTS)]
        sampled = clean.iloc[indexes]
    return [{"x": _round(float(row.x)), "y": _round(float(row.y))} for row in sampled.itertuples()]


def _build_grouped_chart(df: pd.DataFrame, chart_type: str, group_column: str, y_column: str, options: dict[str, Any]):
    group_series = _require_category(df, group_column, "分组变量")
    y_series = _require_numeric(df, y_column, "定量变量")
    clean = pd.DataFrame({"group": group_series, "y": y_series}).dropna()
    if clean.empty:
        raise HTTPException(400, "分组变量和定量变量没有有效样本")
    clean["group_label"] = clean["group"].map(_clean_category_value)
    if chart_type == "grouped_boxplot":
        boxes = []
        for label, item in clean.groupby("group_label", sort=False):
            boxes.append({"label": str(label), **_box_stats(item["y"])})
        return {
            "chartType": "grouped_boxplot",
            "title": _title(options, f"{group_column}分组箱线图"),
            "data": {
                "variable": y_column,
                "groupVariable": group_column,
                "boxes": boxes,
            },
        }, _valid_warning(len(df), len(clean))
    summary = clean.groupby("group_label", sort=False)["y"].mean()
    if options.get("sort", "count_desc") != "original":
        summary = summary.sort_values(ascending=False)
    title = _title(options, f"{group_column}分组均值图")
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "metric": f"{y_column}均值",
            "labels": [str(label) for label in summary.index.tolist()],
            "values": [_round(float(value)) for value in summary.tolist()],
            "defaultMode": "bar",
            "displayTitle": title,
        },
    }, _valid_warning(len(df), len(clean))


def _round(value: float) -> float:
    return round(value, 6)


def _format_number(value: Any) -> str:
    num = float(value)
    if num.is_integer():
        return str(int(num))
    return str(round(num, 6))
