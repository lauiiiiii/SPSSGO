# -*- coding: utf-8 -*-
# spssgo
from scipy import stats
from backend.analysis.common import *

METHOD_KEY = "category_summary"
METHOD_META = {'label': '分类汇总',
 'category': '常用方法',
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
              'type': 'multiple',
              'choices': [
                  'n',
                  '均值',
                  '计数',
                  '中位数',
                  '标准差',
                  '平均值±标准差',
                  '求和',
                  '最大值',
                  '最小值',
                  '25分位数',
                  '75分位数',
                  '90分位数',
                  '95分位数',
                  '99分位数',
                  '标准误',
                  '均值95% CI(LL)',
                  '均值95% CI(UL)',
                  '极差',
                  '四分位间距',
                  '方差',
                  '峰度',
                  '偏度',
              ],
              'default': ['均值']}],
 'param_builder': 'direct'}
METADATA_INJECTOR = "group_labels"

SUMMARY_TYPE_META = {
    "n": ("n", "count"),
    "均值": ("均值", "mean"),
    "计数": ("计数", "count"),
    "中位数": ("中位数", "median"),
    "标准差": ("标准差", "std"),
    "平均值±标准差": ("平均值±标准差", "mean_std"),
    "最大值": ("最大值", "max"),
    "最小值": ("最小值", "min"),
    "求和": ("求和", "sum"),
    "25分位数": ("25分位数", "p25"),
    "75分位数": ("75分位数", "p75"),
    "90分位数": ("90分位数", "p90"),
    "95分位数": ("95分位数", "p95"),
    "99分位数": ("99分位数", "p99"),
    "标准误": ("标准误", "se"),
    "均值95% CI(LL)": ("均值95% CI(LL)", "ci_ll"),
    "均值95% CI(UL)": ("均值95% CI(UL)", "ci_ul"),
    "极差": ("极差", "range"),
    "四分位间距": ("四分位间距", "iqr"),
    "方差": ("方差", "var"),
    "峰度": ("峰度", "kurtosis"),
    "偏度": ("偏度", "skewness"),
}

DETAIL_STAT_KEYS = [
    "n",
    "均值",
    "标准差",
    "平均值±标准差",
    "求和",
    "最小值",
    "最大值",
    "25分位数",
    "中位数",
    "75分位数",
    "90分位数",
    "95分位数",
    "99分位数",
    "标准误",
    "均值95% CI(LL)",
    "均值95% CI(UL)",
    "极差",
    "四分位间距",
    "方差",
    "峰度",
    "偏度",
]


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
    if stat_key == "mean_std":
        mean = clean.mean()
        std = clean.std() if len(clean) > 1 else np.nan
        return (float(mean), float(std))
    if stat_key == "mean":
        return float(clean.mean())
    if stat_key == "median":
        return float(clean.median())
    if stat_key == "std":
        return float(clean.std()) if len(clean) > 1 else np.nan
    if stat_key == "max":
        return float(clean.max())
    if stat_key == "min":
        return float(clean.min())
    if stat_key == "sum":
        return float(clean.sum())
    if stat_key == "p25":
        return float(clean.quantile(0.25))
    if stat_key == "p75":
        return float(clean.quantile(0.75))
    if stat_key == "p90":
        return float(clean.quantile(0.90))
    if stat_key == "p95":
        return float(clean.quantile(0.95))
    if stat_key == "p99":
        return float(clean.quantile(0.99))
    if stat_key == "se":
        return float(clean.std() / np.sqrt(len(clean))) if len(clean) > 1 else np.nan
    if stat_key == "ci_ll":
        return _mean_ci(clean)[0]
    if stat_key == "ci_ul":
        return _mean_ci(clean)[1]
    if stat_key == "range":
        return float(clean.max() - clean.min())
    if stat_key == "iqr":
        return float(clean.quantile(0.75) - clean.quantile(0.25))
    if stat_key == "var":
        return float(clean.var()) if len(clean) > 1 else np.nan
    if stat_key == "kurtosis":
        return float(clean.kurt()) if len(clean) > 3 else np.nan
    if stat_key == "skewness":
        return float(clean.skew()) if len(clean) > 2 else np.nan
    return float(clean.mean())


