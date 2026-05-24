import pandas as pd

from backend.analysis.methods.two_sample_equivalence_test import run


def _section(result, title):
    return next(item for item in result["sections"] if item.get("title") == title)


def test_two_sample_equivalence_same_column_matches_spsspro_sections():
    df = pd.DataFrame({
        "group": [1] * 20 + [2] * 20,
        "score": [10.0, 10.1, 9.9, 10.2, 9.8] * 4 + [10.02, 10.12, 9.92, 10.22, 9.82] * 4,
    })
    result = run(df, {
        "test_var": "score",
        "group_var": "group",
        "reference_level": "2",
        "data_format": "样本在同一列",
        "lower": "-0.1",
        "upper": "0.1",
        "scale_by_reference": True,
    })

    assert _section(result, "输出结果1：描述性统计")["headers"][:5] == ["变量", "N", "均值", "标准差", "均值标准误"]
    assert _section(result, "输出结果2：置信区间与等价限值比较")["headers"] == ["差值", "SE", "对等项的 95% CI", "等价区间"]
    assert _section(result, "输出结果3：等价检验")["headers"] == ["原假设", "自由度", "T值", "P值"]
    assert _section(result, "输出结果4：等价检验可视化")["charts"][0]["chartType"] == "equivalence_interval"


def test_two_sample_equivalence_different_columns():
    df = pd.DataFrame({
        "fast": [1.2, 1.1, 1.3, 1.2, 1.25, 1.15],
        "standard": [1.18, 1.12, 1.28, 1.19, 1.24, 1.14],
    })
    result = run(df, {
        "test_var": "fast",
        "reference_var": "standard",
        "data_format": "样本在不同列",
        "lower": "-0.2",
        "upper": "0.2",
        "scale_by_reference": False,
    })

    desc_rows = _section(result, "输出结果1：描述性统计")["rows"]
    assert [row[0] for row in desc_rows] == ["fast", "standard"]
    assert "均值(fast)" in _section(result, "输出结果2：置信区间与等价限值比较")["rows"][1][0]
