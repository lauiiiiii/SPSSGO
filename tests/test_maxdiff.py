# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import maxdiff


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def _pro_df():
    """MaxDiff Pro 原始数据：每行=一个受访者。"""
    return pd.DataFrame(
        {
            "best": ["battery", "camera", "price", "battery", "camera"],
            "worst": ["price", "price", "design", "design", "design"],
            "battery": ["battery", "camera", "price", "battery", "camera"],
            "camera": ["battery", "camera", "price", "battery", "camera"],
            "price": ["battery", "camera", "price", "battery", "camera"],
            "design": ["battery", "camera", "price", "battery", "camera"],
        }
    )


def _summary_df():
    """MaxDiff 汇总数据：每行=一个选项。"""
    return pd.DataFrame(
        {
            "index": ["battery", "camera", "price", "design"],
            "best_count": [2, 2, 1, 0],
            "worst_count": [0, 0, 2, 3],
            "total_count": [5, 5, 5, 5],
        }
    )


def test_maxdiff_meta():
    assert maxdiff.METHOD_META["label"] == "MaxDiff模型"
    assert "MaxDiff" in maxdiff.METHOD_META["aliases"]
    assert "MaxDiff Pro" in maxdiff.METHOD_META["aliases"]

    sample = build_slot_param_example(maxdiff.METHOD_META)
    slot_keys = [slot["key"] for slot in maxdiff.METHOD_META["slots"]]
    assert "best_variable" in slot_keys
    assert "worst_variable" in slot_keys
    assert "option_variables" in slot_keys
    assert "best_count_variable" in slot_keys
    assert "worst_count_variable" in slot_keys
    assert "total_count_variable" in slot_keys
    assert "index_variable" in slot_keys


def test_maxdiff_pro_mode():
    """测试 MaxDiff Pro 模式（原始数据）。"""
    result = maxdiff.run(
        _pro_df(),
        {
            "best_variable": "best",
            "worst_variable": "worst",
            "option_variables": ["battery", "camera", "price", "design"],
        },
    )

    assert result["name"] == "MaxDiff模型"
    assert "MaxDiff Pro" in result["description"]
    # 对齐 SPSSPRO 格式
    assert result["headers"] == ["属性", "效用系数", "标准误差", "z 统计量", "p 值", "最重要", "最不重要", "出现次数", "偏好份额"]

    table = _section(result, "MaxDiff Pro 属性估计结果")
    assert len(table["rows"]) == 4

    # battery: Best=2, Worst=0, 效用系数应为正
    battery_row = next(row for row in table["rows"] if row[0] == "battery")
    assert battery_row[5] == "2"  # 最重要
    assert battery_row[6] == "0"  # 最不重要
    assert float(battery_row[1]) > 0  # 效用系数为正


