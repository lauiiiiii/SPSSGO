# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "choice_multi_multi"
METHOD_META = {'label': '多选-多选（交叉分析）',
 'category': '问卷分析包',
 'description': '分析两组多选题选项之间的联合选择分布和差异情况',
 'order': 55,
 'slots': [{'key': 'variables_a',
            'label': '二分类0-1变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入第一组多选题变量，变量数至少为2'},
           {'key': 'variables_b',
            'label': '二分类0-1变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入第二组多选题变量，变量数至少为2'}],
 'options': [{'key': 'count_value',
              'label': '计数值',
              'choices': ['1', '2', '0'],
              'choice_labels': {'1': '计数值，默认1'},
              'default': '1',
              'hint': '默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。'}],
 'param_builder': 'direct'}


def inject_metadata(metadata_map, params):
    enriched = dict(params)
    variables = list(enriched.get("variables_a") or []) + list(enriched.get("variables_b") or [])
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    return enriched


def _choice_mask(df, variables, count_value):
    return pd.DataFrame({
        variable: _count_value_mask(df[variable], count_value)
        for variable in variables
    })


def _count_value_mask(series, count_value):
    expected_text = str(count_value if count_value not in (None, "") else "1").strip()
    raw_text = series.astype(str).str.strip()
    numeric = pd.to_numeric(series, errors="coerce")
    expected_numeric = _safe_float(expected_text, None)
    if expected_numeric is None:
        return raw_text == expected_text
    return raw_text.eq(expected_text) | numeric.eq(expected_numeric)


def _label(variable_labels, variable):
    return variable_labels.get(variable, variable)


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
            _fmt(stats["response_rates"][index], 3),
            _fmt(stats["popularity_rates"][index], 3),
            _fmt(stats["chi2"], 3) if index == 0 else "",
            (_fmt(p_value, 3) + _sig(p_value)) if index == 0 and p_value is not None else "",
        ])
    rows.append([
        "总计",
        str(stats["total_responses"]),
        _fmt(100.0 if stats["total_responses"] else 0.0, 3),
        _fmt(sum(stats["popularity_rates"]), 3),
        "",
        "",
    ])
    return rows


def _category_chart(title, labels, counts, percents, total):
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


def _frequency_sections(start_index, title, stats):
    headers = ["多选题选项", "N（计数）", "响应率（%）", "普及率（%）", "X²", "P"]
    return [
        _sec_table(
            f"输出结果{start_index}：多重响应频率分析表",
            headers,
            _frequency_rows(stats),
            note="注：***、**、*分别代表1%、5%、10%的显著性水平",
            description="上表为多重响应频率分析表，展示了选项的频率分布情况，包括个案数、响应率、普及率、显著性P值等。",
        ),
        _sec_charts(
            f"输出结果{start_index + 1}：响应率",
            [_category_chart(f"{title}响应率", stats["labels"], stats["counts"], stats["response_rates"], stats["total_responses"])],
            "上图以可视化的形式展示了多选题各问题选项响应率的频数分布情况。",
        ),
        _sec_charts(
            f"输出结果{start_index + 2}：普及率",
            [_category_chart(f"{title}普及率", stats["labels"], stats["counts"], stats["popularity_rates"], sum(stats["counts"]))],
            "上图以直方图的形式展示了各个问题选项普及率的分布情况。",
        ),
        _sec_charts(
            f"输出结果{start_index + 3}：帕累托图分析",
            [_pareto_chart(f"{title}帕累托图", stats["labels"], stats["counts"])],
            "帕累托图是“二八原则”的图形化体现，80%的问题是由20%的原因所致。",
        ),
    ]


