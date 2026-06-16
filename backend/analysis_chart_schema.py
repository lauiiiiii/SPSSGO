# -*- coding: utf-8 -*-
"""分析图表协议补全，只统一图表字段命名，别在这里塞统计计算。"""
from __future__ import annotations

from typing import Any


CHART_SCHEMA_VERSION = "analysis-chart/v2"


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _dict_value(value: Any) -> dict:
    return dict(value) if isinstance(value, dict) else {}


def _put(target: dict, key: str, value: Any) -> None:
    text = _clean_text(value)
    if text and not target.get(key):
        target[key] = text


def _seed_axis_labels(data: dict, axis_labels: dict) -> None:
    _put(axis_labels, "x", data.get("xLabel"))
    _put(axis_labels, "y", data.get("yLabel"))
    _put(axis_labels, "z", data.get("zLabel"))


def normalize_chart_schema(chart: dict | None) -> dict | None:
    """补齐 chart.data.fields/axisLabels，保留旧字段给历史结果和前端兼容。"""
    if not isinstance(chart, dict):
        return chart
    data = chart.get("data")
    if not isinstance(data, dict):
        data = {}
        chart["data"] = data

    chart_type = _clean_text(chart.get("chartType"))
    fields = _dict_value(data.get("fields"))
    axis_labels = _dict_value(data.get("axisLabels"))
    variable = data.get("variable") or chart.get("varName")

    _seed_axis_labels(data, axis_labels)

    if chart_type == "category_distribution":
        _put(fields, "variable", variable)
        _put(fields, "x", variable)
        _put(axis_labels, "x", variable)
        _put(axis_labels, "y", "频数")
    elif chart_type in {"histogram", "normality_histogram", "boxplot"}:
        _put(fields, "variable", variable)
        _put(fields, "x", variable)
        _put(axis_labels, "x", variable)
    elif chart_type == "grouped_boxplot":
        _put(fields, "group", data.get("groupVariable"))
        _put(fields, "variable", variable)
        _put(fields, "y", variable)
        _put(axis_labels, "x", data.get("groupVariable"))
        _put(axis_labels, "y", variable)
    elif chart_type == "crosstab_distribution":
        _put(fields, "group", data.get("groupVariable"))
        _put(fields, "x", data.get("xVariable"))
        _put(fields, "row", data.get("xVariable"))
        _put(fields, "column", data.get("groupVariable"))
        _put(axis_labels, "x", data.get("groupVariable"))
        _put(axis_labels, "y", data.get("xVariable"))
    elif chart_type == "metric_comparison":
        _put(fields, "group", data.get("groupVariable"))
        _put(fields, "x", data.get("xVariable") or data.get("groupVariable"))
        _put(fields, "value", data.get("metric"))
        _put(fields, "y", data.get("yVariable") or data.get("metric"))
        _put(axis_labels, "x", data.get("xVariable") or data.get("groupVariable"))
        _put(axis_labels, "y", data.get("metric"))
    elif chart_type in {"scatter_plot", "correspondence_map", "factor_loading_quadrant"}:
        if data.get("purpose") != "mds":
            _put(fields, "x", data.get("xVariable") or data.get("xLabel"))
            _put(fields, "y", data.get("yVariable") or data.get("yLabel"))
        _put(fields, "z", data.get("zVariable"))
    elif chart_type in {"pp_plot", "qq_plot", "equivalence_interval"}:
        _put(fields, "variable", variable)
    elif chart_type in {"correlation_heatmap", "factor_loading_heatmap"}:
        _put(fields, "row", data.get("rowVariable"))
        _put(fields, "column", data.get("columnVariable") or data.get("colVariable"))
        _put(fields, "value", data.get("metric") or data.get("valueLabel") or data.get("legendLabel"))
    elif chart_type == "kano_better_worse":
        _put(fields, "x", data.get("xVariable"))
        _put(fields, "y", data.get("yVariable"))
        _put(fields, "value", data.get("metric"))

    if fields:
        data["fields"] = fields
    if axis_labels:
        data["axisLabels"] = axis_labels
    chart.setdefault("schemaVersion", CHART_SCHEMA_VERSION)
    return chart


def normalize_chart_section(section: dict | None) -> dict | None:
    if not isinstance(section, dict):
        return section
    charts = section.get("charts")
    if isinstance(charts, list):
        section["charts"] = [normalize_chart_schema(chart) for chart in charts]
    return section


def normalize_chart_sections(sections: list | None) -> list | None:
    if not isinstance(sections, list):
        return sections
    return [normalize_chart_section(section) for section in sections]