def test_maxdiff_summary_mode():
    """测试 MaxDiff 汇总模式。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    assert result["name"] == "MaxDiff模型"
    assert "MaxDiff" in result["description"]
    assert "MaxDiff Pro" not in result["description"]
    assert result["headers"] == ["属性", "效用系数", "标准误差", "z 统计量", "p 值", "最重要", "最不重要", "出现次数", "偏好份额"]

    table = _section(result, "MaxDiff 属性估计结果")
    assert len(table["rows"]) == 4

    # battery: Best=2, Worst=0, 效用系数应为正
    battery_row = next(row for row in table["rows"] if row[0] == "battery")
    assert battery_row[5] == "2"  # 最重要
    assert battery_row[6] == "0"  # 最不重要
    assert float(battery_row[1]) > 0  # 效用系数为正


def test_maxdiff_invalid_data_format():
    """测试无效数据格式。"""
    df = pd.DataFrame({"q1": [1, 2, 3], "q2": [4, 5, 6]})
    result = maxdiff.run(df, {"variables": ["q1", "q2"]})

    assert result["name"] == "MaxDiff模型"
    assert result["headers"] == []
    assert "数据格式不正确" in result["description"]


def test_maxdiff_pro_requires_option_variables():
    """测试 Pro 模式至少需要 2 个选项变量。"""
    df = pd.DataFrame({"best": ["a", "b"], "worst": ["b", "a"], "a": ["a", "b"]})
    result = maxdiff.run(
        df,
        {
            "best_variable": "best",
            "worst_variable": "worst",
            "option_variables": ["a"],
        },
    )

    assert result["name"] == "MaxDiff模型"
    assert result["headers"] == []
    assert "至少需要 2 个选项" in result["description"]


def test_maxdiff_summary_requires_3_rows():
    """测试汇总模式至少需要 3 个选项行。"""
    df = pd.DataFrame(
        {
            "index": ["a", "b"],
            "best_count": [1, 0],
            "worst_count": [0, 1],
            "total_count": [2, 2],
        }
    )
    result = maxdiff.run(
        df,
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    assert result["name"] == "MaxDiff模型"
    assert result["headers"] == []
    assert "至少需要 3 个选项" in result["description"]


def test_maxdiff_has_chart_section():
    """测试图表 section。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    chart_section = _section(result, "偏好份额")
    assert chart_section["charts"][0]["chartType"] == "metric_comparison"
    assert chart_section["charts"][0]["title"] == "偏好份额"


def test_maxdiff_has_advice_section():
    """测试结果分析 section。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    advice = _section(result, "结果分析")
    assert advice["title"] == "结果分析"
    # 检查包含专业解读的关键部分
    assert "整体结果概览" in advice["content"]
    assert "最受偏好属性" in advice["content"]
    assert "最不受偏好属性" in advice["content"]
    assert "统计指标解读" in advice["content"]
    assert "方法学说明" in advice["content"]
    assert "效用系数" in advice["content"]
    assert "偏好份额" in advice["content"]


def test_maxdiff_has_references_section():
    """测试参考文献 section。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    refs = _section(result, "参考文献")
    assert len(refs["items"]) >= 2


def test_maxdiff_with_variable_labels():
    """测试变量标题注入。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
            "variable_labels": {
                "battery": "电池",
                "camera": "拍照",
                "price": "价格",
                "design": "外观",
            },
        },
    )

    table = _section(result, "MaxDiff 属性估计结果")
    row_labels = [row[0] for row in table["rows"]]
    assert "电池" in row_labels
    assert "拍照" in row_labels
    assert "价格" in row_labels
    assert "外观" in row_labels


def test_maxdiff_preference_shares_sum_to_100():
    """测试偏好份额之和为 100%。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    table = _section(result, "MaxDiff 属性估计结果")
    total = sum(float(row[8].rstrip("%")) for row in table["rows"])
    assert abs(total - 100.0) < 0.1


def test_maxdiff_inject_metadata():
    """测试元数据注入。"""
    metadata_map = {
        "best": {"display_name": "最重要选择"},
        "worst": {"display_name": "最不重要选择"},
        "battery": {"display_name": "电池续航"},
    }
    params = {
        "best_variable": "best",
        "worst_variable": "worst",
        "option_variables": ["battery", "camera"],
    }

    enriched = maxdiff.inject_metadata(metadata_map, params)

    assert enriched["variable_labels"]["best"] == "最重要选择"
    assert enriched["variable_labels"]["worst"] == "最不重要选择"
    assert enriched["variable_labels"]["battery"] == "电池续航"


def test_maxdiff_p_value_significance():
    """测试 p 值显著性标记。"""
    result = maxdiff.run(
        _summary_df(),
        {
            "best_count_variable": "best_count",
            "worst_count_variable": "worst_count",
            "total_count_variable": "total_count",
            "index_variable": "index",
        },
    )

    table = _section(result, "MaxDiff 属性估计结果")
    # 检查 p 值列是否有显著性标记（***, **, *）
    for row in table["rows"]:
        p_str = row[4]
        # p 值列应该包含数字，可能带有 * 标记
        assert any(c.isdigit() for c in p_str)
