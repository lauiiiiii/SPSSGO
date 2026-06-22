# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import coefficient_variation


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_coefficient_variation_meta_aliases_information_weight():
    assert coefficient_variation.METHOD_META["label"] == "变异系数法（信息量权重）"
    assert "信息量权重" in coefficient_variation.METHOD_META["aliases"]

    sample = build_slot_param_example(coefficient_variation.METHOD_META)
    assert "variables" in sample


def test_coefficient_variation_uses_sample_std_and_cv_weights():
    df = pd.DataFrame(
        {
            "x1": [100, 100, 75, 100, 100, 100],
            "x2": [90, 100, 100, 100, 90, 100],
        }
    )

    result = coefficient_variation.run(df, {"variables": ["x1", "x2"]})

    assert result["headers"] == ["项", "平均值", "标准差", "CV系数", "权重(%)"]
    assert result["rows"] == [
        ["x1", "95.833", "10.206", "0.106", "66.596"],
        ["x2", "96.667", "5.164", "0.053", "33.404"],
    ]
    assert "信息量权重" in result["description"]

    main = _section(result, "输出结果1：权重计算结果")
    assert "有效样本量 N=6" in main["description"]
    assert "x1 的权重最高" in main["description"]

    chart = _section(result, "输出结果2：权重值")["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert chart["data"]["metric"] == "权重(%)"
    assert chart["data"]["labels"] == ["x1", "x2"]
    assert chart["data"]["values"] == [66.596, 33.404]
    assert chart["data"]["displayModes"] == [
        {"value": "bar", "label": "柱形图"},
        {"value": "horizontalBar", "label": "条形图"},
    ]
    assert "V_i=σ_i/X_i" in _section(result, "分析步骤")["content"]
    assert "论文" not in _section(result, "详细结论")["content"]


def test_coefficient_variation_rejects_non_positive_means():
    df = pd.DataFrame(
        {
            "x1": [-1, 0, 1],
            "x2": [1, 2, 3],
        }
    )

    result = coefficient_variation.run(df, {"variables": ["x1", "x2"]})

    assert "均值大于 0" in result["description"]
    assert "x1" in result["description"]

