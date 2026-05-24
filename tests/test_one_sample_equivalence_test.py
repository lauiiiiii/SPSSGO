import pandas as pd

from backend.analysis.methods.one_sample_equivalence_test import run


def _section(result, title):
    return next(item for item in result["sections"] if item.get("title") == title)


def test_one_sample_equivalence_uses_scaled_target_bounds_and_spsspro_sections():
    values = [1.8, 1.9, 2.0, 2.1, 2.2] * 20
    result = run(pd.DataFrame({"q1": values}), {
        "variable": "q1",
        "target_value": "2",
        "lower": "-0.1",
        "upper": "0.1",
        "scale_by_target": True,
    })

    desc = _section(result, "输出结果1：描述性统计")
    ci = _section(result, "输出结果2：置信区间与等价限值比较")
    test = _section(result, "输出结果3：等价检验")
    chart = _section(result, "输出结果4：等价检验可视化")

    assert desc["headers"][:5] == ["变量", "N", "均值", "标准差", "均值标准误"]
    assert desc["rows"][0][0:3] == ["q1", "100", "2.000"]
    assert ci["rows"][0][3] == "(-0.200, 0.200)"
    assert test["headers"] == ["原假设", "自由度", "T值", "P值"]
    assert test["rows"][0][0] == "差值 ≤ -0.200"
    assert test["rows"][1][0] == "差值 ≥ 0.200"
    assert chart["charts"][0]["chartType"] == "equivalence_interval"


def test_one_sample_equivalence_supports_one_sided_alternative():
    result = run(pd.DataFrame({"q1": [3, 4, 5, 6, 7, 8]}), {
        "variable": "q1",
        "target_value": "4",
        "lower": "-1",
        "upper": "1",
        "scale_by_target": False,
        "alternative": "检验均值>目标值",
    })

    test = _section(result, "输出结果3：等价检验")
    assert test["rows"][0][0] == "差值 ≤ 0"
    assert "支持" in result["description"]