def _fmt_stat(value, stat_key):
    if stat_key == "count":
        return str(int(value)) if np.isfinite(value) else "0"
    if stat_key == "mean_std":
        mean, std = value if isinstance(value, tuple) else (np.nan, np.nan)
        return f"{_fmt(mean)}±{_fmt(std)}"
    return _fmt(value)


def _mean_ci(clean):
    if len(clean) <= 1:
        return (np.nan, np.nan)
    mean = clean.mean()
    se_value = clean.std() / np.sqrt(len(clean))
    margin = stats.t.ppf(0.975, len(clean) - 1) * se_value
    return (float(mean - margin), float(mean + margin))


# 图表中可切换的统计量，只保留适合对比的数值型指标
CHART_STAT_KEYS = [
    ("均值", "mean"),
    ("标准差", "std"),
    ("中位数", "median"),
    ("最大值", "max"),
    ("最小值", "min"),
    ("求和", "sum"),
]


def _summary_chart(summary_var, default_stat_label, all_stat_rows):
    chart_title = f"{summary_var}分类汇总"
    default_rows = all_stat_rows.get(default_stat_label, [])
    metrics = {}
    for stat_label, rows in all_stat_rows.items():
        metrics[stat_label] = [round(float(row["value"]), 4) for row in rows]
    return {
        "chartType": "metric_comparison",
        "title": chart_title,
        "data": {
            "displayTitle": chart_title,
            "metric": default_stat_label,
            "labels": [row["label"] for row in default_rows] if default_rows else [],
            "values": [round(float(row["value"]), 4) for row in default_rows] if default_rows else [],
            "defaultMode": "bar",
            "metrics": metrics,
        },
    }


def _is_chart_value(value):
    return isinstance(value, (int, float, np.integer, np.floating)) and np.isfinite(value)


def _selected_stats(raw_value):
    if isinstance(raw_value, list):
        names = raw_value
    elif raw_value:
        names = [raw_value]
    else:
        names = ["均值"]
    result = []
    seen = set()
    for name in names:
        if name not in SUMMARY_TYPE_META or name in seen:
            continue
        seen.add(name)
        label, key = SUMMARY_TYPE_META[name]
        result.append((label, key))
    return result or [SUMMARY_TYPE_META["均值"]]


def _display_stat_label(stat_label):
    return "平均值" if stat_label == "均值" else stat_label


