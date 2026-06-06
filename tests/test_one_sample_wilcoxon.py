import pandas as pd

from backend.analysis.methods.one_sample_wilcoxon import METHOD_META, run


def test_one_sample_wilcoxon_test_value_accepts_free_numeric_input():
    test_value_option = next(option for option in METHOD_META["options"] if option["key"] == "test_value")

    assert test_value_option["type"] == "number"
    assert "choices" not in test_value_option


def test_one_sample_wilcoxon_outputs_spssau_style_batch_table():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 4, 4],
        "q2": [3, 3, 4, 4, 5, 5, 5],
    })

    result = run(df, {"test_vars": ["q1", "q2"], "test_value": "3", "auto_test_value": False, "output_normality": False})

    config_section = result["sections"][0]
    main_section = result["sections"][1]

    assert config_section["title"] == "分析配置"
    assert config_section["rows"][2] == ["检验值", "手动输入：统一检验值 3.000"]
    assert main_section["title"] == "输出结果1：单样本Wilcoxon分析结果"
    assert main_section["headers"] == [
        "名称",
        "样本量",
        "检验值",
        "25分位数",
        "中位数",
        "75分位数",
        "统计量Z值",
        "p",
    ]
    assert [row[0] for row in main_section["rows"]] == ["q1", "q2"]
    assert main_section["rows"][0][:6] == ["q1", "6", "3.000", "2.500", "4.000", "4.000"]
    assert main_section["rows"][1][:6] == ["q2", "5", "3.000", "3.500", "4.000", "5.000"]


def test_one_sample_wilcoxon_can_auto_select_test_value_per_variable():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 4, 4],
        "q2": [3, 3, 4, 4, 5, 5, 5],
    })

    result = run(df, {"test_vars": ["q1", "q2"], "auto_test_value": True, "output_normality": False})

    main_rows = result["sections"][1]["rows"]

    assert main_rows[0][2] == "3.286"
    assert main_rows[1][2] == "4.143"
    assert result["sections"][0]["rows"][2][1] == "自动选择：每个变量使用自身均值作为检验值"
    assert "自动按每个变量均值设置检验值" in result["sections"][1]["description"]


def test_one_sample_wilcoxon_keeps_legacy_single_variable_param():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 4, 4],
    })

    result = run(df, {"variable": "q1", "test_value": "3"})

    assert result["rows"][0][0] == "q1"


def test_one_sample_wilcoxon_can_append_normality_histograms():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 4, 4],
    })

    result = run(df, {
        "test_vars": ["q1"],
        "test_value": "3",
        "output_normality": True,
    })

    normality_section = result["sections"][2]
    chart_section = result["sections"][3]

    assert normality_section["title"] == "正态性检验结果"
    assert normality_section["headers"] == [
        "名称",
        "样本量",
        "平均值",
        "标准差",
        "S-W检验",
        "K-S检验",
    ]
    assert normality_section["rows"][0][:4] == ["q1", "7", "3.286", "1.380"]
    assert chart_section["title"] == "正态性检验直方图"
    assert chart_section["charts"][0]["chartType"] == "normality_histogram"


def test_one_sample_wilcoxon_defaults_to_combined_spssau_spsspro_output():
    df = pd.DataFrame({
        "q1": [1, 2, 3, 4, 5, 4, 4],
        "q2": [3, 3, 4, 4, 5, 5, 5],
    })

    result = run(df, {"test_vars": ["q1", "q2"]})

    assert result["sections"][0]["title"] == "分析配置"
    assert result["sections"][0]["rows"][2][1] == "自动选择：每个变量使用自身均值作为检验值"
    assert result["sections"][1]["title"] == "输出结果1：单样本Wilcoxon分析结果"
    assert result["sections"][2]["title"] == "正态性检验结果"
    assert result["sections"][3]["title"] == "正态性检验直方图"
    assert result["sections"][4]["title"] == "分析步骤"