def _cross_result(labels_a, labels_b, masks_a, masks_b):
    matrix = []
    for variable_a in masks_a.columns:
        row = []
        selected_a = masks_a[variable_a]
        for variable_b in masks_b.columns:
            row.append(int((selected_a & masks_b[variable_b]).sum()))
        matrix.append(row)

    row_totals = [sum(row) for row in matrix]
    col_totals = [
        sum(matrix[row_index][col_index] for row_index in range(len(matrix)))
        for col_index in range(len(labels_b))
    ]
    grand_total = int(sum(row_totals))
    chi2_value = None
    p_value = None
    if grand_total > 0 and len(matrix) >= 2 and len(labels_b) >= 2:
        try:
            chi2_value, p_value, _, _ = chi2_contingency(matrix)
        except ValueError:
            chi2_value, p_value = None, None

    headers = ["分组题项"] + labels_b + ["总数", "X²", "P"]
    rows = []
    for row_index, label_a in enumerate(labels_a):
        row_total = row_totals[row_index]
        row = [label_a]
        for value in matrix[row_index]:
            percent = value / row_total * 100 if row_total else 0
            row.append(f"{value}（{_fmt(percent, 3)}%）")
        row.append(str(row_total))
        row.append(_fmt(chi2_value, 3) if row_index == 0 else "")
        row.append((_fmt(p_value, 3) + _sig(p_value)) if row_index == 0 and p_value is not None else "")
        rows.append(row)
    rows.append(["总计"] + [str(value) for value in col_totals] + [str(grand_total), "", ""])
    return {
        "headers": headers,
        "rows": rows,
        "matrix": matrix,
        "row_totals": row_totals,
        "col_totals": col_totals,
        "grand_total": grand_total,
        "chi2": chi2_value,
        "p": p_value,
    }


def _cross_chart(labels_a, labels_b, matrix):
    return {
        "chartType": "crosstab_distribution",
        "title": "交叉图",
        "data": {
            "groupVariable": "多选题B",
            "xVariable": "多选题A",
            "groupLabels": labels_b,
            "xLabels": labels_a,
            "matrix": matrix,
            "total": int(sum(sum(row) for row in matrix)),
            "percentBase": "row",
            "defaultMode": "column",
            "defaultLabelMode": "count",
        },
    }


def run(df, params):
    """
    多选题与多选题交叉分析。

    @param df: 数据 DataFrame
    @param params: variables_a、variables_b 两组多选题拆分字段，count_value 为选中编码
    @return: 两组频率分析、交叉表和交叉图
    """
    variables_a = _resolve_cols(df, params.get("variables_a", []))
    variables_b = _resolve_cols(df, params.get("variables_b", []))
    count_value = params.get("count_value", "1")
    variable_labels = params.get("variable_labels", {})
    if len(variables_a) < 2 or len(variables_b) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "两组多选题变量都至少需要 2 个拆分字段。"}

    temp = df[variables_a + variables_b].copy()
    temp = temp[temp.notna().any(axis=1)]
    sample_size = int(len(temp))
    if sample_size == 0:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有可用样本。"}

    labels_a = [_label(variable_labels, variable) for variable in variables_a]
    labels_b = [_label(variable_labels, variable) for variable in variables_b]
    masks_a = _choice_mask(temp, variables_a, count_value)
    masks_b = _choice_mask(temp, variables_b, count_value)
    stats_a = _frequency_stats(labels_a, [int(masks_a[variable].sum()) for variable in variables_a], sample_size)
    stats_b = _frequency_stats(labels_b, [int(masks_b[variable].sum()) for variable in variables_b], sample_size)
    cross = _cross_result(labels_a, labels_b, masks_a, masks_b)

    sections = []
    sections.extend(_frequency_sections(1, "多选题A", stats_a))
    sections.extend(_frequency_sections(5, "多选题B", stats_b))
    sections.append(_sec_table(
        "输出结果9：多重响应频率交叉分析表",
        cross["headers"],
        cross["rows"],
        note="注：***、**、*分别代表1%、5%、10%的显著性水平",
        description="上表为多重响应频率交叉分析表，包括卡方检验值、显著性P值等。若P<0.05，则说明两组多选题之间存在差异性。",
    ))
    sections.append(_sec_smart(
        f"本次多选-多选交叉分析共纳入{sample_size}个有效样本。"
        f"卡方检验P值为{_fmt(cross['p'], 3) if cross['p'] is not None else '—'}，"
        f"{'在0.05水平上呈现显著性，说明两组多选题选项之间存在差异。' if cross['p'] is not None and cross['p'] <= 0.05 else '在0.05水平上不呈现显著性，说明两组多选题选项之间未见明显差异。'}"
    ))
    sections.append(_sec_charts(
        "输出结果10：交叉图",
        [_cross_chart(labels_a, labels_b, cross["matrix"])],
        "上图展示了两组多选题选项的频数分布情况。横轴为第二组多选题选项，图例为第一组多选题选项。",
    ))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {
        "name": METHOD_META["label"],
        "headers": cross["headers"],
        "rows": cross["rows"],
        "description": f"已完成两组多选题交叉分析，共比较 {len(variables_a) * len(variables_b)} 个选项组合。",
        "sections": sections,
    }
