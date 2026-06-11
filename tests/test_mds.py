# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.methods import mds


def test_mds_raw_columns_build_distance_matrix_and_space_chart():
    df = pd.DataFrame(
        {
            "q4": [1, 2, 3],
            "q5": [2, 3, 4],
            "q6": [4, 3, 2],
        }
    )

    result = mds.run(
        df,
        {
            "variables": ["q4", "q5", "q6"],
            "data_format": "根据数据创建距离矩阵",
            "analysis_dimension": "按变量（列）",
        },
    )

    assert result["name"] == "多维尺度分析MDS"
    assert result["sections"][0]["title"] == "输出结果1：距离矩阵"
    assert result["sections"][0]["rows"][1][1] == "1.732"
    assert result["sections"][1]["title"] == "输出结果2：空间感知图"
    chart = result["sections"][1]["charts"][0]
    assert chart["chartType"] == "scatter_plot"
    assert chart["data"]["showLabels"] is True
    assert chart["data"]["showZeroCross"] is True
    assert chart["data"]["symmetricAxis"] is True
    assert [point["label"] for point in chart["data"]["points"]] == ["q4", "q5", "q6"]


def test_mds_distance_matrix_mode_accepts_lower_triangle_matrix():
    df = pd.DataFrame(
        {
            "q4": [0, 1, 2],
            "q5": [0, 0, 3],
            "q6": [0, 0, 0],
        }
    )

    result = mds.run(
        df,
        {
            "variables": ["q4", "q5", "q6"],
            "data_format": "数据为距离矩阵",
            "analysis_dimension": "按变量（列）",
        },
    )

    distance_rows = result["sections"][0]["rows"]
    assert distance_rows[1][1] == "1.000"
    assert distance_rows[2][1] == "2.000"
    assert distance_rows[2][2] == "3.000"
    assert result["sections"][3]["rows"][0] == ["数据格式", "数据为距离矩阵"]
