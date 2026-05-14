# -*- coding: utf-8 -*-
# 多选题与单选题对比分析：输出多选频率、组间交叉表和交叉图，贴近 SPSSPRO 报告结构。
from backend.analysis.common import *

METHOD_KEY = "choice_multi_single"
METHOD_META = {'label': '多选-单选（对比分析）',
 'category': '问卷分析包',
 'description': '分析多选题选项在不同单选分组中的分布与差异情况',
 'order': 56,
 'slots': [{'key': 'multiple_vars',
            'label': '二分类0-1变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一题目的多选拆分变量'},
           {'key': 'single_var',
            'label': '单选分组变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入用于分组的单选题变量'}],
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


def _label(variable_labels, variable):
    return variable_labels.get(variable, variable)


def _format_percent(value, digits=3):
    text = _fmt(value, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{text}%"


def _choice_masks(df, variables, count_value):
    return pd.DataFrame({
        variable: _count_value_mask(df[variable], count_value)
        for variable in variables
    })


def _single_labels(series, value_labels):
    values = series.dropna().unique().tolist()
    return [str(value) for value in values], {
        str(value): value_labels.get(str(value), str(value))
        for value in values
    }


def _frequency_stats(labels, counts, sample_size):
    total_responses = int(sum(counts))
    response_rates = [count / total_responses * 100 if total_responses else 0 for count in counts]
    popularity_rates = [count / sample_size * 100 if sample_size else 0 for count in counts]
    chi2_value = None
    p_value = None
    if total_responses > 0 and len(counts) >= 2:
        try:
            chi2_value, p_value = chisquare(counts)
        except ValueError:
            chi2_value, p_value = None, None
    return {
        "labels": labels,
        "counts": counts,
        "total_responses": total_responses,
        "response_rates": response_rates,
        "popularity_rates": popularity_rates,
        "chi2": chi2_value,
        "p": p_value,
    }


def _frequency_rows(stats):
    rows = []
    for index, label in enumerate(stats["labels"]):
        p_value = stats["p"]
        rows.append([
            label,
            str(stats["counts"][index]),
            _format_percent(stats["response_rates"][index]),
            _format_percent(stats["popularity_rates"][index]),
            _fmt(stats["chi2"], 3) if index == 0 else "",
            (_fmt(p_value, 3) + _sig(p_value)) if index == 0 and p_value is not None else "",
        ])
    rows.append([
        "总计",
        str(stats["total_responses"]),
        _format_percent(100.0 if stats["total_responses"] else 0.0),
        _format_percent(sum(stats["popularity_rates"])),
        "",
        "",
    ])
    return rows


def _p_summary(p_value, target="各选项选择比例"):
    if p_value is None:
        return "未能计算显著性P值，建议检查表格是否存在过多空单元格。"
    if p_value <= 0.05:
        return (
            f"显著性P值为{_fmt(p_value, 3)}{_sig(p_value)}，P值小于等于0.05，"
            f"在α=0.05时水平上呈现显著性，说明{target}存在显著差异。"
        )
    return (
        f"显著性P值为{_fmt(p_value, 3)}{_sig(p_value)}，P值大于0.05，"
        f"在α=0.05时水平上不呈现显著性，说明{target}未见明显差异。"
    )


def _analysis_result(single_label, cross):
    p_value = cross["p"]
    if p_value is None:
        return (
            f"交叉分析【多选&单选】基于卡方检验来分析多选题与单选题{single_label}之间是否存在显著性差异：\n"
            "当前交叉表未能计算卡方检验显著性P值，建议检查是否存在过多空单元格或有效样本不足。"
        )
    decision = (
        f"水平上呈现显著性，拒绝原假设，说明多选题与单选题{single_label}之间具有显著性差异。"
        if p_value <= 0.05
        else f"水平上不呈现显著性，接受原假设，说明多选题与单选题{single_label}之间不具有显著性差异。"
    )
    return (
        "交叉分析【多选&单选】基于卡方检验来分析多选题与单选题之间是否存在显著性差异：\n"
        f"卡方检验的显著性P值为{_fmt(p_value, 3)}，{decision}"
    )


def _analysis_steps(multi_labels, single_label):
    return "\n".join([
        "1. 根据多重响应频率分析表，对多选题各选项计算计数、响应率与普及率，重点比较高频选项。",
        "2. 对多选题做卡方拟合优度检验，判断各选项选择比例是否存在显著差异。",
        "3. 通过响应率图、普及率图和帕累托图，观察各选项的选择集中程度和主要贡献项。",
        "4. 根据多重响应频率交叉表，分析不同单选分组在多选题各选项上的选择分布。",
        "5. 通过卡方检验判断多选题与单选分组之间是否存在显著差异，并结合交叉图总结结果。",
        f"本次多选题包含：{'、'.join(multi_labels)}；单选分组变量为：{single_label}。",
    ])


def _frequency_description():
    return "\n".join([
        "图表说明：",
        "上表为多重响应频率分析表，展示了选项的频率分布情况，包括个案数、响应率、普及率、显著性P值等。",
        "• 响应率为多选题各选项的全部选择项比例，例如一个多选题由10人回答，共选择了36个选项，其中A选项有8次，则响应率=8/36。",
        "• 普及率为有效样本下各选项的选择比例，例如一个多选题由10人回答，其中A选项有8人选择，则普及率=8/10。",
        "• 响应率和普及率都用于观察选项热度，通常重点关注比例较高的选项。",
    ])


def _frequency_smart(stats):
    max_index = max(range(len(stats["counts"])), key=lambda index: stats["counts"][index]) if stats["counts"] else None
    top_text = ""
    if max_index is not None:
        top_text = (
            f"其中“{stats['labels'][max_index]}”选择次数最高，计数为{stats['counts'][max_index]}，"
            f"响应率为{_format_percent(stats['response_rates'][max_index])}，"
            f"普及率为{_format_percent(stats['popularity_rates'][max_index])}。"
        )
    return f"根据多重响应频率分析表显示，{top_text}卡方拟合优度检验{_p_summary(stats['p'])}"


def _category_chart(title, labels, counts, percents, total, default_mode):
    return {
        "chartType": "category_distribution",
        "title": title,
        "varName": title,
        "data": {
            "variable": title,
            "labels": labels,
            "counts": counts,
            "percents": percents,
            "total": int(total),
            "defaultMode": default_mode,
        },
    }


def _pareto_chart(title, labels, counts):
    ordered = sorted(zip(labels, counts), key=lambda item: item[1], reverse=True)
    sorted_labels = [item[0] for item in ordered]
    sorted_counts = [int(item[1]) for item in ordered]
    total = sum(sorted_counts)
    cumulative = []
    running = 0
    for count in sorted_counts:
        running += count
        cumulative.append(running / total * 100 if total else 0)
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "isPareto": True,
            "metric": "频次",
            "displayTitle": title,
            "labels": sorted_labels,
            "values": sorted_counts,
            "metrics": {
                "频次": sorted_counts,
                "累计百分比": cumulative,
            },
            "defaultMode": "bar",
        },
    }


