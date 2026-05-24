import pandas as pd

from backend.analysis.methods.paired_equivalence_test import run


def _section(result, title):
    return next(item for item in result["sections"] if item.get("title") == title)


def test_paired_equivalence_matches_spsspro_sections():
    df = pd.DataFrame({
        "before": [100.0, 101.0, 99.0, 100.5, 98.5, 101.5, 99.8, 100.2],
        "after": [100.1, 101.1, 99.1, 100.6, 98.6, 101.6, 99.9, 100.3],
    })
    result = run(df, {
        "test_var": "after",
        "reference_var": "before",
        "lower": "-0.2",
        "upper": "0.2",
        "scale_by_reference": False,
    })

    assert _section(result, "输出结果1：描述性统计")["headers"][:5] == ["变量", "N", "均值", "标准差", "均值标准误"]
    assert _section(result, "输出结果2：置信区间与等价限值比较")["headers"] == ["差值", "标准差", "SE", "对等项的 95% CI", "等价区间"]
    assert _section(result, "输出结果3：等价检验")["headers"] == ["原假设", "自由度", "T值", "P值"]
    assert _section(result, "输出结果4：等价检验可视化")["charts"][0]["chartType"] == "equivalence_interval"


def test_paired_equivalence_accepts_legacy_var_keys():
    df = pd.DataFrame({
        "q1": [1.1, 1.2, 1.0, 1.3, 1.2],
        "q4": [1.0, 1.1, 1.0, 1.2, 1.1],
    })
    result = run(df, {"var1": "q1", "var2": "q4", "lower": "-0.5", "upper": "0.5"})

    rows = _section(result, "输出结果1：描述性统计")["rows"]
    assert [row[0] for row in rows] == ["q1", "q4", "q1 - q4"]
