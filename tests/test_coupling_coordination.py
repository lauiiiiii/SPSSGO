# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import coupling_coordination


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def _has_section(result, title):
    return any(section["title"] == title for section in result["sections"])


def test_coupling_meta_uses_au_pro_combined_controls():
    weight_slot = next(slot for slot in coupling_coordination.METHOD_META["slots"] if slot["key"] == "weight_var")
    assert weight_slot["visible_if"] == {"weight_method": "custom"}
    assert "耦合协调度分析" in coupling_coordination.METHOD_META["aliases"]

    sample = build_slot_param_example(coupling_coordination.METHOD_META)
    assert "weight_var" not in sample
    assert sample["weight_method"] == "equal"
    assert sample["data_intervalization"] is True
    assert sample["save_process"] is False


def test_coupling_outputs_spssau_spsspro_granularity():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [80, 90, 70, 95],
            "q2": [8, 6, 9, 5],
            "q3": [30, 40, 35, 45],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q3"],
            "negative_vars": ["q2"],
            "label_vars": ["name"],
            "weight_method": "entropy",
        },
    )

    assert result["headers"] == ["项", "耦合度C值", "协调指数T值", "耦合协调度D值", "协调等级", "耦合协调程度"]
    assert len(result["rows"]) == 4
    assert result["rows"][0][0] == "A"
    assert "指标权重为熵权法" in result["description"]
    assert ["负向指标", "q2"] in _section(result, "算法配置")["rows"]
    assert ["协调指数T", "按指标权重计算"] in _section(result, "算法配置")["rows"]
    assert ["数据区间化", "是"] in _section(result, "算法配置")["rows"]
    assert _section(result, "指标权重计算")["headers"] == ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    assert "区分作用相对更强" in _section(result, "指标权重计算")["description"]
    assert not _has_section(result, "样本处理")
    assert _section(result, "输出结果1：耦合协调度计算结果")["headers"] == result["headers"]
    assert "D 值最高" in _section(result, "输出结果1：耦合协调度计算结果")["description"]

    chart = _section(result, "输出结果2：耦合协调度图")["charts"][0]
    assert chart["chartType"] == "metric_comparison"
    assert chart["data"]["multiSeries"] is True
    assert list(chart["data"]["metrics"].keys()) == ["耦合度C值", "协调指数T值", "耦合协调度D值"]

    grade_rules = _section(result, "输出结果3：耦合协调度等级划分")
    assert len(grade_rules["rows"]) == 10
    assert grade_rules["rows"][0] == ["1", "0 ≤ D < 0.1", "极度失调"]
    assert grade_rules["rows"][-1] == ["10", "0.9 ≤ D ≤ 1.0", "优质协调"]
    grade_summary = _section(result, "输出结果4：耦合协调度等级汇总")
    assert grade_summary["headers"] == ["协调等级", "耦合协调程度", "频数", "占比"]
    assert "等级汇总结果显示" in grade_summary["description"]
    assert all(section.get("description") for section in result["sections"] if section["type"] == "table")
    assert "论文写作中" in _section(result, "结果解释")["content"]
    refs = _section(result, "参考文献")["items"]
    assert len(refs) == 8
    assert any("廖重斌" in ref for ref in refs)
    assert any("Haken H" in ref for ref in refs)
    assert any("Shannon C E" in ref for ref in refs)


def test_coupling_accepts_coordination_index_variable():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
            "t": [0.2, 0.4, 0.6, 0.8],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "coordination_index_var": ["t"],
            "label_vars": ["name"],
            "data_intervalization": False,
        },
    )

    assert ["协调指数T", "t"] in _section(result, "算法配置")["rows"]
    assert ["数据区间化", "否"] in _section(result, "算法配置")["rows"]
    assert "协调指数T变量" in _section(result, "指标权重计算")["description"]
    assert result["rows"][0][2] == "0.200000"
    assert result["rows"][-1][2] == "0.800000"


def test_coupling_outputs_sample_processing_only_when_missing_analysis_enabled():
    df = pd.DataFrame(
        {
            "q1": [1, 2, None, 4],
            "q2": [4, 3, 2, 1],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "include_missing_analysis": True,
        },
    )

    sample_section = _section(result, "样本处理")
    assert sample_section["rows"] == [
        ["原始样本量", "4"],
        ["有效样本量", "3"],
        ["排除样本量", "1"],
    ]


def test_coupling_rejects_raw_scale_as_coordination_index():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
            "raw_t": [6, 3, 6, 1],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "coordination_index_var": ["raw_t"],
        },
    )

    assert "协调指数T变量必须是 0~1" in result["description"]
    assert "原始量表题项" in result["description"]


def test_coupling_long_calculation_table_keeps_full_spssau_item_rows():
    df = pd.DataFrame(
        {
            "group": [1, 2] * 20,
            "q1": list(range(1, 41)),
            "q2": list(range(40, 0, -1)),
            "q3": [value * 2 for value in range(1, 41)],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q3"],
            "negative_vars": ["q2"],
            "label_vars": ["group"],
        },
    )

    table = _section(result, "输出结果1：耦合协调度计算结果")
    chart = _section(result, "输出结果2：耦合协调度图")["charts"][0]

    assert len(result["rows"]) == 40
    assert len(table["rows"]) == 40
    assert table["rows"][0][0] == "第1项"
    assert table["rows"][-1][0] == "第40项"
    assert "按样本顺序列示" in table["description"]
    assert len(chart["data"]["labels"]) == 40


def test_coupling_legacy_group_params_remain_compatible():
    df = pd.DataFrame(
        {
            "a1": [1, 2, 3, 4],
            "a2": [2, 3, 4, 5],
            "b1": [4, 3, 2, 1],
        }
    )

    result = coupling_coordination.run(
        df,
        {
            "group1_vars": ["a1", "a2"],
            "group2_vars": ["b1"],
        },
    )

    assert len(result["rows"]) == 4
    assert ["正向指标", "a1、a2、b1"] in _section(result, "算法配置")["rows"]
    weight_rows = _section(result, "指标权重计算")["rows"]
    assert weight_rows[0][0] == "子系统1"
    assert weight_rows[1][0] == "子系统2"
    assert weight_rows[0][1] == "50.000"


def test_coupling_rejects_duplicate_direction_and_weight_var_as_indicator():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3],
            "q2": [3, 2, 1],
        }
    )

    duplicate = coupling_coordination.run(df, {"positive_vars": ["q1"], "negative_vars": ["q1"]})
    assert "同一指标不能同时作为正向和负向指标" in duplicate["description"]

    weight_as_indicator = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "weight_method": "custom",
            "weight_var": ["q2"],
        },
    )
    assert "指标权重列不能同时作为评价指标" in weight_as_indicator["description"]


def test_coupling_save_process_returns_full_length_score_columns():
    df = pd.DataFrame(
        {
            "q1": [1, 2, None, 4],
            "q2": [4, 3, 2, 1],
        },
        index=[10, 20, 30, 40],
    )

    result = coupling_coordination.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "save_process": True,
        },
    )

    score_columns = result["score_columns"]
    assert [column["base_name"] for column in score_columns] == [
        "耦合协调_耦合度C",
        "耦合协调_协调指数T",
        "耦合协调_协调度D",
        "耦合协调_协调等级",
    ]
    assert all(len(column["values"]) == 4 for column in score_columns)
    assert all(column["values"][2] is None for column in score_columns)
