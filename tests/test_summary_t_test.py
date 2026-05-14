import pandas as pd

from backend.analysis.methods.summary_t_test import run


def _section(result, title):
    return next(item for item in result["sections"] if item.get("title") == title)


def test_summary_t_test_one_sample_matches_spssau_directional_hypothesis():
    result = run(pd.DataFrame(), {
        "test_type": "one_sample",
        "mean": 168,
        "std": 14,
        "n": 100,
        "test_value": 165,
        "confidence_level": "95",
        "alternative": "大于",
    })

    ci_row = _section(result, "单样本t检验置信区间")["rows"][0]
    test_row = _section(result, "单样本t检验假设检验")["rows"][0]

    assert ci_row == ["值", "100", "168.000", "14.000", "1.400", "165.222 ~ 170.778"]
    assert test_row[4:] == ["168.000>165.000", "2.143", "0.983", "95%", "假设成立"]


def test_summary_t_test_independent_uses_pooled_difference_ci():
    result = run(pd.DataFrame(), {
        "test_type": "independent",
        "group1_mean": 2,
        "group1_std": 2,
        "group1_n": 300,
        "group2_mean": 2,
        "group2_std": 3,
        "group2_n": 300,
        "diff_test_value": 0,
        "confidence_level": "95",
        "alternative": "等于",
    })

    ci_row = _section(result, "独立样本t检验差值置信区间")["rows"][0]
    test_row = _section(result, "独立样本t检验差值假设检验")["rows"][0]

    assert ci_row[-3:] == ["0.000", "0.208", "-0.409 ~ 0.409"]
    assert test_row == ["值", "0.000", "0.000", "0.000=0.000", "0.000", "1.000", "95%", "假设成立"]
