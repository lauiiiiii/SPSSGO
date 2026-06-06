# -*- coding: utf-8 -*-
# 多配对样本 Friedman 检验：支持等级题/数值题统一转数值，输出正态性、主检验、图表和两两比较。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "friedman_test"
METHOD_META = {
    "label": "多配对样本Friedman检验",
    "category": "数据检验",
    "description": "比较三个及以上配对样本在秩次上的差异",
    "order": 50,
    "slots": [
        {
            "key": "variables",
            "label": "变量X",
            "type": "multiple",
            "accept": "any",
            "acceptLabel": "定量",
            "min": 3,
            "hint": "放入3个及以上配对测量变量；量表题会按数值转换后检验",
        },
    ],
    "options": [
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": True,
            "hint": "输出各变量正态性检验和直方图，便于和重复测量方差分析互相参照。",
        },
        {
            "key": "pairwise_compare",
            "label": "输出两两比较",
            "type": "checkbox",
            "default": True,
            "hint": "Friedman显著时，可参考Wilcoxon两两比较定位差异来源。",
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


def _signed_rank_z(diff):
    n = len(diff)
    ranks = stats.rankdata(np.abs(diff), method="average")
    w_plus = float(ranks[diff > 0].sum())
    expected = n * (n + 1) / 4
    _, counts = np.unique(np.abs(diff), return_counts=True)
    tie_correction = sum(count ** 3 - count for count in counts if count > 1)
    variance = n * (n + 1) * (2 * n + 1) / 24 - tie_correction / 48
    if variance <= 0:
        return np.nan
    return (w_plus - expected) / np.sqrt(variance)


def _effect_level(value):
    if not np.isfinite(value):
        return "无法判断"
    if value >= 0.5:
        return "大"
    if value >= 0.3:
        return "中等"
    if value >= 0.1:
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
        "label": label,
        "whiskerLow": round(float(non_outliers.min()) if len(non_outliers) else q1, 6),
        "q1": round(q1, 6),
        "median": round(float(values.median()), 6),
        "q3": round(q3, 6),
        "whiskerHigh": round(float(non_outliers.max()) if len(non_outliers) else q3, 6),
        "outliers": [round(float(value), 6) for value in values[(values < lower_fence) | (values > upper_fence)].tolist()],
    }


def _resolve_data(df, params):
    variables = _resolve_cols(df, _as_list(params.get("variables") or params.get("test_vars")))
    if len(variables) < 3:
        return [], None, "Friedman 检验至少需要 3 个配对变量。"
    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    temp = numeric.dropna()
    if len(temp) < 2:
        return variables, None, "有效样本不足，至少需要 2 行完整配对数据。"
    usable = [var for var in variables if temp[var].nunique(dropna=True) > 0]
    if len(usable) < 3:
        return variables, None, "至少需要 3 个可转为数值的有效变量。"
    return usable, temp[usable], ""


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


def _analysis_item(var, series, rank_mean):
    return {
        "var": var,
        "n": len(series),
        "mean": float(series.mean()),
        "std": float(series.std(ddof=1)) if len(series) > 1 else np.nan,
        "median": float(series.median()),
        "q1": float(series.quantile(0.25)),
        "q3": float(series.quantile(0.75)),
        "rank_mean": float(rank_mean),
        "series": series,
    }


def _pairwise_rows(items, pair_count):
    rows = []
    item_map = {item["var"]: item for item in items}
    for left, right in combinations(item_map.keys(), 2):
        diff = item_map[left]["series"] - item_map[right]["series"]
        nonzero_diff = diff[diff != 0]
        if len(nonzero_diff) < 1:
            stat, p_value, z_value = (np.nan, 1.0, np.nan)
        else:
            stat, p_value = wilcoxon(nonzero_diff)
            z_value = _signed_rank_z(nonzero_diff.to_numpy())
        adjusted_p = min(float(p_value) * pair_count, 1.0) if np.isfinite(p_value) else np.nan
        rows.append([
            f"{left} vs {right}",
            _fmt(item_map[left]["median"], 3),
            _fmt(item_map[right]["median"], 3),
            _fmt(item_map[left]["median"] - item_map[right]["median"], 3),
            _fmt(stat, 3),
            _fmt(z_value, 3),
            _p_with_sig(float(p_value)) if np.isfinite(p_value) else "—",
            _p_with_sig(adjusted_p) if np.isfinite(adjusted_p) else "—",
        ])
    return rows


def _config_section(variables, n, output_normality, pairwise_compare):
    return _sec_table(
        "分析配置",
        ["项目", "内容"],
        [
            ["算法", "多配对样本Friedman检验"],
            ["变量", "、".join(variables)],
            ["有效样本量", str(n)],
            ["正态性辅助", "输出" if output_normality else "不输出"],
            ["两两比较", "输出" if pairwise_compare else "不输出"],
            ["缺失值处理", "逐行剔除任一配对变量缺失或无法转为数值的样本"],
        ],
        description="本表记录本次Friedman检验的变量配置和缺失处理口径。",
    )


def _normality_section(items):
    return _sec_table(
        "输出结果1：正态性检验结果",
        ["变量名", "样本量", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"],
        [_normality_row(item["var"], item["series"]) for item in items],
        note="注：*、**、***、**** 分别代表10%、5%、1%、0.1%的显著性水平",
        description="上表展示各配对变量的描述统计和正态性检验结果，可辅助判断是否同步参考重复测量方差分析。",
    )


def _normality_chart_section(items):
    charts = []
    for item in items:
        chart = _normality_histogram_chart(item["var"], item["series"])
        if chart:
            charts.append(chart)
    if not charts:
        return None
    return _sec_charts(
        "输出结果2：正态性检验直方图",
        charts,
        "上图展示各配对变量的分布形态；若变量明显偏离正态，可优先参考Friedman检验结果。",
    )


def _summary_chart_section(items):
    boxes = [_box_summary(item["var"], item["series"]) for item in items]
    median_chart = {
        "chartType": "metric_comparison",
        "title": "Friedman检验中位数趋势图",
        "data": {
            "metric": "中位数",
            "labels": [item["var"] for item in items],
            "values": [round(item["median"], 6) for item in items],
            "defaultMode": "line",
            "fullRow": True,
        },
    }
    box_chart = {
        "chartType": "grouped_boxplot",
        "title": "Friedman检验箱线图",
        "data": {
            "variable": "配对变量",
            "boxes": boxes,
            "fullRow": True,
        },
    }
    return _sec_charts(
        "输出结果4：差异可视化图",
        [median_chart, box_chart],
        "上图通过中位数趋势和箱线图展示各配对变量的分布差异。",
    )


def _description_section(items):
    rows = [
        [
            item["var"],
            str(item["n"]),
            _fmt(item["mean"], 3),
            _fmt(item["std"], 3),
            _median_expr(item["series"]),
            _fmt(item["rank_mean"], 3),
        ]
        for item in items
    ]
    return _sec_table(
        "输出结果3：Friedman检验描述统计",
        ["名称", "样本量", "平均值", "标准差", "中位数M(P25，P75)", "平均秩"],
        rows,
        description="上表展示各配对变量的描述统计和平均秩，平均秩越高表示整体水平越高。",
    )


def _result_section(chi_square, df_value, p_value, kendall_w, n, k):
    return _sec_table(
        "输出结果5：Friedman检验结果",
        ["样本量", "变量个数", "χ²", "df", "p", "Kendall's W", "差异幅度"],
        [[str(n), str(k), _fmt(chi_square, 3), str(df_value), _p_with_sig(p_value), _fmt(kendall_w, 3), _effect_level(kendall_w)]],
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="Friedman检验用于判断三个及以上配对变量的秩次分布是否存在整体差异。",
    )


def _pairwise_section(items):
    pair_count = max(len(items) * (len(items) - 1) // 2, 1)
    return _sec_table(
        "输出结果6：两两比较结果",
        ["比较项", "变量1中位数", "变量2中位数", "中位数差值", "W", "Z", "p", "Bonferroni校正p"],
        _pairwise_rows(items, pair_count),
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="两两比较使用配对样本Wilcoxon符号秩检验，并提供Bonferroni校正后的p值辅助定位差异来源。",
    )


def _smart_text(items, p_value, kendall_w):
    sig_text = "呈现显著差异" if np.isfinite(p_value) and p_value < 0.05 else "未呈现显著差异"
    top = max(items, key=lambda item: item["rank_mean"])
    bottom = min(items, key=lambda item: item["rank_mean"])
    return (
        f"本次共分析{len(items)}个配对变量，Friedman检验结果{sig_text}"
        f"（p={_p_with_sig(p_value)}）。"
        f"平均秩最高的是{top['var']}（{_fmt(top['rank_mean'], 3)}），"
        f"最低的是{bottom['var']}（{_fmt(bottom['rank_mean'], 3)}）。"
        f"Kendall's W={_fmt(kendall_w, 3)}，差异幅度{_effect_level(kendall_w)}。"
    )


def friedman_test(df, params):
    """
    多配对样本 Friedman 检验。

    @param df: 数据 DataFrame
    @param params: variables/test_vars 为三个及以上配对测量变量
    @return: 正态性辅助、Friedman主检验、可视化和可选两两比较结果
    """
    variables, temp, error = _resolve_data(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    output_normality = _bool_param(params, "output_normality", True)
    pairwise_compare = _bool_param(params, "pairwise_compare", True)
    n, k = temp.shape
    ranks = temp.rank(axis=1, method="average")
    rank_means = ranks.mean(axis=0)
    chi_square, p_value = friedmanchisquare(*[temp[var] for var in variables])
    df_value = k - 1
    kendall_w = float(chi_square / (n * (k - 1))) if n > 0 and k > 1 else np.nan
    items = [_analysis_item(var, temp[var], rank_means[var]) for var in variables]

    sections = [_config_section(variables, n, output_normality, pairwise_compare)]
    if output_normality:
        sections.append(_normality_section(items))
        chart_section = _normality_chart_section(items)
        if chart_section:
            sections.append(chart_section)
    description_section = _description_section(items)
    result_section = _result_section(float(chi_square), df_value, float(p_value), kendall_w, n, k)
    sections.extend([
        description_section,
        _summary_chart_section(items),
        result_section,
    ])
    if pairwise_compare:
        sections.append(_pairwise_section(items))
    smart = _smart_text(items, float(p_value), kendall_w)
    sections.extend([
        _sec_advice(
            "多配对样本Friedman检验用于比较同一批样本在三个及以上条件、时间点或题项上的秩次差异；\n"
            "第一：检查各变量正态性，若明显不满足正态，可优先参考Friedman结果；\n"
            "第二：查看整体Friedman检验是否显著；\n"
            "第三：若整体显著，再结合平均秩和两两比较定位具体差异来源；\n"
            "第四：结合Kendall's W判断整体差异幅度。",
            title="分析步骤",
        ),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL + [
            "[3] Friedman M. The use of ranks to avoid the assumption of normality implicit in the analysis of variance[J]. Journal of the American Statistical Association, 1937, 32(200):675-701.",
        ]),
    ])
    return {
        "name": f"多配对样本Friedman检验_{'_'.join(variables[:3])}",
        "headers": description_section["headers"],
        "rows": description_section["rows"],
        "description": smart,
        "sections": sections,
    }


run = friedman_test
