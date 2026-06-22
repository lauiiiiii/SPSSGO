# -*- coding: utf-8 -*-
from unittest.mock import patch

import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import entropy_weight


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def _df():
    return pd.DataFrame(
        {
            "q1": [6.5, 4.5, 1.5, 3.0],
            "q2": [4.5, 3.5, 2.0, 2.5],
            "q3": [1.5, 2.5, 3.0, 4.0],
        }
    )


def test_entropy_weight_meta_uses_weight_analysis_with_method_selector():
    assert entropy_weight.METHOD_META["label"] == "权重分析"
    assert "权重分析(熵权法)" in entropy_weight.METHOD_META["aliases"]

    sample = build_slot_param_example(entropy_weight.METHOD_META)

    assert sample["variables"] == ["数值变量1", "数值变量2"]
    assert sample["analysis_method"] == "ranking"
    method_option = next(option for option in entropy_weight.METHOD_META["options"] if option["key"] == "analysis_method")
    assert [choice["label"] for choice in method_option["choices"]] == ["AHP权重", "熵值法", "优序图法"]


def test_entropy_weight_legacy_without_method_still_uses_entropy_weight():
    result = entropy_weight.run(_df(), {"variables": ["q1", "q2", "q3"]})

    assert result["name"] == "权重分析"
    assert result["headers"] == ["项", "熵值", "差异系数", "权重(%)"]
    assert "熵权分析完成" in result["description"]
    # 对齐 SPSSAU：权重计算结果
    assert _section(result, "权重计算结果")["headers"] == ["项", "熵值", "差异系数", "权重(%)"]
    # 对齐 SPSSAU：权重值图表
    assert _section(result, "权重值")["charts"][0]["chartType"] == "metric_comparison"
    # 对齐 SPSSAU：分析建议
    assert _section(result, "分析建议")["title"] == "分析建议"


def test_entropy_weight_ranking_method_reuses_ranking_report_under_unified_name():
    result = entropy_weight.run(_df(), {"variables": ["q1", "q2", "q3"], "analysis_method": "ranking"})

    assert result["name"] == "权重分析"
    assert result["description"].startswith("优序图法：")
    assert result["headers"] == ["项", "平均值", "TTL(指标得分)", "权重值"]
    # 对齐 SPSSAU：优序图权重计算表
    assert _section(result, "优序图权重计算表")["headers"] == ["项", "q1", "q2", "q3"]
    # 对齐 SPSSAU：优序图权重计算结果表
    assert _section(result, "优序图权重计算结果表")["headers"] == ["项", "平均值", "TTL(指标得分)", "权重值"]
    # 对齐 SPSSAU：分析建议
    assert _section(result, "分析建议")["title"] == "分析建议"
    # 对齐 SPSSAU：权重值图表
    assert _section(result, "权重值")["charts"][0]["chartType"] == "metric_comparison"


def test_entropy_weight_ahp_method_forwards_data_auto_payload():
    r_result = {
        "success": True,
        "name": "层次分析法（AHP快速版）",
        "headers": ["准则", "权重", "排序"],
        "rows": [["q1", "0.6000", "1"], ["q2", "0.4000", "2"]],
        "description": "AHP 快速版完成",
        "sections": [
            {"type": "table", "title": "判断矩阵", "headers": ["平均值", "项", "q1", "q2"], "rows": []},
            {"type": "table", "title": "AHP层次分析结果", "headers": ["项", "特征向量", "权重值", "最大特征值", "CI值"], "rows": []},
            {"type": "table", "title": "一致性检验结果", "headers": ["最大特征根", "CI值", "RI值", "CR值", "一致性检验结果"], "rows": []},
            {"type": "advice", "title": "分析建议", "content": "test"},
            {"type": "charts", "title": "权重值", "charts": [{"chartType": "metric_comparison"}]},
            {"type": "references", "title": "参考文献", "items": []},
        ],
    }

    with patch("backend.analysis.methods.ahp_simplified.run", return_value=r_result) as run_ahp:
        result = entropy_weight.run(
            _df(),
            {
                "variables": ["q1", "q2"],
                "analysis_method": "ahp",
                "include_missing_analysis": True,
            },
        )

    assert result["name"] == "权重分析"
    assert result["description"] == "AHP权重：AHP 快速版完成"
    # 对齐 SPSSAU：不再注入"算法配置"section
    assert _section(result, "判断矩阵")["title"] == "判断矩阵"
    assert _section(result, "AHP层次分析结果")["title"] == "AHP层次分析结果"
    assert _section(result, "一致性检验结果")["title"] == "一致性检验结果"
    assert _section(result, "分析建议")["title"] == "分析建议"
    assert _section(result, "权重值")["charts"][0]["chartType"] == "metric_comparison"
    payload = run_ahp.call_args.args[1]
    assert payload == {
        "input_mode": "data_auto",
        "variables": ["q1", "q2"],
        "variable_labels": {},
        "weight_method": "sum_product",
        "include_missing_analysis": True,
    }


def test_entropy_weight_rejects_unknown_analysis_method():
    result = entropy_weight.run(_df(), {"variables": ["q1", "q2"], "analysis_method": "bad"})

    assert result["name"] == "权重分析"
    assert result["headers"] == []
    assert "分析方法不支持" in result["description"]
