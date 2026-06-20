# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import entropy_method


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_entropy_method_outputs_spssau_spsspro_combined_granularity():
    slot_keys = [slot["key"] for slot in entropy_method.METHOD_META["slots"]]
    assert slot_keys == ["positive_vars", "negative_vars", "index_var"]
    sample = build_slot_param_example(entropy_method.METHOD_META)
    assert sample["non_negative_translation"] is False
    assert sample["save_composite_score"] is False

    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [80, 90, 70, 95],
            "q2": [8, 6, 9, 5],
            "q3": [30, 40, 35, 45],
        }
    )

    result = entropy_method.run(
        df,
        {
            "positive_vars": ["q1", "q3"],
            "negative_vars": ["q2"],
            "index_var": ["name"],
        },
    )

    assert result["headers"] == ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    assert "有效样本量 N=4" in result["description"]
    assert _section(result, "算法配置")["rows"][:3] == [
        ["正向指标", "q1、q3"],
        ["负向指标", "q2"],
        ["索引项", "name"],
    ]
    assert _section(result, "输出结果1：权重计算结果")["headers"] == result["headers"]
    weight_chart = _section(result, "输出结果2：指标重要度直方图")["charts"][0]
    assert weight_chart["chartType"] == "metric_comparison"
    assert weight_chart["data"]["defaultMode"] == "bar"
    assert len(weight_chart["data"]["labels"]) == 3
    score_table = _section(result, "输出结果3：综合得分表")
    assert score_table["headers"] == ["行索引", "综合评价", "排名"]
    assert score_table["rows"][0][0] in {"A", "B", "C", "D"}
    assert _section(result, "输出结果4：综合得分概况")["headers"] == ["指标", "值"]


def test_entropy_method_non_negative_translation_reports_shift_rows():
    df = pd.DataFrame(
        {
            "q1": [-1, 0, 1, 2],
            "q2": [9, 7, 5, 3],
        }
    )

    result = entropy_method.run(
        df,
        {
            "positive_vars": ["q1"],
            "negative_vars": ["q2"],
            "non_negative_translation": True,
        },
    )

    translation = _section(result, "非负平移处理")
    assert translation["headers"] == ["变量", "矩阵最小值", "平移单位"]
    assert [row[0] for row in translation["rows"]] == ["q1", "q2"]
    assert all(row[2] == "0.0100" for row in translation["rows"])


def test_entropy_method_legacy_variables_param_uses_positive_indicators():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
        }
    )

    result = entropy_method.run(df, {"variables": ["q1", "q2"]})

    config_rows = _section(result, "算法配置")["rows"]
    assert ["正向指标", "q1、q2"] in config_rows
    assert ["负向指标", "未设置"] in config_rows
    assert result["rows"]


def test_entropy_method_save_score_returns_full_length_score_column():
    df = pd.DataFrame(
        {
            "q1": [1, 2, None, 4],
            "q2": [4, 3, 2, 1],
        },
        index=[10, 20, 30, 40],
    )

    result = entropy_method.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "save_composite_score": True,
        },
    )

    score_columns = result["score_columns"]
    assert score_columns[0]["base_name"] == "CompScore_熵值法"
    assert len(score_columns[0]["values"]) == 4
    assert score_columns[0]["values"][2] is None


def test_entropy_method_rejects_duplicate_direction_vars():
    df = pd.DataFrame({"q1": [1, 2, 3], "q2": [3, 2, 1]})

    result = entropy_method.run(df, {"positive_vars": ["q1"], "negative_vars": ["q1"]})

    assert result["headers"] == []
    assert "同一指标不能同时作为正向和负向指标" in result["description"]

