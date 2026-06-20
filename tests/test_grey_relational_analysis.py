# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import grey_relational_analysis


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_grey_relational_meta_matches_spsspro_slots_and_options():
    slot_keys = [slot["key"] for slot in grey_relational_analysis.METHOD_META["slots"]]
    assert slot_keys == ["feature_vars", "mother_var", "index_var"]

    sample = build_slot_param_example(grey_relational_analysis.METHOD_META)
    assert sample["dimensionless_method"] == "mean"
    assert sample["rho"] == 0.5
    assert sample["feature_vars"] == ["数值变量1", "数值变量2"]
    assert "灰色关联" in grey_relational_analysis.METHOD_META["aliases"]


def test_grey_relational_outputs_spsspro_granularity():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q2": [2, 3, 4, 5],
            "q3": [5, 4, 3, 2],
            "q4": [3, 4, 5, 6],
        }
    )

    result = grey_relational_analysis.run(
        df,
        {
            "feature_vars": ["q2", "q3"],
            "mother_var": ["q4"],
            "index_var": ["name"],
            "dimensionless_method": "mean",
            "rho": 0.5,
        },
    )

    assert result["headers"] == ["评价项", "关联度", "排名"]
    assert result["rows"][0][0] == "q2"
    assert float(result["rows"][0][1]) > float(result["rows"][1][1])
    assert "有效样本量 N=4" in result["description"]

    config_rows = _section(result, "算法配置")["rows"]
    assert ["特征序列", "q2、q3"] in config_rows
    assert ["母序列", "q4"] in config_rows
    assert ["索引项", "name"] in config_rows
    assert ["无量纲处理方式", "均值化"] in config_rows
    assert ["分辨系数ρ", "0.50"] in config_rows

    sample_rows = _section(result, "样本处理")["rows"]
    assert sample_rows == [["原始样本量", "4"], ["有效样本量", "4"], ["排除样本量", "0"]]
    assert "q2与q4的关联度" in _section(result, "分析结果")["content"]
    assert "分辨系数ρ=0.50" in _section(result, "分析步骤")["content"]

    coeff_table = _section(result, "输出结果1：灰色关联系数")
    assert coeff_table["headers"] == ["行索引", "q2", "q3"]
    assert coeff_table["rows"][0][0] == "A"

    coeff_chart = _section(result, "输出结果2：关联系数图")["charts"][0]
    assert coeff_chart["chartType"] == "metric_comparison"
    assert coeff_chart["data"]["multiSeries"] is True
    assert set(coeff_chart["data"]["metrics"].keys()) == {"q2", "q3"}

    grade_table = _section(result, "输出结果3：灰色关联度结果")
    assert grade_table["headers"] == result["headers"]
    assert grade_table["rows"] == result["rows"]

    chart = _section(result, "输出结果4：灰色关联度排序图")["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert chart["data"]["metric"] == "关联度"
    assert chart["data"]["labels"] == ["q2", "q3"]


def test_grey_relational_keeps_legacy_reference_and_compare_params():
    df = pd.DataFrame(
        {
            "q2": [2, 3, 4, 5],
            "q3": [5, 4, 3, 2],
            "q4": [3, 4, 5, 6],
        }
    )

    result = grey_relational_analysis.run(
        df,
        {
            "compare_vars": ["q2", "q3"],
            "reference_var": "q4",
            "dimensionless_method": "初值化",
        },
    )

    assert result["rows"]
    config_rows = _section(result, "算法配置")["rows"]
    assert ["特征序列", "q2、q3"] in config_rows
    assert ["母序列", "q4"] in config_rows
    assert ["无量纲处理方式", "初值化"] in config_rows


def test_grey_relational_rejects_invalid_rho_and_zero_initial_value():
    df = pd.DataFrame({"q1": [0, 1, 2], "q2": [1, 2, 3], "q3": [2, 3, 4]})

    invalid_rho = grey_relational_analysis.run(
        df,
        {"feature_vars": ["q2", "q3"], "mother_var": ["q1"], "rho": 1},
    )
    assert "分辨系数ρ必须" in invalid_rho["description"]

    zero_initial = grey_relational_analysis.run(
        df,
        {"feature_vars": ["q2", "q3"], "mother_var": ["q1"], "dimensionless_method": "initial"},
    )
    assert "初值化要求" in zero_initial["description"]


def test_grey_relational_coefficient_table_previews_15_rows_and_exports_all():
    df = pd.DataFrame(
        {
            "name": [f"S{index}" for index in range(1, 21)],
            "q2": list(range(2, 22)),
            "q3": list(range(21, 1, -1)),
            "q4": list(range(3, 23)),
        }
    )

    result = grey_relational_analysis.run(
        df,
        {
            "feature_vars": ["q2", "q3"],
            "mother_var": ["q4"],
            "index_var": ["name"],
        },
    )

    coeff_table = _section(result, "输出结果1：灰色关联系数")
    assert len(coeff_table["rows"]) == 15
    assert len(coeff_table["exportRows"]) == 20
    assert coeff_table["rows"][0][0] == "S1"
    assert coeff_table["rows"][-1][0] == "S15"
    assert coeff_table["exportRows"][-1][0] == "S20"
    assert "预览结果" in coeff_table["note"]
