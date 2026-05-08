# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "category_summary"
METHOD_META = {'label': '分类汇总',
 'category': '数据概览',
 'description': '按分类变量分组汇总一个或多个定量变量的统计量',
 'order': 40,
 'slots': [{'key': 'group_var',
            'label': '变量',
            'prefixLabel': '分组',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入用于分组汇总的分类变量'},
           {'key': 'summary_vars',
            'label': '变量',
            'prefixLabel': '汇总',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要按组汇总的定量变量'}],
 'options': [{'key': 'summary_type',
              'label': '类型',
              'choices': ['均值', '计数', '中位数', '标准差', '最大值', '最小值', '求和'],
              'default': '均值'}],
 'param_builder': 'direct'}
METADATA_INJECTOR = "group_labels"

SUMMARY_TYPE_META = {
    "均值": ("均值", "mean"),
    "计数": ("计数", "count"),
    "中位数": ("中位数", "median"),
    "标准差": ("标准差", "std"),
    "最大值": ("最大值", "max"),
    "最小值": ("最小值", "min"),
    "求和": ("求和", "sum"),
}


def _group_label(group_labels, value):
    text = str(value)
    if text in group_labels:
        return group_labels[text]
    numeric_text = _fmt(value, 0)
    return group_labels.get(numeric_text, text)


def _sort_key(value):
    number = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.notna(number):
        return (0, float(number))
    return (1, str(value))


def _calc_stat(series, stat_key):
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if stat_key == "count":
        return float(len(clean))
    if clean.empty:
        return np.nan
    if stat_key == "mean":
        return float(clean.mean())
    if stat_key == "median":
        return float(clean.median())
    if stat_key == "std":
        return float(clean.std()) if len(clean) > 1 else 0.0
    if stat_key == "max":
        return float(clean.max())
    if stat_key == "min":
        return float(clean.min())
    if stat_key == "sum":
        return float(clean.sum())
    return float(clean.mean())


def _fmt_stat(value, stat_key):
    if stat_key == "count":
        return str(int(value)) if np.isfinite(value) else "0"
    return _fmt(value)


def _summary_chart(summary_var, stat_label, rows):
    return {
        "chartType": "metric_comparison",
        "title": f"{summary_var}分类汇总{stat_label}",
        "data": {
            "metric": stat_label,
            "labels": [row["label"] for row in rows],
            "values": [round(float(row["value"]), 4) for row in rows],
            "defaultMode": "bar",
        },
    }

def category_summary(df, params):
    """
    分类汇总：按分类变量对定量变量做分组描述统计

    @param df: 数据 DataFrame
    @param params: 包含 group_var, summary_vars, group_labels 的参数字典
    @return: 含 sections 的结果字典
    """
    group_var = params.get("group_var", "")
    summary_vars = _resolve_cols(df, params.get("summary_vars", []))
    group_labels = params.get("group_labels", {})
    stat_label, stat_key = SUMMARY_TYPE_META.get(
        params.get("summary_type") or "均值",
        SUMMARY_TYPE_META["均值"],
    )
    if group_var not in df.columns:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "分组变量不存在。"}
    if not summary_vars:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "未指定需要汇总的定量变量。"}

    group_values = sorted(
        pd.Series(df[group_var]).dropna().unique().tolist(),
        key=_sort_key,
    )
    if not group_values:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "没有可用于分类汇总的有效数据。"}

    headers = [group_var] + summary_vars
    rows = []
    charts = []
    smart_parts = []
    stat_by_var = {}

    for summary_var in summary_vars:
        var_rows = []
        for group_value in group_values:
            mask = df[group_var] == group_value
            value = _calc_stat(df.loc[mask, summary_var], stat_key)
            var_rows.append({
                "label": _group_label(group_labels, group_value),
                "value": value,
            })
        stat_by_var[summary_var] = var_rows
        finite_rows = [item for item in var_rows if np.isfinite(item["value"])]
        if finite_rows:
            charts.append(_summary_chart(summary_var, stat_label, finite_rows))
            max_group = max(finite_rows, key=lambda item: item["value"])
            min_group = min(finite_rows, key=lambda item: item["value"])
            smart_parts.append(
                f"在{summary_var}上，{max_group['label']}的{stat_label}最高"
                f"（{_fmt_stat(max_group['value'], stat_key)}），"
                f"{min_group['label']}的{stat_label}最低"
                f"（{_fmt_stat(min_group['value'], stat_key)}）"
            )

    for row_index, group_value in enumerate(group_values):
        row = [_group_label(group_labels, group_value)]
        for summary_var in summary_vars:
            value = stat_by_var.get(summary_var, [])[row_index]["value"]
            row.append(_fmt_stat(value, stat_key))
        rows.append(row)

    sections = []
    chart_desc = (
        f"上图展示了汇总变量按{group_var}分组后的{stat_label}结果，"
        "用于研究分组后定量数据的整体情况。"
    )
    if charts:
        sections.append(_sec_charts("输出结果1：分组汇总图", charts, chart_desc))

    table_desc = (
        f"上表展示了汇总变量按{group_var}分组后的{stat_label}结果，"
        "可用于对比不同类别下各指标的统计水平。"
    )
    sections.append(_sec_table("输出结果2：分组汇总表", headers, rows, description=table_desc))

    advice = (
        "分类汇总适合先观察不同类别下的指标分布情况；\n"
        f"第一：先查看各类别在不同汇总变量上的{stat_label}高低；\n"
        "第二：若某些类别差异明显，可进一步结合差异检验判断显著性；\n"
        "第三：如果样本存在缺失，可勾选输出缺失分析查看完整缺失情况。"
    )
    sections.append(_sec_advice(advice))

    smart = "；".join(smart_parts) + "。" if smart_parts else "分类汇总结果如表所示。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {
        "name": f"分类汇总：按{group_var}分组",
        "headers": headers,
        "rows": rows,
        "description": smart,
        "sections": sections,
    }

run = category_summary
