import numpy as np
import pandas as pd

from backend.analysis.methods.manova import run


def _sample_df():
    rng = np.random.default_rng(7)
    rows = []
    for group in ["A", "B", "C"]:
        for phase in ["pre", "post"]:
            for index in range(12):
                baseline = rng.normal()
                group_shift = {"A": 0.0, "B": 0.8, "C": 1.4}[group]
                phase_shift = 0.5 if phase == "post" else 0.0
                rows.append({
                    "group": group,
                    "phase": phase,
                    "baseline": baseline,
                    "y1": 2 + group_shift + 0.3 * baseline + rng.normal(scale=0.4),
                    "y2": 4 + phase_shift + 0.2 * baseline + rng.normal(scale=0.5),
                })
    return pd.DataFrame(rows)


def test_manova_outputs_multivariate_and_between_subject_sections():
    result = run(_sample_df(), {
        "dependent_vars": ["y1", "y2"],
        "group_var": ["group", "phase"],
        "covariates": ["baseline"],
    })

    assert result["headers"] == ["项", "检验方法", "统计值", "F", "P"]
    assert "group" in [row[0] for row in result["rows"]]
    assert "phase" in [row[0] for row in result["rows"]]
    assert [section["title"] for section in result["sections"]] == [
        "分析步骤",
        "输出结果1：多变量检验",
        "智能分析",
        "输出结果2：主体间效应检验",
        "参考文献",
    ]

    subject = result["sections"][3]
    assert subject["headers"] == ["项", "因变量", "平方和", "自由度", "均方", "F", "P"]
    subject_terms = [row[0] for row in subject["rows"]]
    assert "group" in subject_terms
    assert "phase" in subject_terms
    assert "baseline" in subject_terms
    assert "样本缺失情况汇总" not in [section["title"] for section in result["sections"]]


def test_manova_requires_two_dependent_variables():
    result = run(_sample_df(), {
        "dependent_vars": ["y1"],
        "group_var": ["group"],
    })

    assert "至少需要 2 个" in result["description"]