def _frequency_sections(stats):
    headers = ["多选题选项", "N（计数）", "响应率（%）", "普及率（%）", "X²", "P"]
    return [
        _sec_table(
            "输出结果1：多重响应频率分析表",
            headers,
            _frequency_rows(stats),
            note="注：***、**、*分别代表1%、5%、10%的显著性水平",
            description=_frequency_description(),
        ),
        _sec_smart(_frequency_smart(stats)),
        _sec_charts(
            "输出结果2：响应率",
            [_category_chart("响应率", stats["labels"], stats["counts"], stats["response_rates"], stats["total_responses"], "pie")],
            "上图以可视化形式展示了多选题各选项响应率的频数分布情况。",
        ),
        _sec_charts(
            "输出结果3：普及率",
            [_category_chart("普及率", stats["labels"], stats["counts"], stats["popularity_rates"], sum(stats["counts"]), "bar")],
            "上图以直方图形式展示了各个问题选项普及率的分布情况。",
        ),
        _sec_charts(
            "输出结果4：帕累托图分析",
            [_pareto_chart("帕累托图", stats["labels"], stats["counts"])],
            "\n".join([
                "帕累托图是“二八原则”的图形化体现，用于识别少数高贡献选项。",
                "第一：结合图形，找出累计比率为0%~80%对应的选项，这类选项通常是主要关注项。",
                "第二：累计比率在80%~100%对应的选项，通常可作为补充观察项，重要性相对较低。",
            ]),
        ),
    ]


