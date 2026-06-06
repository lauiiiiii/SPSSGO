import pandas as pd

from backend.analysis.methods.friedman_test import METHOD_META, run


def test_friedman_accepts_scale_like_variables_and_outputs_main_sections():
    df = pd.DataFrame({
        "q1": ["1", "2", "3", "4", "5"],
        "q2": ["2", "3", "4", "5", "5"],
        "q3": ["3", "4", "5", "5", "5"],
    })

    result = run(df, {"variables": ["q1", "q2", "q3"], "output_normality": False, "pairwise_compare": False})

    config_section = result["sections"][0]
    desc_section = result["sections"][1]
    chart_section = result["sections"][2]
    main_section = result["sections"][3]

    assert config_section["title"] == "分析配置"
    assert config_section["rows"][1] == ["变量", "q1、q2、q3"]
    assert desc_section["title"] == "输出结果3：Friedman检验描述统计"
    assert desc_section["headers"] == ["名称", "样本量", "平均值", "标准差", "中位数M(P25，P75)", "平均秩"]
    assert [row[0] for row in desc_section["rows"]] == ["q1", "q2", "q3"]
    assert chart_section["title"] == "输出结果4：差异可视化图"
    assert main_section["title"] == "输出结果5：Friedman检验结果"
    assert main_section["headers"] == ["样本量", "变量个数", "χ²", "df", "p", "Kendall's W", "差异幅度"]


def test_friedman_outputs_normality_and_pairwise_by_default():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 6],
        "q2": [2, 3, 4, 5, 6, 7],
        "q3": [3, 4, 5, 6, 7, 8],
    })

    result = run(df, {"variables": ["q1", "q2", "q3"]})

    assert result["sections"][1]["title"] == "输出结果1：正态性检验结果"
    assert result["sections"][2]["title"] == "输出结果2：正态性检验直方图"
    assert result["sections"][6]["title"] == "输出结果6：两两比较结果"
    assert len(result["sections"][6]["rows"]) == 3


def test_friedman_method_meta_allows_detected_categorical_scale_items():
    slot = METHOD_META["slots"][0]

    assert slot["accept"] == "any"
    assert slot["acceptLabel"] == "定量"
    assert slot["min"] == 3
