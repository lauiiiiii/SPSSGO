# -*- coding: utf-8 -*-
import pandas as pd

from backend.analysis.common import build_slot_param_example
from backend.analysis.methods import rsr


def _section(result, title):
    return next(section for section in result["sections"] if section["title"] == title)


def test_rsr_meta_combines_rsr_wrsr_controls():
    weight_slot = next(slot for slot in rsr.METHOD_META["slots"] if slot["key"] == "weight_var")
    assert weight_slot["visible_if"] == {"weight_method": "custom"}
    assert "WRSR秩和比" in rsr.METHOD_META["aliases"]

    sample = build_slot_param_example(rsr.METHOD_META)
    assert "weight_var" not in sample
    assert sample["weight_method"] == "equal"
    assert sample["rank_method"] == "integer"
    assert sample["division_count"] == "3"


def test_rsr_outputs_spssau_spsspro_granularity():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C", "D"],
            "q1": [80, 90, 70, 95],
            "q2": [8, 6, 9, 5],
            "q3": [30, 40, 35, 45],
        }
    )

    result = rsr.run(
        df,
        {
            "positive_vars": ["q1", "q3"],
            "negative_vars": ["q2"],
            "index_var": ["name"],
            "weight_method": "entropy",
            "rank_method": "fractional",
            "division_count": "4",
        },
    )

    assert result["headers"] == ["评价对象", "WRSR值", "排序结果", "分档"]
    assert result["rows"][0][0] == "D"
    assert "变量权重为熵权法" in result["description"]
    assert ["编秩方法", "非整次法"] in _section(result, "算法配置")["rows"]
    assert ["分档数量", "4档"] in _section(result, "算法配置")["rows"]
    assert not any(row[0] == "指标权重列" for row in _section(result, "算法配置")["rows"])
    assert _section(result, "输出结果1：指标权重计算")["headers"] == ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    assert "区分作用相对更大" in _section(result, "输出结果1：指标权重计算")["description"]
    calc_section = _section(result, "WRSR值计算表格")
    assert calc_section["headers"] == ["项", "q1", "q3", "q2", "WRSR值", "WRSR排名"]
    assert calc_section["headerRows"][1] == ["", "[秩]", "[秩]", "[秩]", "", ""]
    assert len(calc_section["rows"][0]) == 6
    assert "转换秩次" in calc_section["description"]
    assert "论文解释时" in _section(result, "输出结果3：RSR/WRSR排序结果")["description"]
    assert _section(result, "输出结果4：RSR/WRSR分布表")["headers"] == [
        "WRSR值",
        "频数",
        "累计频数",
        "平均秩次",
        "累计频率(%)",
        "Probit值",
    ]
    fit_charts = _section(result, "输出结果5：拟合效果图")["charts"]
    assert len(fit_charts) == 1
    fit_chart = fit_charts[0]
    assert fit_chart["title"] == "拟合效果图"
    assert fit_chart["data"]["axisLabels"]["x"] == "排序序号"
    assert fit_chart["data"]["labels"] == ["1", "2", "3", "4"]
    assert list(fit_chart["data"]["metrics"].keys()) == ["实际值", "预测值"]
    assert len(fit_chart["data"]["metrics"]["实际值"]) == 4
    assert len(fit_chart["data"]["metrics"]["预测值"]) == 4
    assert fit_chart["data"]["metrics"]["实际值"] == sorted(fit_chart["data"]["metrics"]["实际值"])
    regression_section = _section(result, "输出结果6：回归模型表格")
    assert regression_section["headers"] == ["项", "B", "标准误", "Beta", "t", "p", "R²", "调整R²", "F"]
    assert regression_section["headerRows"][0][1]["text"] == "非标准化系数"
    assert regression_section["rows"][1][0] == "Probit值"
    assert regression_section["rows"][0][6]["rowspan"] == 2
    assert "F (" in regression_section["rows"][0][8]["text"]
    assert regression_section["note"] == "备注：因变量 = WRSR分布值"
    assert "Probit 线性回归用于检验" in regression_section["description"]
    assert not any(section["title"] == "Probit回归概况" for section in result["sections"])
    assert "分档汇总显示" in _section(result, "输出结果8：分档汇总")["description"]
    charts = _section(result, "输出结果9：综合评价图")["charts"]
    assert [chart["chartType"] for chart in charts] == ["metric_comparison", "category_distribution"]
    assert "在论文写作中" in _section(result, "结果解释")["content"]
    refs = _section(result, "参考文献")["items"]
    assert len(refs) == 8
    assert any("田凤调" in ref for ref in refs)
    assert any("Shannon C E" in ref for ref in refs)
    assert any("Finney D J" in ref for ref in refs)


def test_rsr_legacy_variables_param_uses_equal_weight_positive_indicators():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3, 4],
            "q2": [4, 3, 2, 1],
        }
    )

    result = rsr.run(df, {"variables": ["q1", "q2"]})

    config_rows = _section(result, "算法配置")["rows"]
    assert ["正向指标", "q1、q2"] in config_rows
    assert ["变量权重", "不设置权重"] in config_rows
    assert ["输出指标", "RSR值"] in config_rows
    assert _section(result, "输出结果1：指标权重计算")["headers"] == ["项", "权重(%)"]
    weight_rows = _section(result, "输出结果1：指标权重计算")["rows"]
    assert weight_rows[0][1] == "50.000"
    assert weight_rows[1][1] == "50.000"


def test_rsr_integer_rank_uses_sample_rank_scale_for_ties():
    df = pd.DataFrame(
        {
            "q1": [1, 1, 2, 2, 3, 3],
            "q2": [1, 1, 2, 2, 3, 3],
        }
    )

    result = rsr.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "rank_method": "integer",
            "weight_method": "equal",
        },
    )

    scores = [float(row[1]) for row in result["rows"]]
    assert max(scores) > 0.9
    assert min(scores) < 0.3
    assert "样本排序得到 1 到 N 的秩次" in _section(result, "RSR值计算表格")["description"]


def test_rsr_custom_weight_column_is_normalized_by_variable_order():
    df = pd.DataFrame(
        {
            "q1": [1, 1, 3, 4],
            "q2": [4, 3, 2, 1],
            "weight": [7, 3, None, None],
        }
    )

    result = rsr.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "weight_method": "custom",
            "weight_var": ["weight"],
            "rank_method": "fractional",
        },
    )

    weight_section = _section(result, "输出结果1：指标权重计算")
    assert weight_section["headers"] == ["项", "权重(%)"]
    weight_rows = weight_section["rows"]
    assert weight_rows[0][1] == "70.000"
    assert weight_rows[1][1] == "30.000"
    assert ["指标权重列", "weight"] in _section(result, "算法配置")["rows"]
    assert result["headers"][1] == "WRSR值"


def test_rsr_rejects_duplicate_direction_and_weight_var_as_indicator():
    df = pd.DataFrame(
        {
            "q1": [1, 2, 3],
            "q2": [3, 2, 1],
        }
    )

    duplicate = rsr.run(df, {"positive_vars": ["q1"], "negative_vars": ["q1"]})
    assert "同一指标不能同时作为正向和负向指标" in duplicate["description"]

    weight_as_indicator = rsr.run(
        df,
        {
            "positive_vars": ["q1", "q2"],
            "weight_method": "custom",
            "weight_var": ["q2"],
        },
    )
    assert "指标权重列不能同时作为评价指标" in weight_as_indicator["description"]
