# -*- coding: utf-8 -*-
# 多独立样本 Kruskal-Wallis 检验：支持多个 Y 变量、正态性辅助、分组箱线图和两两比较。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "kruskal_wallis_test"
METHOD_META = {
    "label": "多独立样本Kruskal-Wallis检验",
    "category": "数据检验",
    "description": "比较独立组在一个或多个定量变量上的秩次分布差异",
    "order": 45,
    "slots": [
        {
            "key": "group_var",
            "label": "变量X",
            "type": "single",
            "accept": "any",
            "acceptLabel": "定类",
            "hint": "请输入分组变量",
        },
        {
            "key": "test_vars",
            "label": "变量Y",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "请输入变量",
        },
    ],
    "options": [
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": True,
            "hint": "输出各检验变量的正态性检验和直方图，便于和单因素方差分析互相参照。",
        },
        {
            "key": "pairwise_compare",
            "label": "输出两两比较",
            "type": "checkbox",
            "default": True,
            "hint": "整体检验显著时，可参考Mann-Whitney两两比较定位差异来源。",
        },
    ],
    "param_builder": "direct",
}


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _bool_param(params, key, default=False):
    value = params.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "否", "关闭"}
    return bool(value)


def _p_with_sig(p_value):
    if p_value is None or not np.isfinite(p_value):
        return "—"
    if p_value < 0.001:
        return f"{_fmt(p_value, 3)}****"
    if p_value < 0.01:
        return f"{_fmt(p_value, 3)}***"
    if p_value < 0.05:
        return f"{_fmt(p_value, 3)}**"
    if p_value < 0.1:
        return f"{_fmt(p_value, 3)}*"
    return _fmt(p_value, 3)


def _normality_expr(statistic, p_value):
    if statistic is None or p_value is None or not np.isfinite(statistic) or not np.isfinite(p_value):
        return "—"
    return f"{_fmt(statistic, 3)}({_p_with_sig(p_value)})"


def _safe_normality(series):
    sw_stat = sw_p = ks_stat = ks_p = np.nan
    if len(series) >= 3:
        std_value = series.std(ddof=1)
        if not np.isfinite(std_value) or std_value <= 0:
            return float(sw_stat), float(sw_p), float(ks_stat), float(ks_p)
        try:
            sample = series.sample(min(5000, len(series)), random_state=42) if len(series) > 5000 else series
            sw_stat, sw_p = shapiro(sample)
        except Exception:
            sw_stat, sw_p = (np.nan, np.nan)
        try:
            ks_stat, ks_p = stats.kstest((series - series.mean()) / std_value, "norm")
        except Exception:
            ks_stat, ks_p = (np.nan, np.nan)
    return float(sw_stat), float(sw_p), float(ks_stat), float(ks_p)


def _median_expr(series):
    return f"{_fmt(series.median(), 3)}({_fmt(series.quantile(0.25), 3)},{_fmt(series.quantile(0.75), 3)})"


def _effect_level(value):
    if not np.isfinite(value):
        return "无法判断"
    if value >= 0.14:
        return "大"
    if value >= 0.06:
        return "中等"
    if value >= 0.01:
        return "小"
    return "极小"


