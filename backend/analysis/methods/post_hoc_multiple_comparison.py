# -*- coding: utf-8 -*-
# 这里只放事后多重比较的业务编排和统计口径，图表只吐公共协议。
# 方法输出对齐 SPSSAU/SPSSPRO：先给方差分析总表，再给两两比较和均值趋势图。
import math

from backend.analysis.common import *

METHOD_KEY = "post_hoc_multiple_comparison"

POST_HOC_METHODS = [
    "LSD方法(默认)",
    "Scheffe",
    "Tukey",
    "Bonferroni校正",
    "sidak",
    "Tamhane T2(方差不齐)",
    "SNK Q检验",
    "Duncan检验",
    "Games-Howell(方差不齐)",
]

METHOD_ALIASES = {
    "LSD": "LSD方法(默认)",
    "LSD方法": "LSD方法(默认)",
    "Bonferroni": "Bonferroni校正",
    "Sidak": "sidak",
    "Tamhane T2": "Tamhane T2(方差不齐)",
    "Tamhane's T2": "Tamhane T2(方差不齐)",
    "Tamhane's T2(方差不齐)": "Tamhane T2(方差不齐)",
    "SNK": "SNK Q检验",
    "Duncan": "Duncan检验",
    "Games-Howell": "Games-Howell(方差不齐)",
}

