import pandas as pd

from backend.analysis.methods.independent_t_test import run


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_independent_t_test_outputs_spsspro_style_summary_for_same_column():
    df = pd.DataFrame({
        "group": [1, 1, 1, 1, 2, 2, 2, 2],
        "score": [10, 11, 12, 13, 15, 16, 17, 18],
    })

    result = run(df, {"group_var": "group", "test_vars": ["score"]})

    assert result["name"] == "独立样本T检验_group_score"
    assert _section(result, "输出结果1：正态性检验结果")["headers"] == [
        "变量名",
        "样本量",
        "中位数",
        "平均值",
        "标准差",
        "偏度",
        "峰度",
        "S-W检验",
        "K-S检验",
    ]
    assert _section(result, "输出结果3：方差齐性检验")["rows"][0][:4] == [
        "score",
        "1.291",
        "1.291",
        "0.000",
    ]
    final_table = _section(result, "输出结果5：独立样本T检验分析结果表")
    assert final_table["headers"] == [
        "变量名",
        "变量值",
        "样本量",
        "平均值",
        "标准差",
        "T检验",
        "Welch's T检验",
        "平均值差值",
        "Cohen's d值",
    ]
    assert final_table["rows"][0][:5] == ["score", "1", "4", "11.500", "1.291"]
    assert final_table["rows"][1][:5] == ["", "2", "4", "16.500", "1.291"]


def test_independent_t_test_supports_two_sample_columns():
    df = pd.DataFrame({
        "sample_a": [10, 11, 12, 13, None],
        "sample_b": [15, 16, 17, 18, 19],
    })

    result = run(df, {"data_format": "样本在不同列", "test_vars": ["sample_a", "sample_b"]})

    final_table = _section(result, "输出结果5：独立样本T检验分析结果表")
    assert result["name"] == "独立样本T检验_样本_sample_a / sample_b"
    assert final_table["rows"][0][:5] == ["sample_a / sample_b", "sample_a", "4", "11.500", "1.291"]
    assert final_table["rows"][1][:5] == ["", "sample_b", "5", "17.000", "1.581"]