def _box_summary(label, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    non_outliers = values[(values >= lower_fence) & (values <= upper_fence)]
    return {
        "label": str(label),
        "whiskerLow": round(float(non_outliers.min()) if len(non_outliers) else q1, 6),
        "q1": round(q1, 6),
        "median": round(float(values.median()), 6),
        "q3": round(q3, 6),
        "whiskerHigh": round(float(non_outliers.max()) if len(non_outliers) else q3, 6),
        "outliers": [round(float(value), 6) for value in values[(values < lower_fence) | (values > upper_fence)].tolist()],
    }


def _normality_row(var, series):
    n = len(series)
    sw_stat, sw_p, ks_stat, ks_p = _safe_normality(series)
    std_value = float(series.std(ddof=1)) if n > 1 else np.nan
    has_variance = np.isfinite(std_value) and std_value > 0
    return [
        var,
        str(n),
        _fmt(series.mean(), 3),
        _fmt(std_value, 3),
        _fmt(stats.skew(series, bias=False), 3) if has_variance and n >= 3 else "—",
        _fmt(stats.kurtosis(series, fisher=True, bias=False), 3) if has_variance and n >= 4 else "—",
        _normality_expr(sw_stat, sw_p),
        _normality_expr(ks_stat, ks_p),
    ]


def _resolve_items(df, params):
    group_var = params.get("group_var", "")
    variables = _resolve_cols(df, _as_list(params.get("test_vars") or params.get("test_var") or params.get("variables")))
    if group_var not in df.columns:
        return [], "分组变量不存在。"
    if not variables:
        return [], "至少需要 1 个检验变量。"

    items = []
    skipped = []
    for var in variables:
        temp = df[[group_var, var]].copy()
        temp[var] = pd.to_numeric(temp[var], errors="coerce")
        temp = temp.dropna()
        groups = list(pd.Series(temp[group_var]).dropna().unique())
        group_series = {
            group_value: pd.to_numeric(temp.loc[temp[group_var] == group_value, var], errors="coerce").dropna()
            for group_value in groups
        }
        valid_groups = [group_value for group_value, values in group_series.items() if len(values) >= 1]
        if len(valid_groups) < 2:
            skipped.append(var)
            continue
        items.append({
            "var": var,
            "group_var": group_var,
            "group_values": valid_groups,
            "group_labels": [str(group_value) for group_value in valid_groups],
            "groups": {group_value: group_series[group_value] for group_value in valid_groups},
            "combined": pd.concat([group_series[group_value] for group_value in valid_groups]),
        })

    if not items:
        return [], f"分组变量【{group_var}】至少需要包含2个有效类别，且每个检验变量至少要有2个类别保留有效样本。"
    for item in items:
        item["skipped"] = skipped
    return items, ""


def _analysis_item(item):
    group_values = item["group_values"]
    samples = [item["groups"][group_value] for group_value in group_values]
    h_value, p_value = kruskal(*samples)
    n_total = int(sum(len(sample) for sample in samples))
    k = len(samples)
    ranks = pd.Series(stats.rankdata(pd.concat(samples), method="average"))
    cursor = 0
    group_rows = []
    for group_value, sample in zip(group_values, samples):
        group_ranks = ranks.iloc[cursor:cursor + len(sample)]
        cursor += len(sample)
        group_rows.append({
            "label": str(group_value),
            "series": sample,
            "n": len(sample),
            "mean": float(sample.mean()),
            "std": float(sample.std(ddof=1)) if len(sample) > 1 else np.nan,
            "median": float(sample.median()),
            "q1": float(sample.quantile(0.25)),
            "q3": float(sample.quantile(0.75)),
            "rank_mean": float(group_ranks.mean()),
        })
    epsilon_sq = (float(h_value) - k + 1) / (n_total - k) if n_total > k else np.nan
    epsilon_sq = max(float(epsilon_sq), 0.0) if np.isfinite(epsilon_sq) else np.nan
    return {
        **item,
        "group_rows": group_rows,
        "n": n_total,
        "k": k,
        "h": float(h_value),
        "df": k - 1,
        "p": float(p_value),
        "epsilon_sq": epsilon_sq,
    }


def _mann_whitney_z(g1, g2, u_value):
    n1, n2 = len(g1), len(g2)
    total_n = n1 + n2
    if n1 < 1 or n2 < 1 or total_n < 2:
        return np.nan
    _, counts = np.unique(pd.concat([g1, g2]).to_numpy(), return_counts=True)
    tie_sum = sum(count ** 3 - count for count in counts if count > 1)
    variance = n1 * n2 / 12 * ((total_n + 1) - tie_sum / (total_n * (total_n - 1)))
    if variance <= 0:
        return np.nan
    return (u_value - n1 * n2 / 2) / np.sqrt(variance)


def _cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    if n1 < 2 or n2 < 2:
        return np.nan
    pooled_var = ((n1 - 1) * g1.var(ddof=1) + (n2 - 1) * g2.var(ddof=1)) / (n1 + n2 - 2)
    pooled_std = np.sqrt(pooled_var) if pooled_var >= 0 else np.nan
    return (g1.mean() - g2.mean()) / pooled_std if np.isfinite(pooled_std) and pooled_std > 0 else np.nan


def _config_section(items, output_normality, pairwise_compare):
    skipped = items[0].get("skipped", []) if items else []
    rows = [
        ["算法", "多独立样本Kruskal-Wallis检验"],
        ["分组变量X", items[0]["group_var"] if items else ""],
        ["检验变量Y", "、".join(item["var"] for item in items)],
        ["组别", "、".join(items[0].get("group_labels", [])) if items else ""],
        ["正态性辅助", "输出" if output_normality else "不输出"],
        ["两两比较", "输出" if pairwise_compare else "不输出"],
        ["缺失值处理", "每个Y变量单独剔除分组变量或检验变量缺失的样本"],
    ]
    if skipped:
        rows.append(["跳过变量", "、".join(skipped)])
    return _sec_table(
        "分析配置",
        ["项目", "内容"],
        rows,
        description="本表记录本次Kruskal-Wallis检验的分组关系和变量配置。",
    )


def _normality_section(items):
    return _sec_table(
        "输出结果1：正态性检验结果",
        ["变量名", "样本量", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"],
        [_normality_row(item["var"], item["combined"]) for item in items],
        note="注：*、**、***、**** 分别代表10%、5%、1%、0.1%的显著性水平",
        description="上表展示各检验变量的描述统计和正态性检验结果，可辅助判断是否同步参考单因素方差分析。",
    )


def _normality_chart_section(items):
    charts = []
    for item in items:
        chart = _normality_histogram_chart(item["var"], item["combined"])
        if chart:
            charts.append(chart)
    if not charts:
        return None
    return _sec_charts(
        "输出结果2：正态性检验直方图",
        charts,
        "上图展示各检验变量的总体分布形态；若明显偏离正态，可优先参考Kruskal-Wallis检验结果。",
    )


def _description_section(items):
    rows = []
    for item in items:
        for group in item["group_rows"]:
            rows.append([
                item["var"],
                group["label"],
                str(group["n"]),
                _fmt(group["mean"], 3),
                _fmt(group["std"], 3),
                _median_expr(group["series"]),
                _fmt(group["rank_mean"], 3),
            ])
    return _sec_table(
        "输出结果3：分组描述统计",
        ["变量名", "组别", "样本量", "平均值", "标准差", "中位数M(P25，P75)", "平均秩"],
        rows,
        description="上表展示各检验变量在不同组别下的描述统计和平均秩，平均秩越高表示整体水平越高。",
    )


def _summary_chart_section(items):
    charts = []
    for item in items:
        labels = [group["label"] for group in item["group_rows"]]
        medians = [round(group["median"], 6) for group in item["group_rows"]]
        charts.append({
            "chartType": "metric_comparison",
            "title": f"{item['var']}分组中位数趋势图",
            "data": {
                "metric": "中位数",
                "labels": labels,
                "values": medians,
                "defaultMode": "line",
                "fullRow": True,
            },
        })
        charts.append({
            "chartType": "grouped_boxplot",
            "title": f"{item['var']}分组箱线图",
            "data": {
                "variable": item["var"],
                "boxes": [_box_summary(group["label"], group["series"]) for group in item["group_rows"]],
                "fullRow": True,
            },
        })
    return _sec_charts(
        "输出结果4：差异可视化图",
        charts,
        "上图通过分组中位数趋势和箱线图展示各组别之间的分布差异。",
    )


def _result_section(items):
    rows = [
        [
            item["var"],
            str(item["n"]),
            str(item["k"]),
            _fmt(item["h"], 3),
            str(item["df"]),
            _p_with_sig(item["p"]),
            _fmt(item["epsilon_sq"], 3),
            _effect_level(item["epsilon_sq"]),
        ]
        for item in items
    ]
    return _sec_table(
        "输出结果5：Kruskal-Wallis检验结果",
        ["变量名", "样本量", "组别数", "H", "df", "p", "ε²", "差异幅度"],
        rows,
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="Kruskal-Wallis检验用于判断独立组在秩次分布上是否存在整体差异。",
    )


def _pairwise_section(items):
    rows = []
    for item in items:
        pair_count = max(item["k"] * (item["k"] - 1) // 2, 1)
        for left, right in combinations(item["group_values"], 2):
            g1 = item["groups"][left]
            g2 = item["groups"][right]
            u_value, p_value = mannwhitneyu(g1, g2, alternative="two-sided")
            z_value = _mann_whitney_z(g1, g2, float(u_value))
            adjusted_p = min(float(p_value) * pair_count, 1.0) if np.isfinite(p_value) else np.nan
            cohens_d = _cohens_d(g1, g2)
            rows.append([
                f"{item['var']}：{left} vs {right}",
                _median_expr(g1),
                _median_expr(g2),
                _fmt(float(g1.median()) - float(g2.median()), 3),
                _fmt(float(u_value), 3),
                _fmt(z_value, 3),
                _p_with_sig(float(p_value)),
                _p_with_sig(adjusted_p),
                _fmt(abs(cohens_d), 3),
            ])
    return _sec_table(
        "输出结果6：两两比较结果",
        ["比较项", "组1中位数", "组2中位数", "中位数差值", "U", "Z", "p", "Bonferroni校正p", "Cohen's d"],
        rows,
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="两两比较使用Mann-Whitney U检验，并提供Bonferroni校正后的p值辅助定位差异来源。",
    )


def _smart_text(items):
    sig_items = [item for item in items if np.isfinite(item["p"]) and item["p"] < 0.05]
    parts = [f"本次共分析{len(items)}个检验变量，其中{len(sig_items)}个变量在多组之间呈现显著差异（p<0.05）。"]
    for item in items:
        top = max(item["group_rows"], key=lambda group: group["rank_mean"])
        bottom = min(item["group_rows"], key=lambda group: group["rank_mean"])
        sig_text = "呈现显著差异" if np.isfinite(item["p"]) and item["p"] < 0.05 else "未呈现显著差异"
        parts.append(
            f"{item['var']}：Kruskal-Wallis检验{sig_text}，"
            f"H={_fmt(item['h'], 3)}，df={item['df']}，p={_p_with_sig(item['p'])}；"
            f"平均秩最高的是{top['label']}组（{_fmt(top['rank_mean'], 3)}），"
            f"最低的是{bottom['label']}组（{_fmt(bottom['rank_mean'], 3)}）；"
            f"ε²={_fmt(item['epsilon_sq'], 3)}，差异幅度{_effect_level(item['epsilon_sq'])}。"
        )
    return "\n".join(parts)


def kruskal_wallis_test(df, params):
    """
    多独立样本 Kruskal-Wallis 检验。

    @param df: 数据 DataFrame
    @param params: group_var 为分组变量，test_vars/test_var 为一个或多个定量检验变量
    @return: 正态性辅助、分组描述、Kruskal-Wallis主检验、可视化和可选两两比较
    """
    resolved, error = _resolve_items(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    output_normality = _bool_param(params, "output_normality", True)
    pairwise_compare = _bool_param(params, "pairwise_compare", True)
    items = [_analysis_item(item) for item in resolved]

    sections = [_config_section(items, output_normality, pairwise_compare)]
    if output_normality:
        sections.append(_normality_section(items))
        chart_section = _normality_chart_section(items)
        if chart_section:
            sections.append(chart_section)
    description_section = _description_section(items)
    result_section = _result_section(items)
    sections.extend([
        description_section,
        _summary_chart_section(items),
        result_section,
    ])
    if pairwise_compare:
        sections.append(_pairwise_section(items))
    smart = _smart_text(items)
    sections.extend([
        _sec_advice(
            "多独立样本Kruskal-Wallis检验用于比较独立组在定量变量上的秩次分布差异；\n"
            "第一：确认变量X为分组变量，变量Y为定量变量；\n"
            "第二：查看正态性辅助结果，若数据明显非正态，可优先参考Kruskal-Wallis结果；\n"
            "第三：若整体检验p<0.05，说明至少有两组存在差异，再结合平均秩和两两比较定位具体差异来源；\n"
            "第四：结合ε²判断整体差异幅度。",
            title="分析步骤",
        ),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL + [
            "[3] Kruskal W H, Wallis W A. Use of ranks in one-criterion variance analysis[J]. Journal of the American Statistical Association, 1952, 47(260):583-621.",
        ]),
    ])
    return {
        "name": f"多独立样本Kruskal-Wallis检验_{'_'.join(item['var'] for item in items[:3])}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": smart,
        "sections": sections,
    }


run = kruskal_wallis_test
