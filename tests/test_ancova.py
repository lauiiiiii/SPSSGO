import pandas as pd

from backend.analysis.methods.ancova import run


def test_ancova_outputs_spss_style_sections_and_adjusted_means():
    df = pd.DataFrame({
        "group": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C"],
        "score": [5.1, 6.0, 6.8, 8.2, 6.9, 8.1, 8.7, 10.2, 9.2, 9.8, 11.3, 11.7],
        "baseline": [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4],
    })

    result = run(df, {
        "group_var": "group",
        "dependent": "score",
        "covariates": ["baseline"],
        "include_effect_size": True,
        "do_post_hoc": True,
        "post_hoc_method": "Bonferroni校正",
    })

    assert result["headers"] == ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²", "偏η²"]
    assert [row[0] for row in result["rows"]] == ["截距", "group", "baseline", "误差"]
    assert result["rows"][0][6]
    assert result["rows"][1][-1]
    assert [section["title"] for section in result["sections"]] == [
        "分析步骤",
        "输出结果1：主体间效应检验",
        "智能分析",
        "输出结果2：协方差分析调整均值（group）",
        "group调整均值对比图",
        "输出结果3：group事后多重比较结果",
        "参考文献",
    ]

    adjusted = result["sections"][3]
    assert adjusted["headers"] == ["group", "平均值", "标准误差", "95%置信区间下限", "95%置信区间上限"]
    assert len(adjusted["rows"]) == 3


def test_ancova_accepts_multiple_group_variables_without_default_missing_table():
    df = pd.DataFrame({
        "group": ["A", "A", "A", "A", "B", "B", "B", "B", "A", "A", "B", "B"],
        "phase": ["pre", "pre", "post", "post", "pre", "pre", "post", "post", "pre", "post", "pre", "post"],
        "score": [5.1, 6.0, 7.2, 8.2, 6.9, 8.1, 9.0, 10.2, 5.8, 7.7, 7.4, 9.8],
        "baseline": [1, 2, 3, 4, 1, 2, 3, 4, 2, 3, 2, 3],
    })

    result = run(df, {
        "group_var": ["group", "phase"],
        "dependent": "score",
        "covariates": ["baseline"],
        "do_post_hoc": True,
    })

    row_names = [row[0] for row in result["rows"]]
    assert "group" in row_names
    assert "phase" in row_names
    titles = [section["title"] for section in result["sections"]]
    assert "输出结果2：协方差分析调整均值（group）" in titles
    assert "输出结果2：协方差分析调整均值（phase）" in titles
    assert "样本缺失情况汇总" not in titles


def test_ancova_parallelism_option_adds_group_covariate_interaction():
    df = pd.DataFrame({
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
        "score": [5.0, 5.8, 6.7, 7.9, 6.1, 7.7, 9.2, 10.8],
        "baseline": [1, 2, 3, 4, 1, 2, 3, 4],
    })

    result = run(df, {
        "group_var": "group",
        "dependent": "score",
        "covariates": ["baseline"],
        "include_interaction": True,
    })

    assert "group*baseline" in [row[0] for row in result["rows"]]
