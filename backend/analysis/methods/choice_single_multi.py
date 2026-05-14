# -*- coding: utf-8 -*-
# 单选题与多选题交叉分析：按 SPSSPRO 结构输出多重响应频率、交叉检验和公共图表。
from backend.analysis.common import *
from backend.analysis.methods.choice_multi_single import (
    _choice_masks,
    _frequency_sections,
    _frequency_stats,
    _format_percent,
    _label,
    _p_summary,
    _single_labels,
)

METHOD_KEY = "choice_single_multi"
METHOD_META = {'label': '单选-多选（对比分析）',
 'category': '问卷分析包',
 'description': '基于卡方检验分析单选题与多选题选项之间是否存在显著差异',
 'order': 57,
 'slots': [{'key': 'single_var',
            'label': '单选变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入单选题变量'},
           {'key': 'multiple_vars',
            'label': '二分类0-1变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一题目的多选拆分变量'}],
 'options': [{'key': 'count_value',
              'label': '计数值',
              'choices': ['1', '2', '0'],
              'choice_labels': {'1': '计数值，默认1'},
              'default': '1',
              'hint': '默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。'}],
 'param_builder': 'direct'}

def inject_metadata(metadata_map, params):
    enriched = dict(params)
    variables = list(enriched.get("multiple_vars") or [])
    single_var = enriched.get("single_var")
    if single_var:
        variables.append(single_var)
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    value_labels = metadata_map.get(single_var or "", {}).get("value_labels") or {}
    enriched["single_value_labels"] = normalized_label_dict(value_labels)
    return enriched


def _analysis_result(single_label, cross):
    p_value = cross["p"]
    if p_value is None:
        return (
            f"交叉分析【单选&多选】基于卡方检验来分析单选题{single_label}与多选题的选项是否存在显著性差异。\n"
            "当前交叉表未能计算卡方检验显著性P值，建议检查是否存在过多空单元格或有效样本不足。"
        )
    decision = (
        f"水平上呈现显著性，拒绝原假设，说明单选题{single_label}与多选题之间具有显著性差异。"
        if p_value <= 0.05
        else f"水平上不呈现显著性，接受原假设，说明单选题{single_label}与多选题之间不具有显著性差异。"
    )
    return (
        f"交叉分析【单选&多选】基于卡方检验来分析单选题与多选题的选项是否存在显著性差异：\n"
        f"卡方检验的显著性P值为{_fmt(p_value, 3)}，{decision}"
    )


def _analysis_steps():
    return "\n".join([
        "1. 根据多重响应频率分析表对响应率与普及率进行分析，响应率为全部样本下的各选项的选择比例，普及率为有效样本下的各选项的选择比例，两者都重点对比例较高项进行分析。",
        "2. 进行卡方拟合优度检验，分析各选项的选择比例是否存在差异性，若P<0.05，则说明拒绝没有差异的原假设，各选项的选择比例具有显著性差异。",
        "3. 根据多重响应交叉表进行分析，通过对比计数与百分比，重点对比例较高项进行分析。",
        "4. 通过卡方检验多选题与单选题之间的交叉关系，若显著性P值大于0.05，则说明其并不会呈现出差异性。",
        "5. 对分析进行总结。",
    ])


def _cross_result(single_label, multi_labels, group_values, group_labels, masks, single_series):
    matrix = []
    for variable in masks.columns:
        selected = masks[variable]
        row = []
        for group_value in group_values:
            group_mask = single_series.astype(str) == group_value
            row.append(int((selected & group_mask).sum()))
        matrix.append(row)

    row_totals = [sum(row) for row in matrix]
    group_totals = [int((single_series.astype(str) == value).sum()) for value in group_values]
    grand_total = int(sum(row_totals))
    chi2_value = None
    p_value = None
    if grand_total > 0 and len(matrix) >= 2 and len(group_values) >= 2:
        try:
            chi2_value, p_value, _, _ = chi2_contingency(matrix)
        except ValueError:
            chi2_value, p_value = None, None

    headers = ["分组题项", ""] + multi_labels + ["总数", "X²", "P"]
    rows = []
    for group_index, group_value in enumerate(group_values):
        group_total = group_totals[group_index]
        row = [single_label if group_index == 0 else "", group_labels[group_value]]
        for multi_index in range(len(multi_labels)):
            count = matrix[multi_index][group_index]
            percent = count / group_total * 100 if group_total else 0
            row.append(f"{count}（{_format_percent(percent)}）")
        row.append(str(group_total))
        row.append(_fmt(chi2_value, 3) if group_index == 0 else "")
        row.append((_fmt(p_value, 3) + _sig(p_value)) if group_index == 0 and p_value is not None else "")
        rows.append(row)
    rows.append(["总计", ""] + [str(value) for value in row_totals] + [str(grand_total), "", ""])
    return {
        "headers": headers,
        "headerRows": [
            [
                {"text": "分组题项", "colspan": 2},
                *multi_labels,
                {"text": "总数", "rowspan": 1},
                {"text": "X²", "rowspan": 1},
                {"text": "P", "rowspan": 1},
            ],
        ],
        "rows": rows,
        "matrix": matrix,
        "row_totals": row_totals,
        "group_totals": group_totals,
        "grand_total": grand_total,
        "chi2": chi2_value,
        "p": p_value,
    }


