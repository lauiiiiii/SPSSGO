# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "frequency"
METHOD_META = {'label': '频数分析',
 'category': '常用方法',
 'description': '统计各类别的频次和百分比分布',
 'order': 10,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'any',
            'min': 1,
            'hint': '放入需要统计频次的变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "frequency_labels"

def _frequency_variables(params):
    variables = params.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    legacy_variable = params.get("variable", "")
    if legacy_variable and legacy_variable not in variables:
        variables = [legacy_variable] + list(variables)
    return [variable for variable in variables if variable]


def _frequency_label(labels, value):
    if isinstance(value, str):
        return labels.get(value, value)
    text = str(value)
    try:
        numeric_value = float(value)
        int_text = str(int(numeric_value)) if numeric_value.is_integer() else text
    except (TypeError, ValueError, OverflowError):
        int_text = text
    return labels.get(int_text, labels.get(text, text))


def _frequency_chart(variable, rows, total):
    detail_rows = [row for row in rows if row[1] != "合计"]
    return {
        "chartType": "category_distribution",
        "title": f"{variable}柱状图",
        "varName": variable,
        "data": {
            "variable": variable,
            "labels": [row[1] for row in detail_rows],
            "counts": [int(row[2]) for row in detail_rows],
            "percents": [float(row[3]) for row in detail_rows],
            "total": int(total),
        },
    }


def frequency_table(df, params):
    """
    频率/百分比统计，支持多个变量合并输出

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典，兼容旧版 variable
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, _frequency_variables(params))
    if not variables:
        return {"name": "频数分析", "headers": [], "rows": [], "description": "未找到指定变量。"}

    labels_by_variable = params.get("labels_by_variable") or {}
    legacy_labels = params.get("labels", {})
    headers = ["名称", "选项", "频数", "百分比(%)"]
    rows = []
    charts = []
    smart_parts = []

    for variable in variables:
        labels = labels_by_variable.get(variable) or legacy_labels
        vc = df[variable].dropna().value_counts()
        try:
            vc = vc.sort_index()
        except TypeError:
            vc = vc.loc[sorted(vc.index, key=lambda value: str(value))]
        total = int(vc.sum())
        if total <= 0:
            rows.append([variable, "合计", "0", "0.0"])
            smart_parts.append(f"{variable}没有有效样本，暂不生成分布判断。")
            continue

        variable_rows = []
        first_row = True
        for val, cnt in vc.items():
            label = _frequency_label(labels, val)
            pct = cnt / total * 100
            variable_rows.append([variable if first_row else "", str(label), str(int(cnt)), _fmt(pct, 1)])
            first_row = False
        variable_rows.append(["", "合计", str(total), "100.0"])
        rows.extend(variable_rows)

        max_cat = vc.idxmax()
        min_cat = vc.idxmin()
        max_label = _frequency_label(labels, max_cat)
        min_label = _frequency_label(labels, min_cat)
        smart_parts.append(
            f"{variable}共{total}个有效样本，"
            f"{max_label}频次最高（{int(vc.max())}，占{_fmt(vc.max() / total * 100, 1)}%），"
            f"{min_label}频次最低（{int(vc.min())}，占{_fmt(vc.min() / total * 100, 1)}%）。"
        )
        charts.append(_frequency_chart(variable, variable_rows, total))

    sections = []
    sections.append(_sec_table(
        "输出结果1：频数分析结果",
        headers,
        rows,
        description="频数分析结果展示了各变量选项的频数和百分比。"
    ))
    sections.append(_sec_advice(
        "频数分析用于研究定类数据的分布情况。建议先查看各变量有效样本量，再重点关注占比较高或过低的选项，并结合问卷题意判断分布是否合理。"
    ))
    smart = "\n".join(smart_parts)
    sections.append(_sec_smart(smart))
    if charts:
        sections.append(_sec_charts(
            "输出结果2：频数分布图",
            charts,
            "上图以图形形式展示各变量的频数和百分比分布，可切换柱状图、条形图、饼图和环形图。"
        ))
    sections.append(_sec_refs(_REFS_GENERAL))

    name_suffix = "、".join(variables)
    return {
        "name": f"频数分析：{name_suffix}",
        "headers": headers,
        "rows": rows,
        "description": smart,
        "sections": sections,
    }

run = frequency_table
