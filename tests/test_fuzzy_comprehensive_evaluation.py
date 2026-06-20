# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import fuzzy_comprehensive_evaluation


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_fuzzy_outputs_spssau_spsspro_granularity():
    weight_slot = next(
        slot for slot in fuzzy_comprehensive_evaluation.METHOD_META["slots"]
        if slot["key"] == "weight_var"
    )
    assert weight_slot["visible_if"] == {"weight_method": "custom"}
    sample = build_slot_param_example(fuzzy_comprehensive_evaluation.METHOD_META)
    assert "weight_var" not in sample
    assert sample["weight_method"] == "entropy"

    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [1, 2, 4, 8],
            "q2": [8, 4, 2, 1],
            "q3": [2, 3, 5, 7],
        }
    )

    result = fuzzy_comprehensive_evaluation.run(
        df,
        {
            "variables": ["q1", "q2", "q3"],
            "index_var": ["name"],
            "weight_method": "entropy",
            "fuzzy_operator": "weighted_average",
        },
    )

    assert result["headers"] == ["评价对象", "差隶属度", "中隶属度", "优隶属度", "最大隶属等级", "综合得分", "排序"]
    assert "加权平均型" in result["description"]
    assert _section(result, "输出结果1：指标权重计算")["headers"] == ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    assert _section(result, "输出结果2：综合隶属度矩阵")["headers"] == [
        "评价对象",
        "差",
        "中",
        "优",
        "差(归一化)",
        "中(归一化)",
        "优(归一化)",
    ]
    assert _section(result, "输出结果3：综合得分计算")["headers"] == result["headers"]
    chart = _section(result, "输出结果4：综合得分排序图")["charts"][0]
    assert chart["chartType"] == "metric_comparison"


def test_fuzzy_operator_choices_are_all_supported():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 4, 8],
            "q2": [8, 4, 2, 1],
            "q3": [2, 3, 5, 7],
        }
    )

    for operator in [
        "main_factor_decision",
        "main_factor_prominent",
        "bounded_sum_min",
        "weighted_average",
        "取小与有界型：M(∧,+)",
    ]:
        result = fuzzy_comprehensive_evaluation.run(
            df,
            {"variables": ["q1", "q2", "q3"], "weight_method": "equal", "fuzzy_operator": operator},
        )

        assert result["rows"]
        operator_table = _section(result, "模糊算子说明")
        assert any(row[1] == "当前选择" for row in operator_table["rows"])


def test_fuzzy_custom_weight_column_is_normalized_by_variable_order():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [1, 2, 4, 8],
            "q2": [8, 4, 2, 1],
            "weight": [7, 3, None, None],
        }
    )

    result = fuzzy_comprehensive_evaluation.run(
        df,
        {
            "variables": ["q1", "q2"],
            "index_var": ["name"],
            "weight_method": "custom",
            "weight_var": ["weight"],
        },
    )

    weight_rows = _section(result, "输出结果1：指标权重计算")["rows"]
    assert weight_rows[0][0] == "q1"
    assert weight_rows[0][3] == "70.000"
    assert weight_rows[1][3] == "30.000"


def test_fuzzy_custom_weight_requires_weight_source():
    df = pd.DataFrame({"q1": [1, 2, 3], "q2": [3, 2, 1]})

    result = fuzzy_comprehensive_evaluation.run(
        df,
        {"variables": ["q1", "q2"], "weight_method": "custom"},
    )

    assert "自定义权重" in result["description"]
    assert result["rows"] == []
