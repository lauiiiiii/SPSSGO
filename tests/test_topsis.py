# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import topsis


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_topsis_outputs_spssau_spsspro_granularity():
    weight_slot = next(slot for slot in topsis.METHOD_META["slots"] if slot["key"] == "weight_var")
    assert weight_slot["visible_if"] == {"weight_method": "custom"}
    assert "熵权TOPSIS" in topsis.METHOD_META["aliases"]
    sample = build_slot_param_example(topsis.METHOD_META)
    assert "weight_var" not in sample
    assert sample["weight_method"] == "entropy"

    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [80, 90, 70, 95],
            "q2": [8, 6, 9, 5],
            "q3": [30, 40, 35, 45],
        }
    )

    result = topsis.run(
        df,
        {
            "positive_vars": ["q1", "q3"],
            "negative_vars": ["q2"],
            "index_var": ["name"],
            "weight_method": "entropy",
        },
    )

    assert result["headers"] == ["评价对象", "正理想解距离D+", "负理想解距离D-", "相对接近度C", "排序结果"]
    assert result["rows"]
    assert "变量权重为熵权法" in result["description"]
    assert _section(result, "输出结果1：指标权重计算")["headers"] == ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    assert _section(result, "输出结果2：TOPSIS评价法计算结果")["headers"] == result["headers"]
    assert _section(result, "输出结果3：正负理想解")["headers"] == ["项", "正理想解A+", "负理想解A-"]
    assert _section(result, "输出结果4：描述统计")["headers"] == ["项", "样本量", "平均值", "标准差"]
    chart = _section(result, "输出结果5：相对接近度排序图")["charts"][0]
    assert chart["chartType"] == "metric_comparison"


def test_topsis_equal_weight_keeps_legacy_variables_param():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
        }
    )

    result = topsis.run(df, {"variables": ["q1", "q2"], "weight_method": "TOPSIS"})

    config_rows = _section(result, "算法配置")["rows"]
    assert ["正向指标", "q1、q2"] in config_rows
    assert ["变量权重", "不设置权重"] in config_rows
    weight_rows = _section(result, "输出结果1：指标权重计算")["rows"]
    assert weight_rows[0][3] == "50.000"
    assert weight_rows[1][3] == "50.000"


def test_topsis_custom_weight_column_is_normalized_by_variable_order():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
            "weight": [7, 3, None, None],
        }
    )

    result = topsis.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "weight_method": "custom",
            "weight_var": ["weight"],
        },
    )

    weight_rows = _section(result, "输出结果1：指标权重计算")["rows"]
    assert weight_rows[0][3] == "70.000"
    assert weight_rows[1][3] == "30.000"


def test_topsis_save_process_returns_full_length_score_columns_with_custom_index():
    df = pd.DataFrame(
        {
            "q1": [1, 2, None, 4],
            "q2": [4, 3, 2, 1],
        },
        index=[10, 20, 30, 40],
    )

    result = topsis.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "weight_method": "equal",
            "save_process": True,
        },
    )

    score_columns = result["score_columns"]
    assert [column["base_name"] for column in score_columns] == [
        "TOPSIS_D正",
        "TOPSIS_D负",
        "TOPSIS_相对接近度C",
        "TOPSIS_排序结果",
    ]
    assert all(len(column["values"]) == 4 for column in score_columns)
    assert all(column["values"][2] is None for column in score_columns)