def _build_detail_section(
    df,
    group_var,
    summary_vars,
    group_values,
    group_labels,
):
    headers = ["标题", "项"]
    headers.extend(_group_label(group_labels, value) for value in group_values)
    headers.append("汇总")
    rows = []

    for summary_var in summary_vars:
        for stat_index, stat_name in enumerate(DETAIL_STAT_KEYS):
            stat_label, stat_key = SUMMARY_TYPE_META[stat_name]
            row = [
                {"text": summary_var, "rowspan": len(DETAIL_STAT_KEYS)}
                if stat_index == 0 else None,
                stat_label,
            ]
            for group_value in group_values:
                grouped = df.loc[df[group_var] == group_value, summary_var]
                row.append(_fmt_stat(_calc_stat(grouped, stat_key), stat_key))
            row.append(_fmt_stat(_calc_stat(df[summary_var], stat_key), stat_key))
            rows.append([cell for cell in row if cell is not None])

    export_rows = []
    for summary_var in summary_vars:
        for stat_name in DETAIL_STAT_KEYS:
            stat_label, stat_key = SUMMARY_TYPE_META[stat_name]
            row = [summary_var, stat_label]
            for group_value in group_values:
                grouped = df.loc[df[group_var] == group_value, summary_var]
                row.append(_fmt_stat(_calc_stat(grouped, stat_key), stat_key))
            row.append(_fmt_stat(_calc_stat(df[summary_var], stat_key), stat_key))
            export_rows.append(row)

    section = _sec_table(
        "输出结果3：详细指标表",
        headers,
        rows,
        description=(
            "上表展示了各汇总变量在不同分类下的详细统计指标，"
            "可通过过滤指标筛选需要查看的指标。"
        ),
    )
    category_headers = [_group_label(group_labels, value) for value in group_values]
    section["headerRows"] = [
        [
            {"text": "标题", "rowspan": 2},
            {"text": "项", "rowspan": 2},
            {"text": group_var, "colspan": len(category_headers)},
            {"text": "汇总", "rowspan": 2},
        ],
        category_headers,
    ]
    section["bodyRowspanColumns"] = 1
    section["exportRows"] = export_rows
    section["filterTitle"] = "分类汇总分析结果-详细指标"
    section["rowFilter"] = {
        "label": "过滤指标",
        "columnIndex": 1,
        "choices": DETAIL_STAT_KEYS,
        "default": DETAIL_STAT_KEYS,
        "allLabel": "全选",
    }
    return section


def _build_summary_stat_rows(df, group_var, summary_vars, group_values, stat_key):
    rows = []
    for summary_var in summary_vars:
        row = [summary_var]
        for group_value in group_values:
            grouped = df.loc[df[group_var] == group_value, summary_var]
            row.append(_fmt_stat(_calc_stat(grouped, stat_key), stat_key))
        row.append(_fmt_stat(_calc_stat(df[summary_var], stat_key), stat_key))
        rows.append(row)
    return rows


def _build_base_section(
    df,
    group_var,
    summary_vars,
    group_values,
    group_labels,
    selected_stats,
):
    category_headers = [_group_label(group_labels, value) for value in group_values]
    headers = ["标题"] + category_headers + ["汇总"]
    stat_modes = []
    for stat_label, stat_key in selected_stats:
        stat_modes.append({
            "key": stat_key,
            "label": stat_label,
            "rows": _build_summary_stat_rows(
                df,
                group_var,
                summary_vars,
                group_values,
                stat_key,
            ),
        })

    first_mode = stat_modes[0]
    section = _sec_table(
        f"分类汇总分析结果-基础指标（{_display_stat_label(first_mode['label'])}）",
        headers,
        first_mode["rows"],
        description=(
            f"上表展示了汇总变量按{group_var}分组后的{first_mode['label']}结果，"
            "可用于对比不同类别下各指标的统计水平。"
        ),
    )
    section["displayModeTitle"] = "分类汇总分析结果-基础指标"
    section["headerRows"] = [
        [
            {"text": "标题", "rowspan": 2},
            {"text": group_var, "colspan": len(category_headers)},
            {"text": "汇总", "rowspan": 2},
        ],
        category_headers,
    ]
    if len(stat_modes) > 1:
        section["displayModes"] = stat_modes
        section["defaultDisplayMode"] = first_mode["key"]
    return section