METHOD_META = {'label': '事后多重比较',
 'category': '差异对比分析包',
 'description': '在方差分析显著后，对组间差异进行事后多重比较',
 'order': 35,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量（3组及以上）'},
           {'key': 'test_vars', 'label': '检验变量', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入需要比较的定量变量'}],
 'options': [{'key': 'method', 'label': '比较方法', 'choices': POST_HOC_METHODS, 'default': 'LSD方法(默认)'},
             {'key': 'use_letters', 'label': '字母标记法', 'type': 'checkbox', 'default': False},
             {'key': 'include_effect_size', 'label': '效应量', 'type': 'checkbox', 'default': False},
             {'key': 'show_p_marks', 'label': 'P值标识', 'type': 'checkbox', 'default': True}],
 'param_builder': 'direct'}


def _normalize_method(method):
    text = str(method or "LSD方法(默认)").strip()
    return METHOD_ALIASES.get(text, text if text in POST_HOC_METHODS else "LSD方法(默认)")


def _as_list(value):
    if isinstance(value, list):
        return [item for item in value if item]
    return [value] if value else []


def _safe_p(value):
    try:
        number = float(value)
        if not np.isfinite(number):
            return 1.0
        return min(max(number, 0.0), 1.0)
    except Exception:
        return 1.0


def _fmt_p(p, show_marks=True):
    return f"{_fmt(p, 3)}{_sig(p) if show_marks else ''}"


def _studentized_range_sf(q_value, k, df_error):
    try:
        return _safe_p(stats.studentized_range.sf(q_value, k, df_error))
    except Exception:
        try:
            from statsmodels.stats.libqsturng import psturng
            return _safe_p(float(psturng(q_value, k, df_error)))
        except Exception:
            # 这里必须兜底，不然后面全挂；退回保守的 t 分布近似。
            return _safe_p(2 * stats.t.sf(abs(q_value) / math.sqrt(2), df_error))


def _anova_summary(temp, group_var, test_var, group_keys):
    groups = {g: temp.loc[temp[group_var] == g, test_var] for g in group_keys}
    f_val, p_val = f_oneway(*[groups[g] for g in group_keys])
    grand_mean = temp[test_var].mean()
    ss_between = sum(len(groups[g]) * (groups[g].mean() - grand_mean) ** 2 for g in group_keys)
    ss_within = sum(((groups[g] - groups[g].mean()) ** 2).sum() for g in group_keys)
    df_between = len(group_keys) - 1
    df_within = len(temp) - len(group_keys)
    ms_within = ss_within / df_within if df_within > 0 else np.nan
    return {
        "groups": groups,
        "f": float(f_val),
        "p": _safe_p(p_val),
        "ss_within": float(ss_within),
        "df_between": df_between,
        "df_within": df_within,
        "ms_within": float(ms_within) if np.isfinite(ms_within) else np.nan,
        "eta_sq": float(ss_between / (ss_between + ss_within)) if (ss_between + ss_within) > 0 else np.nan,
    }


def _welch_pair(group_i, group_j):
    n_i = len(group_i)
    n_j = len(group_j)
    mean_i = float(group_i.mean())
    mean_j = float(group_j.mean())
    var_i = float(group_i.var(ddof=1)) if n_i > 1 else 0.0
    var_j = float(group_j.var(ddof=1)) if n_j > 1 else 0.0
    se = math.sqrt((var_i / n_i if n_i else 0) + (var_j / n_j if n_j else 0))
    if se <= 0:
        return mean_i, mean_j, mean_i - mean_j, 0.0, 1.0, 1
    t_val = (mean_i - mean_j) / se
    numerator = (var_i / n_i + var_j / n_j) ** 2
    denominator = 0.0
    if n_i > 1:
        denominator += (var_i / n_i) ** 2 / (n_i - 1)
    if n_j > 1:
        denominator += (var_j / n_j) ** 2 / (n_j - 1)
    df_pair = numerator / denominator if denominator > 0 else max(n_i + n_j - 2, 1)
    p_raw = 2 * stats.t.sf(abs(t_val), df_pair)
    return mean_i, mean_j, mean_i - mean_j, se, _safe_p(p_raw), df_pair


def _pair_p_value(method, group_i, group_j, mse, df_error, pair_count, rank_distance, group_count):
    mean_i, mean_j, diff, welch_se, welch_p, welch_df = _welch_pair(group_i, group_j)
    n_i = len(group_i)
    n_j = len(group_j)
    pooled_se = math.sqrt(mse * (1 / n_i + 1 / n_j)) if mse > 0 and n_i and n_j else welch_se
    if method in ["Tamhane T2(方差不齐)", "Games-Howell(方差不齐)"]:
        q_value = abs(diff) / welch_se * math.sqrt(2) if welch_se > 0 else 0.0
        p_value = _studentized_range_sf(q_value, group_count, welch_df)
        if method == "Tamhane T2(方差不齐)":
            p_value = 1 - (1 - welch_p) ** pair_count
        return mean_i, mean_j, diff, welch_se, _safe_p(p_value)
    if pooled_se <= 0:
        return mean_i, mean_j, diff, pooled_se, 1.0
    t_value = diff / pooled_se
    p_raw = _safe_p(2 * stats.t.sf(abs(t_value), df_error))
    if method == "Bonferroni校正":
        p_value = min(p_raw * pair_count, 1.0)
    elif method == "sidak":
        p_value = 1 - (1 - p_raw) ** pair_count
    elif method == "Scheffe":
        f_pair = (diff ** 2) / (mse * (1 / n_i + 1 / n_j)) if mse > 0 else 0.0
        p_value = stats.f.sf(f_pair / max(group_count - 1, 1), group_count - 1, df_error)
    elif method == "Tukey":
        q_value = abs(diff) / math.sqrt(mse / 2 * (1 / n_i + 1 / n_j)) if mse > 0 else 0.0
        p_value = _studentized_range_sf(q_value, group_count, df_error)
    elif method == "SNK Q检验":
        q_value = abs(diff) / math.sqrt(mse / 2 * (1 / n_i + 1 / n_j)) if mse > 0 else 0.0
        p_value = _studentized_range_sf(q_value, max(rank_distance, 2), df_error)
    elif method == "Duncan检验":
        q_value = abs(diff) / math.sqrt(mse / 2 * (1 / n_i + 1 / n_j)) if mse > 0 else 0.0
        # Duncan 是逐步放宽口径，这里用 rank distance 做范围校正，别改成全局 Tukey。
        p_value = 1 - (1 - _studentized_range_sf(q_value, max(rank_distance, 2), df_error)) ** max(rank_distance - 1, 1)
    else:
        p_value = p_raw
    return mean_i, mean_j, diff, pooled_se, _safe_p(p_value)


def _comparison_rows(method, anova, group_keys, show_p_marks=True):
    groups = anova["groups"]
    pair_count = len(list(combinations(group_keys, 2)))
    group_count = len(group_keys)
    mean_rank = {
        group: index + 1
        for index, group in enumerate(sorted(group_keys, key=lambda item: float(groups[item].mean())))
    }
    rows = []
    raw_rows = []
    for g_i, g_j in combinations(group_keys, 2):
        rank_distance = abs(mean_rank[g_i] - mean_rank[g_j]) + 1
        mean_i, mean_j, diff, se, p_value = _pair_p_value(
            method,
            groups[g_i],
            groups[g_j],
            anova["ms_within"],
            anova["df_within"],
            pair_count,
            rank_distance,
            group_count,
        )
        rows.append([
            str(g_i),
            str(g_j),
            _fmt(mean_i, 3),
            _fmt(mean_j, 3),
            _fmt(diff, 3),
            _fmt(se, 3),
            _fmt_p(p_value, show_p_marks),
        ])
        raw_rows.append({"i": str(g_i), "j": str(g_j), "mean_i": mean_i, "mean_j": mean_j, "diff": diff, "se": se, "p": p_value})
    return rows, raw_rows


def _letters_for_groups(group_keys, group_means, pair_rows):
    sorted_groups = sorted(group_keys, key=lambda item: group_means[item], reverse=True)
    sig_pairs = {frozenset([row["i"], row["j"]]) for row in pair_rows if row["p"] < 0.05}
    letters = {str(group): "" for group in sorted_groups}
    current_letters = []
    for group in sorted_groups:
        group_text = str(group)
        placed = False
        for letter in current_letters:
            members = [item for item, text in letters.items() if letter in text]
            if all(frozenset([group_text, member]) not in sig_pairs for member in members):
                letters[group_text] += letter
                placed = True
        if not placed:
            letter = chr(ord("A") + len(current_letters))
            current_letters.append(letter)
            letters[group_text] += letter
    return [[str(group), _fmt(group_means[group], 3), letters[str(group)]] for group in sorted_groups]


def _build_single_chart(group_var, summary):
    labels = [str(group) for group in summary["group_keys"]]
    values = [summary["means"].get(group, 0) for group in summary["group_keys"]]
    test_var = summary["test_var"]
    return {
        "chartType": "metric_comparison",
        "title": f"{group_var}和{test_var}事后多重比较对比图",
        "data": {
            "metric": test_var,
            "labels": labels,
            "values": values,
            "defaultMode": "line",
            "displayTitle": f"{group_var}和{test_var}事后多重比较对比图",
        },
    }


def _build_charts(group_var, summaries):
    labels = [str(group) for group in summaries[0]["group_keys"]]
    metrics = {}
    for summary in summaries:
        metrics[summary["test_var"]] = [summary["means"].get(group, 0) for group in summary["group_keys"]]
    charts = [_build_single_chart(group_var, summary) for summary in summaries]
    if len(summaries) <= 1:
        return charts
    first_metric = summaries[0]["test_var"]
    charts.append({
        "chartType": "metric_comparison",
        "title": f"{group_var}和所有项分析对比",
        "data": {
            "metric": first_metric,
            "labels": labels,
            "values": metrics[first_metric],
            "metrics": metrics,
            "multiSeries": True,
            "defaultMode": "line",
            "displayTitle": f"{group_var}和所有项分析对比",
        },
    })
    return charts


def _smart_text(method, summaries):
    lines = [f"使用{method}方法的事后多重比较结果显示："]
    for summary in summaries:
        order = ">".join([str(item) for item in sorted(summary["group_keys"], key=lambda group: summary["means"][group], reverse=True)])
        sig_pairs = [row for row in summary["pairs"] if row["p"] < 0.05]
        if sig_pairs:
            pair_text = "、".join([f"{row['i']}与{row['j']}" for row in sig_pairs[:6]])
            more = "等" if len(sig_pairs) > 6 else ""
            lines.append(f"对于变量{summary['test_var']}，均值大小排序为：{order}。其中{pair_text}{more}存在显著性差异。")
        else:
            lines.append(f"对于变量{summary['test_var']}，均值大小排序为：{order}。总体均值都不存在显著性差异。")
    return "\n".join(lines)


def run(df, params):
    group_var = params.get("group_var", "")
    test_vars = _as_list(params.get("test_vars") or params.get("test_var") or params.get("dependent"))
    method = _normalize_method(params.get("method", "LSD"))
    use_letters = bool(params.get("use_letters", False))
    include_effect_size = bool(params.get("include_effect_size", False))
    show_p_marks = bool(params.get("show_p_marks", True))

    if group_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量不存在。"}
    valid_vars = [var for var in test_vars if var in df.columns]
    if not valid_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "检验变量不存在。"}

    anova_rows = []
    comparison_rows = []
    letter_rows = []
    summaries = []
    for test_var in valid_vars:
        temp = df[[group_var, test_var]].copy()
        temp[test_var] = pd.to_numeric(temp[test_var], errors="coerce")
        temp = temp.dropna()
        group_keys = sorted(pd.Series(temp[group_var]).dropna().unique())
        if len(group_keys) < 3:
            continue
        anova = _anova_summary(temp, group_var, test_var, group_keys)
        group_means = {group: float(anova["groups"][group].mean()) for group in group_keys}
        group_sds = {group: float(anova["groups"][group].std()) for group in group_keys}
        group_ns = {group: int(len(anova["groups"][group])) for group in group_keys}
        anova_row = [
            test_var,
            *[f"{_fmt(group_means[group], 3)}±{_fmt(group_sds[group], 3)}(n={group_ns[group]})" for group in group_keys],
            _fmt(anova["f"], 3),
            _fmt_p(anova["p"], show_p_marks),
        ]
        if include_effect_size:
            anova_row.append(_fmt(anova["eta_sq"], 3))
        anova_rows.append(anova_row)
        rows, raw_rows = _comparison_rows(method, anova, group_keys, show_p_marks)
        for index, row in enumerate(rows):
            comparison_rows.append([test_var if index == 0 else "", *row])
        if use_letters:
            for index, row in enumerate(_letters_for_groups(group_keys, group_means, raw_rows)):
                letter_rows.append([test_var if index == 0 else "", *row])
        summaries.append({
            "test_var": test_var,
            "group_keys": group_keys,
            "means": group_means,
            "anova": anova,
            "pairs": raw_rows,
        })

    if not summaries:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "事后多重比较至少需要 3 个有效组。"}

    group_headers = [str(group) for group in summaries[0]["group_keys"]]
    anova_headers = ["名称", *group_headers, "F", "p"]
    if include_effect_size:
        anova_headers.append("η²")
    comparison_headers = ["名称", "(I)名称", "(J)名称", "(I)平均值", "(J)平均值", "差值(I-J)", "标准误", "p"]
    sections = [
        _sec_advice(
            "第一：先进行方差分析，判断分组变量下各分析项是否存在显著差异；\n"
            "第二：若方差分析p<0.05，则继续查看事后多重比较，定位具体哪两组差异显著；\n"
            "第三：方差齐时常用 LSD、Tukey、Bonferroni、Scheffe、SNK、Duncan；方差不齐时优先看 Tamhane T2 或 Games-Howell。",
            title="分析步骤",
        ),
        _sec_table(
            "输出结果1：方差分析结果",
            anova_headers,
            anova_rows,
            description="上表展示各组均值±标准差、样本量、F检验和显著性p值。若p<0.05，说明至少存在一组均值差异。",
        ),
        _sec_charts(
            "输出结果2：方差分析对比图",
            _build_charts(group_var, summaries),
            "上图展示各分析项在不同组别下的均值趋势，可先观察均值差异方向。",
        ),
        _sec_table(
            "输出结果3：事后多重比较结果",
            comparison_headers,
            comparison_rows,
            note="* p<0.05 ** p<0.01 *** p<0.001",
            description=f"上表使用{method}方法，对变量之间具体差异进行分析。",
        ),
        _sec_smart(_smart_text(method, summaries)),
        _sec_refs(_REFS_GENERAL),
    ]
    if use_letters and letter_rows:
        sections.insert(4, _sec_table(
            "深入分析：字母标记法",
            ["名称", "组别", "平均值", "字母标记"],
            letter_rows,
            description="同一变量下，含有相同字母的组别差异不显著，不含相同字母的组别差异显著。",
        ))

    return {
        "name": METHOD_META["label"],
        "headers": comparison_headers,
        "rows": comparison_rows,
        "description": "事后多重比较完成。",
        "sections": sections,
    }
