import pandas as pd

from backend.analysis.methods.kruskal_wallis_test import METHOD_META, run


def test_kruskal_supports_multiple_y_and_outputs_main_sections():
    df = pd.DataFrame({
        "group": ["一组"] * 4 + ["二组"] * 4 + ["三组"] * 4,
        "q1": [1, 2, 2, 3, 4, 5, 5, 6, 7, 8, 8, 9],
        "q2": [2, 2, 3, 3, 3, 4, 4, 5, 6, 6, 7, 7],
    })

    result = run(df, {
        "group_var": "group",
        "test_vars": ["q1", "q2"],
        "output_normality": False,
        "pairwise_compare": False,
    })

    config_section = result["sections"][0]
    desc_section = result["sections"][1]
    chart_section = result["sections"][2]
    main_section = result["sections"][3]

    assert config_section["title"] == "分析配置"
    assert config_section["rows"][2] == ["检验变量Y", "q1、q2"]
    assert config_section["rows"][3] == ["组别", "一组、二组、三组"]
    assert desc_section["title"] == "输出结果3：分组描述统计"
    assert desc_section["headers"] == ["变量名", "组别", "样本量", "平均值", "标准差", "中位数M(P25，P75)", "平均秩"]
    assert chart_section["title"] == "输出结果4：差异可视化图"
    assert chart_section["charts"][0]["data"]["fullRow"] is True
    assert chart_section["charts"][1]["chartType"] == "grouped_boxplot"
    assert main_section["title"] == "输出结果5：Kruskal-Wallis检验结果"
    assert main_section["headers"] == ["变量名", "样本量", "组别数", "H", "df", "p", "ε²", "差异幅度"]
    assert [row[0] for row in main_section["rows"]] == ["q1", "q2"]


def test_kruskal_keeps_legacy_test_var_param_and_outputs_pairwise():
    df = pd.DataFrame({
        "group": [0, 0, 1, 1, 2, 2],
        "score": [1, 2, 3, 4, 5, 6],
    })

    result = run(df, {"group_var": "group", "test_var": "score", "output_normality": False})

    assert result["rows"][0][0] == "score"
    assert result["sections"][4]["title"] == "输出结果6：两两比较结果"
    assert [row[0] for row in result["sections"][4]["rows"]] == [
        "score：0 vs 1",
        "score：0 vs 2",
        "score：1 vs 2",
    ]


def test_kruskal_does_not_require_three_group_levels():
    df = pd.DataFrame({
        "group": ["A", "A", "A", "B", "B", "B"],
        "score": [1, 2, 3, 4, 5, 6],
    })

    result = run(df, {
        "group_var": "group",
        "test_vars": ["score"],
        "output_normality": False,
        "pairwise_compare": False,
    })

    assert result["sections"][0]["rows"][3] == ["组别", "A、B"]
    assert result["rows"][0][0] == "score"
    assert result["rows"][0][2] == "2"


def test_kruskal_outputs_normality_helpers_by_default():
    df = pd.DataFrame({
        "group": ["A", "A", "B", "B", "C", "C"],
        "q1": [1, 2, 3, 4, 5, 6],
    })

    result = run(df, {"group_var": "group", "test_vars": ["q1"]})

    assert result["sections"][1]["title"] == "输出结果1：正态性检验结果"
    assert result["sections"][2]["title"] == "输出结果2：正态性检验直方图"
    assert result["sections"][6]["title"] == "输出结果6：两两比较结果"


def test_kruskal_meta_allows_encoded_group_and_multiple_y():
    group_slot = METHOD_META["slots"][0]
    y_slot = METHOD_META["slots"][1]

    assert group_slot["accept"] == "any"
    assert group_slot["acceptLabel"] == "定类"
    assert group_slot["hint"] == "请输入分组变量"
    assert y_slot["type"] == "multiple"
    assert y_slot["min"] == 1
    assert y_slot["hint"] == "请输入变量"
