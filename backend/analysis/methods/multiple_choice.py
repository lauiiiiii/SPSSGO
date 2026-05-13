# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "multiple_choice"
METHOD_META = {'label': '多选分析',
 'category': '问卷分析包',
 'description': '对同一多选题拆分后的多个选项变量进行选择频次统计',
 'order': 50,
 'slots': [{'key': 'variables',
            'label': '多选题变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一多选题的多个选项变量'}],
 'options': [{'key': 'count_value',
              'label': '计数值',
              'choices': ['1', '2', '0'],
              'choice_labels': {'1': '计数值，默认1'},
              'default': '1',
              'hint': '默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。'}],
 'param_builder': 'direct'}
METADATA_INJECTOR = "multiple_choice_labels"

def _count_value_mask(series, count_value):
    """
    按用户指定的计数值判断选中项。

    @param series: 选项列原始数据
    @param count_value: 被视为“选中”的编码值，默认 1
    @return: 布尔掩码，True 表示该样本选择了该选项
    """
    expected_text = str(count_value if count_value not in (None, "") else "1").strip()
    raw_text = series.astype(str).str.strip()
    numeric = pd.to_numeric(series, errors="coerce")
    expected_numeric = _safe_float(expected_text, None)
    if expected_numeric is None:
        return raw_text == expected_text
    return raw_text.eq(expected_text) | numeric.eq(expected_numeric)


def _multiple_choice_chart(title, labels, counts, percents, sample_size, variable):
    return {
        "chartType": "category_distribution",
        "title": title,
        "varName": variable,
        "data": {
            "variable": variable,
            "labels": labels,
            "counts": counts,
            "percents": percents,
            "total": int(sample_size),
        },
    }


def _pareto_chart(labels, counts):
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
        "title": "帕累托图",
        "data": {
            "isPareto": True,
            "metric": "频次",
            "displayTitle": "帕累托图",
            "labels": sorted_labels,
            "values": sorted_counts,
            "metrics": {
                "频次": sorted_counts,
                "累计百分比": cumulative,
            },
            "defaultMode": "bar",
        },
    }


def multiple_choice_analysis(df, params):
    """
    多选分析：针对多选题拆分后的多个选项变量统计选择频次

    @param df: 数据 DataFrame
    @param params: variables 为多选拆分变量，count_value 为计数编码，可选缺失按未选处理
    @return: 多重响应频率表、响应率/普及率图及帕累托图
    """
    variables = _resolve_cols(df, params.get("variables", []))
    variable_labels = params.get("variable_labels", {})
    count_value = params.get("count_value", "1")
    missing_as_unselected = params.get("missing_as_unselected") in (True, "true", "1", 1, "是")
    if len(variables) < 2:
        return {"name": "多选分析", "headers": [], "rows": [], "description": "需要至少2个多选题选项变量。"}

    valid_df = df[variables].copy()
    if not missing_as_unselected:
        valid_df = valid_df[valid_df.notna().any(axis=1)]
    sample_size = int(valid_df.shape[0])
    headers = ["多选题选项", "N（计数）", "响应率（%）", "普及率（%）", "X²", "P"]
    rows = []
    labels = []
    counts = []
    for var in variables:
        mask = _count_value_mask(valid_df[var], count_value)
        count = int(mask.sum())
        label = variable_labels.get(var, var)
        labels.append(label)
        counts.append(count)

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

    for index, label in enumerate(labels):
        rows.append([
            label,
            str(counts[index]),
            _fmt(response_rates[index], 3),
            _fmt(popularity_rates[index], 3),
            _fmt(chi2_value, 3) if index == 0 else "",
            (_fmt(p_value, 3) + _sig(p_value)) if index == 0 and p_value is not None else "",
        ])

    rows.append([
        "总计",
        str(total_responses),
        _fmt(100.0 if total_responses else 0.0, 3),
        _fmt(sum(popularity_rates), 3),
        "",
        "",
    ])

    picked = list(zip(labels, counts, response_rates, popularity_rates))
    top_label, top_count, top_response, top_popularity = max(picked, key=lambda item: item[1])
    low_label, low_count, low_response, low_popularity = min(picked, key=lambda item: item[1])

    sections = []
    sections.append(_sec_table(
        "输出结果1：多重响应频率分析表",
        headers,
        rows,
        note="注：***、**、*分别代表1%、5%、10%的显著性水平",
        description="上表展示多选题各选项的频率分布，包括计数、响应率、普及率及卡方拟合优度检验。"
    ))
    chart_variable = "多选题"
    sections.append(_sec_charts(
        "输出结果2：响应率",
        [_multiple_choice_chart("响应率", labels, counts, response_rates, total_responses, chart_variable)],
        "上图以图形形式展示各问题选项响应率的分布情况。"
    ))
    sections.append(_sec_charts(
        "输出结果3：普及率",
        [_multiple_choice_chart("普及率", labels, counts, popularity_rates, sample_size, chart_variable)],
        "上图以图形形式展示各问题选项普及率的分布情况。"
    ))
    sections.append(_sec_charts(
        "输出结果4：帕累托图",
        [_pareto_chart(labels, counts)],
        "帕累托图按照选择频次从高到低排序，并展示累计百分比。"
    ))
    advice = (
        f"本次按计数值 {count_value} 判定选中项；\n"
        f"{'本次已将缺失值按未选处理，等同于先把空值补为未选编码再统计；' if missing_as_unselected else '本次未将缺失值按未选处理，全空样本不会进入有效样本数；'}\n"
        "第一：响应率表示某选项占全部选择次数的比例，所有响应率合计为100%；\n"
        "第二：普及率表示某选项占有效样本的比例，多选题普及率合计通常会超过100%；\n"
        "第三：若卡方检验显著，说明各选项选择比例并不均匀。"
    )
    sections.append(_sec_advice(advice))
    conclusion = "未进行卡方显著性判断"
    if p_value is not None:
        conclusion = (
            f"卡方拟合优度检验的P值为{_fmt(p_value, 3)}，"
            f"{'在0.05水平上呈现显著性，拒绝原假设，各项选择比例存在差异' if p_value <= 0.05 else '在0.05水平上不呈现显著性，接受原假设，各项选择比例较均匀'}"
        )
    smart = (
        f"本次多选分析共纳入{sample_size}个有效样本，累计选择{total_responses}次。"
        f"{top_label}被选择次数最多（{top_count}次，响应率{_fmt(top_response, 3)}%，普及率{_fmt(top_popularity, 3)}%），"
        f"{low_label}被选择次数最少（{low_count}次，响应率{_fmt(low_response, 3)}%，普及率{_fmt(low_popularity, 3)}%）。"
        f"{conclusion}。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": "多选分析", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = multiple_choice_analysis
