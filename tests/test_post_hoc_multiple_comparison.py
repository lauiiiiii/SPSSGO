import pandas as pd

from backend.analysis.methods.post_hoc_multiple_comparison import POST_HOC_METHODS, run


def test_post_hoc_multiple_comparison_outputs_spssau_spsspro_style_sections():
    df = pd.DataFrame({
        "group": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        "score_a": [1, 2, 1, 3, 3, 4, 6, 6, 7],
        "score_b": [2, 2, 3, 3, 4, 4, 4, 5, 5],
    })

    result = run(df, {
        "group_var": "group",
        "test_vars": ["score_a", "score_b"],
        "method": "LSD",
        "use_letters": True,
    })

    assert result["sections"][0]["title"] == "分析步骤"
    assert result["sections"][1]["title"] == "输出结果1：方差分析结果"
    assert result["sections"][1]["headers"] == ["名称", "1", "2", "3", "F", "p"]
    assert result["sections"][1]["rows"][0][0] == "score_a"
    assert "±" in result["sections"][1]["rows"][0][1]

    chart_section = result["sections"][2]
    assert chart_section["title"] == "输出结果2：方差分析对比图"
    assert [chart["title"] for chart in chart_section["charts"]] == [
        "group和score_a事后多重比较对比图",
        "group和score_b事后多重比较对比图",
        "group和所有项分析对比",
    ]
    assert chart_section["charts"][0]["chartType"] == "metric_comparison"
    assert "metrics" not in chart_section["charts"][0]["data"]
    assert sorted(chart_section["charts"][2]["data"]["metrics"].keys()) == ["score_a", "score_b"]
    assert chart_section["charts"][2]["data"]["multiSeries"] is True

    comparison_section = result["sections"][3]
    assert comparison_section["title"] == "输出结果3：事后多重比较结果"
    assert comparison_section["headers"] == [
        "名称",
        "(I)名称",
        "(J)名称",
        "(I)平均值",
        "(J)平均值",
        "差值(I-J)",
        "标准误",
        "p",
    ]
    assert len(comparison_section["rows"]) == 6
    assert result["sections"][4]["title"] == "深入分析：字母标记法"
    assert result["sections"][5]["title"] == "智能分析"


def test_post_hoc_multiple_comparison_supports_all_declared_methods():
    df = pd.DataFrame({
        "group": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
        "score": [1, 2, 1, 2, 3, 2, 4, 4, 5, 6, 5, 6],
    })

    for method in POST_HOC_METHODS:
        result = run(df, {"group_var": "group", "test_vars": ["score"], "method": method})
        assert result["sections"][3]["title"] == "输出结果3：事后多重比较结果"
        assert len(result["sections"][3]["rows"]) == 6


def test_post_hoc_multiple_comparison_keeps_legacy_single_test_var_params():
    df = pd.DataFrame({
        "group": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        "score": [1, 2, 1, 3, 3, 4, 6, 6, 7],
    })

    result = run(df, {"group_var": "group", "test_var": "score", "method": "Bonferroni"})

    assert result["sections"][1]["rows"][0][0] == "score"
    assert "Bonferroni校正" in result["sections"][3]["description"]
