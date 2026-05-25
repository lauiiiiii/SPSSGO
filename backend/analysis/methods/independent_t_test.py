# -*- coding: utf-8 -*-
# 独立样本 T 检验：对齐 SPSSPRO 的同列/不同列输入、正态性、方差齐性和 Welch 输出口径。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "independent_t_test"
METHOD_META = {
    "label": "独立样本T检验",
    "category": "差异对比分析包",
    "description": "比较两个独立组别在一个或多个定量变量上的均值差异",
    "slots": [
        {
            "key": "group_var",
            "label": "变量X",
            "type": "single",
            "accept": "categorical",
            "hint": "样本在同一列时放入二分类变量",
            "min": 0,
        },
        {
            "key": "test_vars",
            "label": "变量Y",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入需要检验差异的定量变量",
        },
    ],
    "options": [
        {
            "key": "data_format",
            "label": "检验数据形式",
            "choices": ["样本在同一列", "样本在不同列"],
            "default": "样本在同一列",
        },
    ],
    "param_builder": "direct",
}
METADATA_INJECTOR = "group_labels"


def _group_label(group_labels, value):
    text = str(value)
    if text in group_labels:
        return group_labels[text]
    try:
        numeric_text = str(int(float(value)))
        if numeric_text in group_labels:
            return group_labels[numeric_text]
    except Exception:
        pass
    return text


def _p_with_sig(p_value):
    if p_value is None or not np.isfinite(p_value):
        return "—"
    return f"{_fmt(p_value, 3)}{_sig(p_value)}"


def _test_expr(t_value, p_value):
    return f"T={_fmt(t_value, 3)}\nP={_p_with_sig(p_value)}"


def _effect_level(cohens_d):
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        return "大"
    if abs_d >= 0.5:
        return "中"
    if abs_d >= 0.2:
        return "小"
    return "极小"


def _normality_expr(statistic, p_value):
    if statistic is None or p_value is None or not np.isfinite(statistic) or not np.isfinite(p_value):
        return "—"
    return f"{_fmt(statistic, 3)}({_p_with_sig(p_value)})"


def _safe_normality(series):
    n = len(series)
    sw_stat = sw_p = ks_stat = ks_p = np.nan
    if n >= 3:
        try:
            sample = series.sample(min(5000, n), random_state=42) if n > 5000 else series
            sw_stat, sw_p = shapiro(sample)
        except Exception:
            sw_stat, sw_p = (np.nan, np.nan)
        try:
            std_value = series.std(ddof=1)
            if np.isfinite(std_value) and std_value > 0:
                ks_stat, ks_p = stats.kstest((series - series.mean()) / std_value, "norm")
        except Exception:
            ks_stat, ks_p = (np.nan, np.nan)
    return float(sw_stat), float(sw_p), float(ks_stat), float(ks_p)


def _cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    if n1 < 2 or n2 < 2:
        return np.nan
    pooled_var = ((n1 - 1) * g1.var(ddof=1) + (n2 - 1) * g2.var(ddof=1)) / (n1 + n2 - 2)
    pooled_std = np.sqrt(pooled_var) if pooled_var >= 0 else np.nan
    return (g1.mean() - g2.mean()) / pooled_std if np.isfinite(pooled_std) and pooled_std > 0 else np.nan


def _welch_df(g1, g2):
    n1, n2 = len(g1), len(g2)
    s1_sq = g1.var(ddof=1)
    s2_sq = g2.var(ddof=1)
    numerator = (s1_sq / n1 + s2_sq / n2) ** 2
    denominator = ((s1_sq / n1) ** 2) / (n1 - 1) + ((s2_sq / n2) ** 2) / (n2 - 1)
    return numerator / denominator if denominator > 0 else n1 + n2 - 2


