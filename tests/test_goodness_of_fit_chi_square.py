import pandas as pd

from backend.analysis.methods.goodness_of_fit_chi_square import METHOD_META, run


def test_goodness_of_fit_uses_expected_ratios_and_spsspro_result_table():
    df = pd.DataFrame({"q1": [1] * 60 + [2] * 35})

    result = run(df, {
        "variable": "q1",
        "expected_ratios": {"1": "50", "2": "50"},
    })

    assert METHOD_META["slots"][0]["key"] == "variable"
    assert METHOD_META["slots"][0]["label"] == "变量"
    assert result["name"] == "卡方拟合优度检验_q1"

    table = next(section for section in result["sections"] if section["title"] == "输出结果1：卡方拟合优度检验")
    assert table["headers"] == ["项", "实际频数", "期望频数", "实际比例", "期望比例", "残差", "χ²", "P"]
    assert table["headerRows"][0][1]["text"] == "卡方拟合优度检验"
    assert table["rows"][0] == ["1", "60", "47.500", "0.632", "0.500", "12.500", "6.579", "0.010**"]
    assert table["rows"][1] == ["2", "35", "47.500", "0.368", "0.500", "-12.500", "", ""]

    chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：期望频数图")
    chart = chart_section["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert chart["data"]["multiSeries"] is True
    assert chart["data"]["displayModes"] == [
        {"value": "bar", "label": "柱形图"},
        {"value": "line", "label": "折线图"},
    ]
    assert chart["data"]["metrics"]["实际频数"] == [60.0, 35.0]
    assert chart["data"]["metrics"]["期望频数"] == [47.5, 47.5]


def test_goodness_of_fit_defaults_to_equal_ratios_when_missing():
    df = pd.DataFrame({"q1": ["本科生"] * 87 + ["研究生"] * 13})

    result = run(df, {"variable": "q1"})

    table = next(section for section in result["sections"] if section["title"] == "输出结果1：卡方拟合优度检验")
    assert table["rows"][0][2] == "50.000"
    assert table["rows"][0][4] == "0.500"
    assert table["rows"][0][6] == "54.760"
