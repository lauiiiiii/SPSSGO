import pandas as pd

from backend.analysis.methods.cochrans_q_test import METHOD_META, run


def test_cochrans_q_requires_binary_variables():
    df = pd.DataFrame({
        "q1": [0, 1, 2, 0],
        "q2": [0, 1, 0, 1],
        "q3": [1, 0, 1, 0],
    })

    result = run(df, {"variables": ["q1", "q2", "q3"]})

    assert result["description"] == "类别数量必须为2项！"


def test_cochrans_q_outputs_spss_style_tables_and_chart():
    rows = (
        [[1, 1, 1]] * 8
        + [[0, 0, 0]]
        + [[1, 0, 0]] * 2
        + [[0, 1, 0]] * 3
        + [[0, 0, 1]] * 3
        + [[0, 1, 1]] * 10
        + [[1, 0, 1]] * 10
        + [[1, 1, 0]] * 13
    )
    df = pd.DataFrame(rows, columns=["q8_1", "q8_2", "q8_3"])

    result = run(df, {"variables": ["q8_1", "q8_2", "q8_3"]})

    assert METHOD_META["slots"][0]["label"] == "变量"
    assert result["name"] == "Cochran's Q检验_q8_1_q8_2_q8_3"

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Cochran's Q 检验")
    assert main["headerRows"][0][1]["text"] == "频数百分比"
    assert main["rows"][0][0:3] == ["q8_1", "33", "17"]
    assert main["rows"][0][3]["text"] == "50"
    assert main["rows"][0][4]["text"] == "0.341"
    assert main["rows"][0][5]["text"] == "2"
    assert main["rows"][0][6]["text"] == "0.843"

    freq = next(section for section in result["sections"] if section["title"] == "频数分析结果")
    assert freq["rows"][0] == ["q8_1", "33", "17", "66.000%", "34.000%"]

    chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：频数分析堆叠图")
    chart = chart_section["charts"][0]
    assert chart["chartType"] == "crosstab_distribution"
    assert chart["data"]["groupLabels"] == ["q8_1", "q8_2", "q8_3"]
    assert chart["data"]["xLabels"] == ["1", "0"]
    assert chart["data"]["matrix"] == [[33, 34, 31], [17, 16, 19]]
    assert chart["data"]["displayModes"] == [
        {"value": "stackedColumn", "label": "堆积柱形图"},
        {"value": "column", "label": "柱形图"},
        {"value": "stackedBar", "label": "堆积条形图"},
        {"value": "bar", "label": "条形图"},
    ]