def _series_stats(name, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    n = len(values)
    sw_stat, sw_p, ks_stat, ks_p = _safe_normality(values)
    return {
        "name": name,
        "values": values,
        "n": n,
        "median": float(values.median()) if n else np.nan,
        "mean": float(values.mean()) if n else np.nan,
        "std": float(values.std(ddof=1)) if n > 1 else np.nan,
        "skew": float(stats.skew(values, bias=False)) if n >= 3 else np.nan,
        "kurtosis": float(stats.kurtosis(values, fisher=True, bias=False)) if n >= 4 else np.nan,
        "sw_stat": sw_stat,
        "sw_p": sw_p,
        "ks_stat": ks_stat,
        "ks_p": ks_p,
    }


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


def _resolve_same_column(df, params):
    group_var = params.get("group_var", "")
    variables = _resolve_cols(df, params.get("test_vars", []) or params.get("dependent", []))
    if group_var not in df.columns:
        return [], "", f"分组变量 {group_var} 不存在。"
    if not variables:
        return [], "", "至少需要 1 个检验变量。"

    group_labels = params.get("group_labels", {})
    resolved = []
    for var in variables:
        temp = df[[group_var, var]].copy()
        temp[var] = pd.to_numeric(temp[var], errors="coerce")
        temp = temp.dropna()
        groups = list(pd.Series(temp[group_var]).dropna().unique())
        if len(groups) != 2:
            continue
        groups = sorted(groups, key=lambda value: str(value))
        g1_value, g2_value = groups[0], groups[1]
        g1 = pd.to_numeric(temp.loc[temp[group_var] == g1_value, var], errors="coerce").dropna()
        g2 = pd.to_numeric(temp.loc[temp[group_var] == g2_value, var], errors="coerce").dropna()
        if len(g1) < 2 or len(g2) < 2:
            continue
        resolved.append({
            "var": var,
            "group_var": group_var,
            "g1_label": _group_label(group_labels, g1_value),
            "g2_label": _group_label(group_labels, g2_value),
            "g1": g1,
            "g2": g2,
            "display_name": f"{group_var}-{var}",
        })
    if not resolved:
        return [], group_var, "字段为【{}】必须为两个类别，且每组至少保留 2 个有效样本。".format(group_var)
    return resolved, group_var, ""


def _resolve_different_columns(df, params):
    variables = _resolve_cols(df, params.get("test_vars", []) or params.get("dependent", []))
    if len(variables) != 2:
        return [], "", "样本在不同列时，检验变量必须且只能放入 2 个定量变量。"
    g1 = pd.to_numeric(df[variables[0]], errors="coerce").dropna()
    g2 = pd.to_numeric(df[variables[1]], errors="coerce").dropna()
    if len(g1) < 2 or len(g2) < 2:
        return [], "", "每组至少需要 2 个有效样本。"
    return [{
        "var": " / ".join(variables),
        "group_var": "样本",
        "g1_label": variables[0],
        "g2_label": variables[1],
        "g1": g1,
        "g2": g2,
        "display_name": f"{variables[0]}-{variables[1]}",
    }], "样本", ""


def _analysis_item(item):
    g1, g2 = item["g1"], item["g2"]
    n1, n2 = len(g1), len(g2)
    mean1, mean2 = float(g1.mean()), float(g2.mean())
    std1, std2 = float(g1.std(ddof=1)), float(g2.std(ddof=1))
    lev_stat, lev_p = levene(g1, g2, center="mean")
    equal_var = bool(lev_p > 0.05)
    t_equal, p_equal = ttest_ind(g1, g2, equal_var=True)
    t_welch, p_welch = ttest_ind(g1, g2, equal_var=False)
    df_equal = n1 + n2 - 2
    df_welch = _welch_df(g1, g2)
    cohens_d = _cohens_d(g1, g2)
    g1_stats = _series_stats(f"{item['var']}({item['g1_label']})", g1)
    g2_stats = _series_stats(f"{item['var']}({item['g2_label']})", g2)
    return {
        **item,
        "n1": n1,
        "n2": n2,
        "mean1": mean1,
        "mean2": mean2,
        "std1": std1,
        "std2": std2,
        "total_n": n1 + n2,
        "total_mean": float(pd.concat([g1, g2]).mean()),
        "total_std": float(pd.concat([g1, g2]).std(ddof=1)),
        "lev_stat": float(lev_stat),
        "lev_p": float(lev_p),
        "equal_var": equal_var,
        "t_equal": float(t_equal),
        "p_equal": float(p_equal),
        "t_welch": float(t_welch),
        "p_welch": float(p_welch),
        "df_equal": df_equal,
        "df_welch": float(df_welch),
        "mean_diff": mean1 - mean2,
        "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else np.nan,
        "g1_stats": g1_stats,
        "g2_stats": g2_stats,
    }


def _normality_rows(items):
    rows = []
    for item in items:
        combined = pd.concat([item["g1"], item["g2"]])
        stats_info = _series_stats(item["var"], combined)
        rows.append([
            item["var"],
            str(stats_info["n"]),
            _fmt(stats_info["median"], 3),
            _fmt(stats_info["mean"], 3),
            _fmt(stats_info["std"], 3),
            _fmt(stats_info["skew"], 3),
            _fmt(stats_info["kurtosis"], 3),
            _normality_expr(stats_info["sw_stat"], stats_info["sw_p"]),
            _normality_expr(stats_info["ks_stat"], stats_info["ks_p"]),
        ])
    return rows


def _homogeneity_section(items):
    first = items[0]
    headers = ["名称", first["g1_label"], first["g2_label"], "F", "P"]
    rows = []
    for item in items:
        rows.append([
            item["var"],
            _fmt(item["std1"], 3),
            _fmt(item["std2"], 3),
            _fmt(item["lev_stat"], 3),
            _p_with_sig(item["lev_p"]),
        ])
    section = _sec_table(
        "输出结果3：方差齐性检验",
        headers,
        rows,
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description=(
            "上表展示方差齐性结果，包括标准差、F 检验结果和显著性 P 值。"
            "P<0.05 时说明两组波动不一致，后续优先参考 Welch's T 检验。"
        ),
    )
    section["headerRows"] = [
        [
            {"text": "名称", "rowspan": 2},
            {"text": f"{first['group_var']}（标准差）", "colspan": 2},
            {"text": "F", "rowspan": 2},
            {"text": "P", "rowspan": 2},
        ],
        [first["g1_label"], first["g2_label"]],
    ]
    return section


def _mean_chart(items):
    first = items[0]
    if len(items) == 1:
        item = items[0]
        return {
            "chartType": "metric_comparison",
            "title": f"{item['display_name']}T检验均值对比图",
            "data": {
                "metric": "平均值",
                "labels": [item["g1_label"], item["g2_label"]],
                "values": [round(item["mean1"], 6), round(item["mean2"], 6)],
            },
        }
    return {
        "chartType": "metric_comparison",
        "title": f"{first['group_var']}-所有项T检验均值对比图",
        "data": {
            "metric": "平均值",
            "labels": [first["g1_label"], first["g2_label"]],
            "values": [round(items[0]["mean1"], 6), round(items[0]["mean2"], 6)],
            "defaultMode": "bar",
            "metrics": {
                item["var"]: [round(item["mean1"], 6), round(item["mean2"], 6)]
                for item in items
            },
            "multiSeries": True,
        },
    }


def _boxplot_chart(item):
    return {
        "chartType": "grouped_boxplot",
        "title": f"{item['display_name']}T检验均值对比图",
        "varName": item["var"],
        "data": {
            "variable": item["var"],
            "boxes": [
                _box_summary(item["g1_label"], item["g1"]),
                _box_summary(item["g2_label"], item["g2"]),
            ],
        },
    }


def _result_section(items):
    headers = ["变量名", "变量值", "样本量", "平均值", "标准差", "T检验", "Welch's T检验", "平均值差值", "Cohen's d值"]
    rows = []
    for item in items:
        selected_t = item["t_equal"] if item["equal_var"] else item["t_welch"]
        selected_p = item["p_equal"] if item["equal_var"] else item["p_welch"]
        rows.extend([
            [
                item["var"],
                item["g1_label"],
                str(item["n1"]),
                _fmt(item["mean1"], 3),
                _fmt(item["std1"], 3),
                _test_expr(item["t_equal"], item["p_equal"]),
                _test_expr(item["t_welch"], item["p_welch"]),
                _fmt(item["mean_diff"], 3),
                _fmt(abs(item["cohens_d"]), 3),
            ],
            [
                "",
                item["g2_label"],
                str(item["n2"]),
                _fmt(item["mean2"], 3),
                _fmt(item["std2"], 3),
                "",
                "",
                "",
                "",
            ],
            ["", "总计", str(item["total_n"]), _fmt(item["total_mean"], 3), _fmt(item["total_std"], 3), "", "", "", ""],
        ])
        item["selected_t"] = selected_t
        item["selected_p"] = selected_p
    return _sec_table(
        "输出结果5：独立样本T检验分析结果表",
        headers,
        rows,
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description=(
            "上表展示独立样本T检验结果，包括均值、标准差、T 检验、Welch's T 检验、"
            "显著性 P 值、平均值差值和效应量 Cohen's d。"
        ),
    )


def _smart_text(items):
    parts = []
    for item in items:
        p_value = item["p_equal"] if item["equal_var"] else item["p_welch"]
        method = "独立样本T检验" if item["equal_var"] else "Welch's T检验"
        significant = p_value < 0.05
        direction = "存在显著差异" if significant else "不存在显著差异"
        parts.append(
            f"{item['g1_label']}、{item['g2_label']}在{item['var']}上的均值分别为"
            f"{_fmt(item['mean1'], 3)}/{_fmt(item['mean2'], 3)}；"
            f"由于{'满足' if item['equal_var'] else '不满足'}方差齐性，采用{method}，"
            f"显著性结果P值为{_p_with_sig(p_value)}，说明两组在{item['var']}上{direction}；"
            f"Cohen's d={_fmt(abs(item['cohens_d']), 3)}，差异幅度{_effect_level(item['cohens_d'])}。"
        )
    return "\n".join(parts)


def run(df, params):
    """
    独立样本 T 检验。

    @param df: 数据 DataFrame
    @param params: 同列模式传 group_var + test_vars；不同列模式传 data_format + 2 个 test_vars
    @return: SPSSPRO 风格的正态性、方差齐性、均值图和 T 检验汇总
    """
    data_format = params.get("data_format") or "样本在同一列"
    if data_format == "样本在不同列":
        raw_items, group_var, error = _resolve_different_columns(df, params)
    else:
        raw_items, group_var, error = _resolve_same_column(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    items = [_analysis_item(item) for item in raw_items]
    normality_charts = []
    for item in items:
        chart = _normality_histogram_chart(item["var"], pd.concat([item["g1"], item["g2"]]))
        if chart:
            normality_charts.append(chart)

    normality_section = _sec_table(
        "输出结果1：正态性检验结果",
        ["变量名", "样本量", "中位数", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"],
        _normality_rows(items),
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description="上表展示定量变量的描述统计和正态性检验结果，用于判断独立样本T检验的适用性。",
    )

    sections = [
        _sec_advice(
            "1. 根据二分类变量对定量字段进行分组，分别查看总体分布是否近似正态。\n"
            "2. 进行方差齐性检验，P<0.05 时优先参考 Welch's T 检验。\n"
            "3. 若 T 检验呈现显著性，可结合均值差和 Cohen's d 判断差异方向与幅度。",
            title="分析步骤",
        ),
        normality_section,
    ]
    if normality_charts:
        sections.append(_sec_charts(
            "输出结果2：正态性检验直方图",
            normality_charts,
            "上图展示各检验变量的频数分布和正态拟合曲线，可辅助判断分布形态。",
        ))
    sections.extend([
        _homogeneity_section(items),
        _sec_charts(
            "输出结果4：独立样本T检验均值对比图",
            [_boxplot_chart(item) for item in items] + [_mean_chart(items)],
            "上表展示独立样本T检验的均值结果，通过比较均值，可以挖掘其差异关系。",
        ),
        _result_section(items),
        _sec_smart(_smart_text(items)),
        _sec_refs(_REFS_GENERAL + [
            "[3] Fisher Box, Joan. Guinness, Gosset, Fisher, and Small Samples. Statistical Science, 1987, 2(1):45-52.",
        ]),
    ])

    result_section = sections[-3]
    title_suffix = "_".join([item["var"] for item in items[:3]])
    return {
        "name": f"独立样本T检验_{group_var}_{title_suffix}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": _smart_text(items),
        "sections": sections,
    }


independent_t_test = run