def category_summary(df, params):
    """
    分类汇总：按分类变量对定量变量做分组描述统计

    @param df: 数据 DataFrame
    @param params: 包含 group_var, summary_vars, summary_type 的参数字典
    @return: 含 sections 的结果字典
    """
    group_var = params.get("group_var", "")
    summary_vars = [
        variable for variable in _resolve_cols(df, params.get("summary_vars", []))
        if variable != group_var
    ]
    group_labels = params.get("group_labels", {})
    selected_stats = _selected_stats(params.get("summary_type"))
    if group_var not in df.columns:
        return {
            "name": "分类汇总",
            "headers": [],
            "rows": [],
            "description": "分组变量不存在。",
        }
    if not summary_vars:
        return {
            "name": "分类汇总",
            "headers": [],
            "rows": [],
            "description": "未指定需要汇总的定量变量。",
        }

    group_values = sorted(
        pd.Series(df[group_var]).dropna().unique().tolist(),
        key=_sort_key,
    )
    if not group_values:
        return {
            "name": "分类汇总",
            "headers": [],
            "rows": [],
            "description": "没有可用于分类汇总的有效数据。",
        }

    headers = ["标题"] + [_group_label(group_labels, value) for value in group_values] + ["汇总"]
    rows = _build_summary_stat_rows(
        df,
        group_var,
        summary_vars,
        group_values,
        selected_stats[0][1],
    )
    charts = []
    smart_parts = []

    for summary_var in summary_vars:
        all_stat_rows = {}
        for stat_label, stat_key in CHART_STAT_KEYS:
            var_rows = []
            for group_value in group_values:
                mask = df[group_var] == group_value
                value = _calc_stat(df.loc[mask, summary_var], stat_key)
                var_rows.append({
                    "label": _group_label(group_labels, group_value),
                    "value": value,
                })
            finite_rows = [item for item in var_rows if _is_chart_value(item["value"])]
            if finite_rows:
                all_stat_rows[stat_label] = finite_rows
        if all_stat_rows:
            default_stat_label = selected_stats[0][0] if selected_stats[0][0] in all_stat_rows else list(all_stat_rows.keys())[0]
            charts.append(_summary_chart(summary_var, default_stat_label, all_stat_rows))
            default_rows = all_stat_rows[default_stat_label]
            max_group = max(default_rows, key=lambda item: item["value"])
            min_group = min(default_rows, key=lambda item: item["value"])
            smart_parts.append(
                f"在{summary_var}上，{max_group['label']}的{default_stat_label}最高"
                f"（{_fmt_stat(max_group['value'], SUMMARY_TYPE_META[default_stat_label][1])}），"
                f"{min_group['label']}的{default_stat_label}最低"
                f"（{_fmt_stat(min_group['value'], SUMMARY_TYPE_META[default_stat_label][1])}）"
            )

    sections = []
    stat_text = "、".join(label for label, _ in selected_stats)
    chart_desc = (
        f"上图展示了汇总变量按{group_var}分组后的{stat_text}结果，"
        "用于研究分组后定量数据的整体情况。"
    )
    if charts:
        sections.append(_sec_charts("输出结果1：分组汇总图", charts, chart_desc))

    sections.append(
        _build_base_section(
            df,
            group_var,
            summary_vars,
            group_values,
            group_labels,
            selected_stats,
        )
    )
    sections.append(
        _build_detail_section(
            df,
            group_var,
            summary_vars,
            group_values,
            group_labels,
        )
    )

    advice = (
        "分类汇总适合先观察不同类别下的指标分布情况；\n"
        f"第一：先查看各类别在不同汇总变量上的{stat_text}高低；\n"
        "第二：若某些类别差异明显，可进一步结合差异检验判断显著性；\n"
        "第三：如果样本存在缺失，可勾选输出缺失分析查看完整缺失情况。"
    )
    sections.append(_sec_advice(advice))

    smart = "；".join(smart_parts) + "。" if smart_parts else "分类汇总结果如表所示。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs([
        "[1] 盛骤，谢式千，潘承毅。概率论与数理统计 [M].5 版。北京：高等教育出版社，2019.",
        "[2] Feller W.An Introduction to Probability Theory and Its Applications:Vol.1 [M].3rd ed.New York:Wiley,1968.",
        "[3] 宗序平，姚玉兰。利用 Q-Q 图与 P-P 图快速检验数据的统计分布 [J]. 统计与决策，2010 (20):151-152.",
    ]))

    return {
        "name": f"分类汇总：按{group_var}分组",
        "headers": headers,
        "rows": rows,
        "description": smart,
        "sections": sections,
    }

run = category_summary
