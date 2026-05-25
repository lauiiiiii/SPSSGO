import pandas as pd

from backend.analysis.methods.paired_t_test import run


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_paired_t_test_outputs_spssau_spsspro_style_multi_pair_tables():
    df = pd.DataFrame({
        "q1": [1, 2, 2, 3, 1, 2],
        "q2": [4, 5, 4, 5, 4, 5],
        "q3": [2, 4, 3, 5, 2, 4],
        "q4": [3, 4, 4, 4, 3, 4],
    })

    result = run(df, {"var1": ["q1", "q2"], "var2": ["q3", "q4"]})

    assert result["name"] == "配对样本T检验_q1-q3_q2-q4"
    normality = _section(result, "输出结果1：配对差值正态性检验结果")
    assert normality["headers"] == ["变量名", "样本量", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"]
    assert normality["rows"][0][:4] == ["q1配对q3", "6", "-1.500", "0.548"]

    final_table = _section(result, "输出结果3：配对样本T检验结果")
    assert final_table["headers"] == ["配对变量", "配对1", "配对2", "配对差值（配对1-配对2）", "t", "df", "P", "Cohen's d"]
    assert final_table["rows"][1][0] == "q2配对q4"
    assert final_table["rows"][1][5] == "5"

    effect_table = _section(result, "深入分析-效应量指标")
    assert effect_table["headers"] == ["名称", "平均值差值", "差值95% CI", "df", "差值标准差", "Cohen's d值"]
    assert effect_table["rows"][1][0] == "q2配对q4"


def test_paired_t_test_accepts_legacy_single_variable_params():
    df = pd.DataFrame({
        "before": [10, 11, 12, 13, 14],
        "after": [12, 12, 13, 14, 15],
    })

    result = run(df, {"var1": "before", "var2": "after"})

    final_table = _section(result, "输出结果3：配对样本T检验结果")
    assert final_table["rows"][0][0] == "before配对after"
    assert final_table["rows"][0][5] == "4"