def _cross_description():
    return "\n".join([
        "图表说明：",
        "上表为多重响应频率交叉分析表，包括卡方检验值、显著性P值等。",
        "• 分析卡方检验多选题与单选题之间的交叉关系，若P<0.05，则说明多选题与单选题之间存在差异性。",
        "• 通过对比计数与百分比，重点对比例较高项进行分析。",
    ])


def _cross_smart(single_label, multi_labels, group_labels, cross):
    p_value = cross["p"]
    target = f"不同{single_label}在{'、'.join(multi_labels)}上的选择"
    group_text = "、".join(group_labels.values())
    if p_value is None:
        p_text = "未能计算卡方检验P值，建议检查交叉表是否存在过多空单元格。"
    else:
        p_text = _p_summary(p_value, target)
    return (
        f"模型的多重响应分析交叉表显示，单选分组包括{group_text}。"
        f"{p_text}"
    )


def _cross_chart(single_label, multi_labels, group_values, group_labels, matrix):
    return {
        "chartType": "crosstab_distribution",
        "title": "交叉图",
        "data": {
            "groupVariable": single_label,
            "xVariable": "多选题选项",
            "groupLabels": [group_labels[value] for value in group_values],
            "xLabels": multi_labels,
            "matrix": matrix,
            "total": int(sum(sum(row) for row in matrix)),
            "percentBase": "row",
            "defaultMode": "column",
            "defaultLabelMode": "count",
        },
    }


def run(df, params):
    """
    单选题与多选题交叉分析。

    @param df: 数据 DataFrame
    @param params: single_var 单选分组字段，multiple_vars 多选拆分字段，count_value 为选中编码
    @return: SPSSPRO 风格的多选频率、单选分组交叉表、交叉图与显著性解释
    """
    single_var = params.get("single_var", "")
    multiple_vars = _resolve_cols(df, params.get("multiple_vars", []))
    count_value = params.get("count_value", "1")
    variable_labels = params.get("variable_labels", {})
    value_labels = params.get("single_value_labels", {})
    if single_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"单选变量 {single_var} 不存在。"}
    if len(multiple_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个多选拆分变量。"}

    temp = df[[single_var] + multiple_vars].copy()
    temp = temp[temp[single_var].notna()]
    sample_size = int(len(temp))
    if sample_size == 0:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有可用样本。"}

    multi_labels = [_label(variable_labels, variable) for variable in multiple_vars]
    single_label = _label(variable_labels, single_var)
    group_values, group_labels = _single_labels(temp[single_var], value_labels)
    masks = _choice_masks(temp, multiple_vars, count_value)
    stats = _frequency_stats(multi_labels, [int(masks[variable].sum()) for variable in multiple_vars], sample_size)
    cross = _cross_result(single_label, multi_labels, group_values, group_labels, masks, temp[single_var])

    sections = [
        _sec_advice(_analysis_result(single_label, cross), "分析结果"),
        _sec_advice(_analysis_steps(), "分析步骤"),
    ]
    sections.extend(_frequency_sections(stats))
    cross_section = _sec_table(
        "输出结果5：多重响应频率交叉分析表",
        cross["headers"],
        cross["rows"],
        note="注：***、**、*分别代表1%、5%、10%的显著性水平",
        description=_cross_description(),
    )
    cross_section["headerRows"] = cross["headerRows"]
    sections.append(cross_section)
    sections.append(_sec_smart(_cross_smart(single_label, multi_labels, group_labels, cross)))
    sections.append(_sec_charts(
        "输出结果6：交叉图",
        [_cross_chart(single_label, multi_labels, group_values, group_labels, cross["matrix"])],
        "上图展示了单选题选项与多选题选项的频数分布情况。横轴为问题选项，纵轴为出现频率。",
    ))
    sections.append(_sec_refs(_REFS_MULTIPLE_RESPONSE_CROSS))

    return {
        "name": METHOD_META["label"],
        "headers": cross["headers"],
        "rows": cross["rows"],
        "description": _analysis_result(single_label, cross).replace("\n", " "),
        "sections": sections,
    }
