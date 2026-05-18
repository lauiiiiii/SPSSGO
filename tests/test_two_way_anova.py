import pandas as pd

from backend.analysis.methods.two_way_anova import run


def test_two_way_anova_outputs_spssau_spsspro_style_sections():
    df = pd.DataFrame({
        "factor_a": ["A", "A", "A", "B", "B", "B", "A", "B", "A", "B", "A", "B"],
        "factor_b": ["X", "Y", "X", "Y", "X", "Y", "Y", "X", "X", "Y", "Y", "X"],
        "score": [1, 2, 1.5, 4, 3.2, 4.5, 2.2, 3.1, 1.2, 4.8, 2.1, 3.5],
        "cov": [1, 2, 1, 2, 1, 2, 3, 1, 2, 3, 1, 2],
    })

    result = run(df, {
        "factors": ["factor_a", "factor_b"],
        "dependent": "score",
        "covariates": ["cov"],
        "include_interaction": True,
        "do_post_hoc": True,
        "post_hoc_method": "LSD",
    })

    assert result["sections"][0]["title"] == "分析步骤"
    main_section = result["sections"][1]
    assert main_section["title"] == "输出结果1：双因素方差分析结果"
    assert main_section["headers"] == ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"]
    assert [row[0] for row in main_section["rows"]] == ["factor_a", "factor_b", "factor_a * factor_b", "cov", "误差"]
    assert main_section["rows"][0][-2]

    chart_section = result["sections"][3]
    assert chart_section["title"] == "输出结果2：均值对比图"
    assert chart_section["charts"][0]["chartType"] == "metric_comparison"
    assert chart_section["charts"][0]["data"]["multiSeries"] is True

    assert result["sections"][4]["title"] == "factor_a和factor_b的均值对比(平均值±标准差)"
    assert result["sections"][5]["title"] == "样本缺失情况汇总"
    assert result["sections"][6]["title"] == "输出结果3：事后多重比较结果"


def test_two_way_anova_can_skip_interaction_and_post_hoc():
    df = pd.DataFrame({
        "factor_a": ["A", "A", "B", "B", "A", "B", "A", "B"],
        "factor_b": ["X", "Y", "X", "Y", "X", "Y", "Y", "X"],
        "score": [1, 2, 3, 4, 1.2, 4.2, 2.1, 3.1],
    })

    result = run(df, {
        "factor1": "factor_a",
        "factor2": "factor_b",
        "dependent": "score",
        "include_interaction": False,
        "do_post_hoc": False,
    })

    main_rows = result["sections"][1]["rows"]
    assert "factor_a * factor_b" not in [row[0] for row in main_rows]
    assert not any(section["title"] == "输出结果3：事后多重比较结果" for section in result["sections"])
