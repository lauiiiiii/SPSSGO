import pandas as pd

from backend.analysis.methods.wilcoxon_signed_rank_test import METHOD_META, run


def test_paired_wilcoxon_supports_spssau_style_multiple_pairs():
    df = pd.DataFrame({
        "q1": [1, 1, 2, 2, 3, 3],
        "q2": [3, 4, 4, 5, 5, 6],
        "q3": [2, 2, 3, 3, 4, 4],
        "q4": [2, 3, 4, 4, 5, 5],
    })

    result = run(df, {
        "var1": ["q1", "q2"],
        "var2": ["q3", "q4"],
        "output_normality": False,
    })

    config_section = result["sections"][0]
    main_section = result["sections"][1]

    assert config_section["title"] == "分析配置"
    assert config_section["rows"][2] == ["配对组数", "2"]
    assert main_section["title"] == "输出结果3：配对样本Wilcoxon分析结果"
    assert main_section["headers"] == [
        "名称",
        "配对1",
        "配对2",
        "中位数差值(配对1-配对2)",
        "统计量Z值",
        "p",
    ]
    assert [row[0] for row in main_section["rows"]] == ["q1配对q3", "q2配对q4"]
    assert main_section["rows"][0][1] == "2.000(1.250,2.750)"
    assert main_section["rows"][0][2] == "3.000(2.250,3.750)"
    assert main_section["rows"][0][3] == "-1.000"


def test_paired_wilcoxon_keeps_legacy_single_pair_params():
    df = pd.DataFrame({
        "before": [1, 2, 3, 4, 5],
        "after": [2, 3, 3, 5, 6],
    })

    result = run(df, {"var1": "before", "var2": "after", "output_normality": False})

    assert result["rows"][0][0] == "before配对after"


def test_paired_wilcoxon_outputs_normality_helpers_by_default():
    df = pd.DataFrame({
        "q1": [1, 1, 2, 2, 3, 3],
        "q3": [2, 2, 3, 3, 4, 4],
    })

    result = run(df, {"var1": ["q1"], "var2": ["q3"]})

    assert result["sections"][1]["title"] == "输出结果1：配对差值正态性检验结果"
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
    assert result["sections"][3]["title"] == "输出结果3：配对样本Wilcoxon分析结果"


def test_paired_wilcoxon_method_meta_is_aligned_multiple_input():
    assert [slot["type"] for slot in METHOD_META["slots"]] == ["multiple", "multiple"]
    assert METHOD_META["options"][0]["key"] == "output_normality"
