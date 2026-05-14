import pandas as pd

from backend.analysis.methods.one_sample_t_test import run


def test_one_sample_t_test_outputs_spssau_style_tables():
    df = pd.DataFrame({
        "q1_1": [1, 2, 3, 4, 5, 4, 4],
    })

    result = run(df, {"test_vars": ["q1_1"], "test_value": "3"})

    main_section = result["sections"][0]
    effect_section = result["sections"][3]

    assert main_section["title"] == "输出结果1：单样本T检验分析结果"
    assert main_section["headers"] == [
        "名称",
        "样本量",
        "最小值",
        "最大值",
        "平均值",
        "标准差",
        "t",
        "p",
    ]
    assert main_section["rows"][0][:6] == [
        "q1_1",
        "7",
        "1",
        "5",
        "3.286",
        "1.380",
    ]
    assert effect_section["title"] == "深入分析-效应量指标"
    assert effect_section["headers"] == [
        "名称",
        "平均值",
        "对比数字",
        "差值",
        "差值95% CI",
        "df",
        "标准差",
        "Cohen's d 值",
    ]
    assert effect_section["rows"][0][1:4] == ["3.286", "3.000", "0.286"]


def test_one_sample_t_test_can_append_normality_histograms():
    df = pd.DataFrame({
        "q1_1": [1, 2, 3, 4, 5, 4, 4],
    })

    result = run(df, {
        "test_vars": ["q1_1"],
        "test_value": "3",
        "output_normality": True,
    })

    normality_section = result["sections"][1]
    chart_section = result["sections"][2]

    assert normality_section["title"] == "正态性检验结果"
    assert normality_section["headers"] == [
        "名称",
        "样本量",
        "平均值",
        "标准差",
        "S-W检验",
        "K-S检验",
    ]
    assert normality_section["rows"][0][:4] == ["q1_1", "7", "3.286", "1.380"]
    assert chart_section["title"] == "正态性检验直方图"
    assert chart_section["charts"][0]["chartType"] == "normality_histogram"
