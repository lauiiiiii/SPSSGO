import pandas as pd

from backend.analysis.methods.mann_whitney_u_test import METHOD_META, run


def test_mann_whitney_supports_numeric_binary_group_and_multiple_y():
    df = pd.DataFrame({
        "group": [0, 0, 0, 0, 1, 1, 1, 1],
        "q1": [1, 2, 2, 3, 4, 5, 5, 6],
        "q2": [2, 2, 3, 3, 3, 4, 4, 5],
    })

    result = run(df, {
        "group_var": "group",
        "test_vars": ["q1", "q2"],
        "output_normality": False,
    })

    config_section = result["sections"][0]
    main_section = result["sections"][1]

    assert config_section["title"] == "分析配置"
    assert config_section["rows"][2] == ["检验变量Y", "q1、q2"]
    assert main_section["title"] == "输出结果3：MannWhitney U检验分析结果"
    assert main_section["headers"] == [
        "名称",
        "组1",
        "组2",
        "组1秩均值",
        "组2秩均值",
        "U",
        "统计量Z值",
        "p",
        "Cohen's d",
    ]
    assert [row[0] for row in main_section["rows"]] == ["q1：0 vs 1", "q2：0 vs 1"]
    assert main_section["rows"][0][1] == "2.000(1.750,2.250)"
    assert main_section["rows"][0][2] == "5.000(4.750,5.250)"


def test_mann_whitney_keeps_legacy_test_var_param():
    df = pd.DataFrame({
        "group": ["A", "A", "B", "B"],
        "score": [1, 2, 5, 6],
    })

    result = run(df, {"group_var": "group", "test_var": "score", "output_normality": False})

    assert result["rows"][0][0] == "score：A vs B"


def test_mann_whitney_supports_chinese_group_labels():
    df = pd.DataFrame({
        "group": ["实验组", "实验组", "对照组", "对照组"],
        "score": [5, 6, 1, 2],
    })

    result = run(df, {"group_var": "group", "test_vars": ["score"], "output_normality": False})

    assert result["sections"][0]["rows"][3] == ["组别", "实验组、对照组"]
    assert "实验组" in result["description"]
    assert "对照组" in result["description"]


def test_mann_whitney_supports_more_than_two_groups_as_pairwise_tests():
    df = pd.DataFrame({
        "group": ["一组", "一组", "二组", "二组", "三组", "三组"],
        "score": [1, 2, 3, 4, 5, 6],
    })

    result = run(df, {"group_var": "group", "test_vars": ["score"], "output_normality": False})
    rows = result["sections"][1]["rows"]

    assert result["sections"][0]["rows"][4] == ["比较方式", "多组自动两两比较"]
    assert [row[0] for row in rows] == [
        "score：一组 vs 二组",
        "score：一组 vs 三组",
        "score：二组 vs 三组",
    ]


def test_mann_whitney_outputs_normality_helpers_by_default():
    df = pd.DataFrame({
        "group": [0, 0, 0, 1, 1, 1],
        "q1": [1, 2, 3, 4, 5, 6],
    })

    result = run(df, {"group_var": "group", "test_vars": ["q1"]})

    assert result["sections"][1]["title"] == "输出结果1：正态性检验结果"
    assert result["sections"][1]["headers"] == [
        "变量名",
        "样本量",
        "平均值",
        "标准差",
        "偏度",
        "峰度",
        "S-W检验",
        "K-S检验",
    ]
    assert result["sections"][2]["title"] == "输出结果2：正态性检验直方图"
    assert result["sections"][3]["title"] == "输出结果3：MannWhitney U检验分析结果"


def test_mann_whitney_meta_allows_encoded_group_and_multiple_y():
    group_slot = METHOD_META["slots"][0]
    y_slot = METHOD_META["slots"][1]

    assert group_slot["accept"] == "any"
    assert group_slot["acceptLabel"] == "定类"
    assert "自动两两比较" in group_slot["hint"]
    assert y_slot["type"] == "multiple"
