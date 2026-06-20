# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.methods import data_envelopment_analysis


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_dea_bcc_outputs_spssau_spsspro_granularity():
    df = pd.DataFrame(
        {
            "unit": ["A", "B", "C", "D"],
            "x1": [1, 2, 3, 4],
            "x2": [2, 2, 3, 5],
            "y1": [1, 2, 2, 4],
        }
    )

    result = data_envelopment_analysis.run(
        df,
        {"input_vars": ["x1", "x2"], "output_vars": ["y1"], "index_var": ["unit"]},
    )

    assert result["headers"] == ["决策单元", "技术效益", "规模效益", "综合效益", "松弛变量S-", "松弛变量S+", "有效性"]
    assert result["rows"][0][0] == "A"
    assert "有效样本量 N=4" in result["description"]
    assert _section(result, "输出结果1：效益分析表")["headers"] == result["headers"]
    chart = _section(result, "输出结果2：效益有效性分析")["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert set(chart["data"]["metrics"]) == {"技术效益", "规模效益", "综合效益"}
    assert _section(result, "输出结果3：规模报酬分析")["headers"] == [
        "决策单元",
        "CCR综合效益",
        "BCC技术效益",
        "规模效益",
        "λ合计",
        "规模报酬",
    ]
    assert _section(result, "输出结果4：松弛变量分析")["headers"] == ["决策单元", "S-(x1)", "S-(x2)", "S+(y1)"]


def test_dea_non_negative_translation_keeps_model_running():
    df = pd.DataFrame(
        {
            "x1": [-1, 0, 1, 2],
            "y1": [1, 2, 3, 4],
        }
    )

    result = data_envelopment_analysis.run(
        df,
        {"input_vars": ["x1"], "output_vars": ["y1"], "non_negative_translation": True},
    )

    translation = _section(result, "非负平移处理")
    assert translation["rows"][0][0] == "x1"
    assert result["rows"]


def test_dea_save_efficiency_returns_full_length_score_column():
    df = pd.DataFrame(
        {
            "x1": [1, 2, None, 4],
            "y1": [1, 2, 3, 4],
        }
    )

    result = data_envelopment_analysis.run(
        df,
        {"input_vars": ["x1"], "output_vars": ["y1"], "save_efficiency": True},
    )

    score_columns = result["score_columns"]
    assert score_columns[0]["base_name"] == "DEA_综合效益"
    assert len(score_columns[0]["values"]) == 4
    assert score_columns[0]["values"][2] is None


def test_dea_ccr_outputs_compact_efficiency_table():
    df = pd.DataFrame(
        {
            "x1": [1, 2, 3, 4],
            "y1": [1, 1, 2, 3],
        }
    )

    result = data_envelopment_analysis.run(
        df,
        {"input_vars": ["x1"], "output_vars": ["y1"], "dea_type": "CCR"},
    )

    assert result["headers"] == ["决策单元", "综合效益", "松弛变量S-", "松弛变量S+", "有效性"]
    chart = _section(result, "输出结果2：效益有效性分析")["charts"][0]
    assert set(chart["data"]["metrics"]) == {"综合效益"}
    assert _section(result, "输出结果3：规模报酬分析")["headers"] == ["决策单元", "综合效益", "λ合计", "规模报酬"]
