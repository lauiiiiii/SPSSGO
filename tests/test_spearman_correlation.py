# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.methods import pearson_correlation, spearman_correlation


def test_spearman_entry_reuses_main_correlation_spearman_output():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4, 5, 6],
            "q2": [6, 5, 4, 3, 2, 1],
            "q3": [1, 1, 2, 2, 3, 3],
        }
    )
    params = {"variables": ["q1", "q2", "q3"]}

    result = spearman_correlation.run(df, params)
    expected = pearson_correlation.run(
        df,
        {
            **params,
            "correlation_method": "Spearman相关系数",
        },
    )

    assert result["name"] == "Spearman 等级相关"
    assert result["headers"] == expected["headers"]
    assert result["rows"] == expected["rows"]
    assert result["description"] == expected["description"]
    assert result["sections"] == expected["sections"]

    chart = result["sections"][1]["charts"][0]
    assert chart["chartType"] == "correlation_heatmap"
    assert chart["title"] == "Spearman相关系数热力图"


def test_spearman_entry_keeps_constant_variable_guard_from_main_correlation():
    df = pd.DataFrame(
        {
            "constant": [1, 1, 1, 1],
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
        }
    )

    result = spearman_correlation.run(df, {"variables": ["constant", "q1", "q2"]})

    assert result["name"] == "Spearman 等级相关"
    assert result["sections"][0]["rows"][0][5] == "—"
    assert result["sections"][0]["rows"][1][2] == "—"
