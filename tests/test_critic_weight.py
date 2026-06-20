# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import critic_weight


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_critic_weight_meta_and_spssau_spsspro_granularity():
    assert critic_weight.METHOD_META["label"] == "CRITIC权重法"
    sample = build_slot_param_example(critic_weight.METHOD_META)
    assert sample["variables"] == ["数值变量1", "数值变量2"]
    assert sample["save_composite_score"] is False

    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [2, 4, 6, 8],
            "q3": [4, 3, 2, 1],
        }
    )

    result = critic_weight.run(df, {"variables": ["q1", "q2", "q3"]})

    assert result["headers"] == ["项", "指标变异性", "指标冲突性", "信息量", "权重(%)"]
    assert result["rows"] == [
        ["q1", "1.291", "2.000", "2.582", "20.000"],
        ["q2", "2.582", "2.000", "5.164", "40.000"],
        ["q3", "1.291", "4.000", "5.164", "40.000"],
    ]
    assert "有效样本量 N=4" in result["description"]
    assert "score_columns" not in result

    assert _section(result, "算法配置")["rows"] == [
        ["评价指标", "q1、q2、q3"],
        ["保存综合得分", "关闭"],
        ["变异性口径", "样本标准差"],
    ]
    assert _section(result, "样本处理")["rows"] == [
        ["原始样本量", "4"],
        ["有效样本量", "4"],
        ["排除样本量", "0"],
    ]
    assert "Σ(1-rjk)" in _section(result, "分析步骤")["content"]

    chart = _section(result, "输出结果2：指标重要度直方图")["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert chart["data"]["metric"] == "权重(%)"
    assert chart["data"]["labels"] == ["q2", "q3", "q1"]
    assert chart["data"]["values"] == [40.0, 40.0, 20.0]

    describe = _section(result, "输出结果3：描述统计")
    assert describe["headers"] == ["项", "样本量", "平均值", "标准差"]
    assert describe["rows"] == [
        ["q1", "4", "2.500", "1.291"],
        ["q2", "4", "5.000", "2.582"],
        ["q3", "4", "2.500", "1.291"],
    ]
    assert "q2 的权重最高" in _section(result, "详细结论")["content"]


def test_critic_weight_save_score_returns_full_length_column_with_missing_placeholder():
    df = pd.DataFrame(
        {
            "q1": [1, 2, None, 4],
            "q2": [2, 4, 6, 8],
            "q3": [4, 3, 2, 1],
        },
        index=[10, 20, 30, 40],
    )

    result = critic_weight.run(
        df,
        {
            "variables": ["q1", "q2", "q3"],
            "save_composite_score": True,
        },
    )

    score_columns = result["score_columns"]
    assert score_columns[0]["base_name"] == "CompScore_CRITIC权重法"
    assert len(score_columns[0]["values"]) == 4
    assert score_columns[0]["values"][2] is None
    assert _section(result, "算法配置")["rows"][1] == ["保存综合得分", "开启"]
    assert _section(result, "样本处理")["rows"] == [
        ["原始样本量", "4"],
        ["有效样本量", "3"],
        ["排除样本量", "1"],
    ]


def test_critic_weight_accepts_string_variable_param():
    df = pd.DataFrame({"q1": [1, 2, 3], "q2": [3, 2, 1]})

    result = critic_weight.run(df, {"variables": "q1"})

    assert result["headers"] == []
    assert "至少需要 2 个" in result["description"]
