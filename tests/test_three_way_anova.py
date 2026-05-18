import pandas as pd

from backend.analysis.methods.three_way_anova import run


def _sample_df():
    rows = []
    for a in ["A1", "A2"]:
        for b in ["B1", "B2", "B3"]:
            for c in ["C1", "C2"]:
                for rep in range(3):
                    rows.append({
                        "a": a,
                        "b": b,
                        "c": c,
                        "score": 1
                        + (a == "A2") * 0.6
                        + (b == "B2") * 0.2
                        + (b == "B3") * 0.5
                        + (c == "C2") * 0.3
                        + rep * 0.05,
                        "cov": rep,
                    })
    return pd.DataFrame(rows)


def test_three_way_anova_outputs_spssau_spsspro_style_sections():
    result = run(_sample_df(), {
        "factors": ["a", "b", "c"],
        "dependent": "score",
        "covariates": ["cov"],
        "include_interaction": True,
        "second_order_interaction": True,
        "third_order_interaction": True,
        "include_effect_size": True,
        "do_post_hoc": True,
        "post_hoc_method": "Tukey法",
    })

    main = result["sections"][0]
    assert main["title"] == "输出结果1：三因素方差分析结果"
    assert main["headers"] == ["差异源", "平方和", "df", "均方", "F", "p", "η²", "partial η²"]
    assert "R²" in main["note"]
    assert result["sections"][1]["title"] == "分析建议"
    row_names = [row[0] for row in main["rows"]]
    assert "a" in row_names
    assert "a * b" in row_names
    assert "a * b * c" in row_names
    assert "cov" in row_names

    chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：均值对比图")
    assert len(chart_section["charts"]) == 3
    assert all(chart["chartType"] == "metric_comparison" for chart in chart_section["charts"])
    assert any(section["title"] == "三因素均值对比" for section in result["sections"])
    post_hoc = next(section for section in result["sections"] if section["title"] == "输出结果3：事后多重比较结果")
    assert "tukey" in post_hoc["description"].lower()


def test_three_way_anova_can_skip_interactions_and_post_hoc():
    result = run(_sample_df(), {
        "factors": ["a", "b", "c"],
        "dependent": "score",
        "include_interaction": False,
        "do_post_hoc": False,
    })

    row_names = [row[0] for row in result["sections"][0]["rows"]]
    assert "a * b" not in row_names
    assert result["sections"][0]["headers"] == ["差异源", "平方和", "df", "均方", "F", "p"]
    assert any(section["title"] == "三因素均值对比" for section in result["sections"])
    assert not any(section["title"] == "输出结果3：事后多重比较结果" for section in result["sections"])