def _cross_result(multi_labels, group_values, group_labels, masks, single_series):
    matrix = []
    for variable in masks.columns:
        selected = masks[variable]
        row = []
        for group_value in group_values:
            group_mask = single_series.astype(str) == group_value
            row.append(int((selected & group_mask).sum()))
        matrix.append(row)

    row_totals = [sum(row) for row in matrix]
    col_totals = [
        sum(matrix[row_index][col_index] for row_index in range(len(matrix)))
        for col_index in range(len(group_values))
    ]
    grand_total = int(sum(row_totals))
    chi2_value = None
    p_value = None
    if grand_total > 0 and len(matrix) >= 2 and len(group_values) >= 2:
        try:
            chi2_value, p_value, _, _ = chi2_contingency(matrix)
        except ValueError:
            chi2_value, p_value = None, None

    headers = ["分组题项"] + [group_labels[value] for value in group_values] + ["总数", "X²", "P"]
    rows = []
    for row_index, label in enumerate(multi_labels):
        row_total = row_totals[row_index]
        row = [label]
        for value in matrix[row_index]:
            percent = value / row_total * 100 if row_total else 0
            row.append(f"{value}（{_format_percent(percent)}）")
        row.append(str(row_total))
        row.append(_fmt(chi2_value, 3) if row_index == 0 else "")
        row.append((_fmt(p_value, 3) + _sig(p_value)) if row_index == 0 and p_value is not None else "")
        rows.append(row)
    rows.append(["总计"] + [str(value) for value in col_totals] + [str(grand_total), "", ""])
    return {
        "headers": headers,
        "headerRows": [
            [
                {"text": "分组题项", "rowspan": 2},
                {"text": "", "colspan": len(group_values)},
                {"text": "总数", "rowspan": 2},
                {"text": "X²", "rowspan": 2},
                {"text": "P", "rowspan": 2},
            ],
            [group_labels[value] for value in group_values],
        ],
        "rows": rows,
        "matrix": matrix,
        "row_totals": row_totals,
        "col_totals": col_totals,
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
    多选题与单选题交叉对比分析。

    @param df: 数据 DataFrame
    @param params: multiple_vars 多选拆分字段，single_var 单选分组字段，count_value 为选中编码
    @return: 多选频率分析、单选分组交叉表和交叉图
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
    cross = _cross_result(multi_labels, group_values, group_labels, masks, temp[single_var])
    cross["headerRows"][0][1]["text"] = single_label

    sections = [
        _sec_advice(_analysis_result(single_label, cross), "分析结果"),
        _sec_advice(_analysis_steps(multi_labels, single_label), "分析步骤"),
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
        "上图展示了单选题选项与多选题选项的频数分布情况，横轴为单选题选项，图例为多选题选项。",
    ))
    sections.append(_sec_refs(_REFS_MULTIPLE_RESPONSE_CROSS))

    return {
        "name": METHOD_META["label"],
        "headers": cross["headers"],
        "rows": cross["rows"],
        "description": _analysis_result(single_label, cross).replace("\n", " "),
        "sections": sections,
    }
