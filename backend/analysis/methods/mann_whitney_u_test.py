# -*- coding: utf-8 -*-
# 独立样本 Mann-Whitney 检验：支持分组变量两两比较和多个 Y 变量，输出 SPSSAU 主表和 SPSSPRO 正态性辅助判断。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "mann_whitney_u_test"
METHOD_META = {
    "label": "独立样本MannWhitney检验",
    "category": "数据检验",
    "description": "比较两个独立组在一个或多个定量变量上的秩次分布差异",
    "order": 40,
    "slots": [
        {
            "key": "group_var",
            "label": "变量X",
            "type": "single",
            "accept": "any",
            "acceptLabel": "定类",
            "hint": "放入分组变量；2组直接检验，3组及以上自动两两比较",
        },
        {
            "key": "test_vars",
            "label": "变量Y",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入需要逐个检验的定量变量",
        },
    ],
    "options": [
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": True,
            "hint": "输出各检验变量的正态性检验和直方图，便于和独立样本T检验互相参照。",
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
            standardized = (series - series.mean()) / std_value
            ks_stat, ks_p = stats.kstest(standardized, "norm")
        except Exception:
            ks_stat, ks_p = (np.nan, np.nan)
    return float(sw_stat), float(sw_p), float(ks_stat), float(ks_p)


def _median_expr(series):
    return f"{_fmt(series.median(), 3)}({_fmt(series.quantile(0.25), 3)},{_fmt(series.quantile(0.75), 3)})"


def _effect_level(value):
    if not np.isfinite(value):
        return "无法判断"
    abs_value = abs(value)
    if abs_value >= 0.8:
        return "大"
    if abs_value >= 0.5:
        return "中等"
    if abs_value >= 0.2:
        return "小"
    return "极小"


def _cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    if n1 < 2 or n2 < 2:
        return np.nan
    pooled_var = ((n1 - 1) * g1.var(ddof=1) + (n2 - 1) * g2.var(ddof=1)) / (n1 + n2 - 2)
    pooled_std = np.sqrt(pooled_var) if pooled_var >= 0 else np.nan
    return (g1.mean() - g2.mean()) / pooled_std if np.isfinite(pooled_std) and pooled_std > 0 else np.nan


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
        if len(groups) < 2:
            skipped.append(var)
            continue
        group_series = {
            group_value: pd.to_numeric(temp.loc[temp[group_var] == group_value, var], errors="coerce").dropna()
            for group_value in groups
        }
        valid_groups = [group_value for group_value, values in group_series.items() if len(values) >= 1]
        if len(valid_groups) < 2:
            skipped.append(var)
            continue
        for g1_value, g2_value in combinations(valid_groups, 2):
            items.append({
                "var": var,
                "group_var": group_var,
                "groups": [str(group_value) for group_value in valid_groups],
                "g1_value": g1_value,
                "g2_value": g2_value,
                "g1_label": str(g1_value),
                "g2_label": str(g2_value),
                "g1": group_series[g1_value],
                "g2": group_series[g2_value],
            })

    if not items:
        return [], f"分组变量【{group_var}】至少需要包含 2 个有效组，且每个检验变量至少要有两个组保留有效样本。"
    for item in items:
        item["skipped"] = skipped
    return items, ""


def _analysis_item(item):
    g1 = item["g1"]
    g2 = item["g2"]
    u_value, p_value = mannwhitneyu(g1, g2, alternative="two-sided")
    combined = pd.concat([g1, g2])
    ranks = pd.Series(stats.rankdata(combined, method="average"), index=combined.index)
    rank_mean1 = float(ranks.iloc[:len(g1)].mean())
    rank_mean2 = float(ranks.iloc[len(g1):].mean())
    z_value = _mann_whitney_z(g1, g2, float(u_value))
    cohens_d = _cohens_d(g1, g2)
    return {
        **item,
        "n1": len(g1),
        "n2": len(g2),
        "median1": float(g1.median()),
        "median2": float(g2.median()),
        "rank_mean1": rank_mean1,
        "rank_mean2": rank_mean2,
        "u": float(u_value),
        "z": float(z_value) if np.isfinite(z_value) else np.nan,
        "p": float(p_value),
        "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else np.nan,
        "combined": combined,
    }


def _config_section(items, output_normality):
    skipped = items[0].get("skipped", []) if items else []
    variables = list(dict.fromkeys(item["var"] for item in items))
    rows = [
        ["算法", "独立样本MannWhitney检验"],
        ["分组变量X", items[0]["group_var"] if items else ""],
        ["检验变量Y", "、".join(variables)],
        ["组别", "、".join(items[0].get("groups", [])) if items else ""],
        ["比较方式", "两组直接比较" if items and len(items[0].get("groups", [])) == 2 else "多组自动两两比较"],
        ["正态性辅助", "输出" if output_normality else "不输出"],
        ["缺失值处理", "每个Y变量单独剔除分组变量或检验变量缺失的样本"],
    ]
    if skipped:
        rows.append(["跳过变量", "、".join(skipped)])
    return _sec_table(
        "分析配置",
        ["项目", "内容"],
        rows,
        description="本表记录本次独立样本MannWhitney检验的分组关系和变量配置。",
    )


def _normality_section(items):
    rows = []
    seen_vars = set()
    for item in items:
        if item["var"] in seen_vars:
            continue
        seen_vars.add(item["var"])
        rows.append(_normality_row(item["var"], item["combined"]))
    return _sec_table(
        "输出结果1：正态性检验结果",
        ["变量名", "样本量", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"],
        rows,
        note="注：*、**、***、**** 分别代表10%、5%、1%、0.1%的显著性水平",
        description="上表展示各检验变量的描述统计和正态性检验结果，可辅助判断是否同步参考独立样本T检验。",
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
        "上图展示各检验变量的总体分布形态；若明显偏离正态，可优先参考Mann-Whitney检验结果。",
    )


def _result_section(items):
    rows = []
    for item in items:
        rows.append([
            f"{item['var']}：{item['g1_label']} vs {item['g2_label']}",
            _median_expr(item["g1"]),
            _median_expr(item["g2"]),
            _fmt(item["rank_mean1"], 3),
            _fmt(item["rank_mean2"], 3),
            _fmt(item["u"], 3),
            _fmt(item["z"], 3),
            _p_with_sig(item["p"]),
            _fmt(abs(item["cohens_d"]), 3),
        ])
    section = _sec_table(
        "输出结果3：MannWhitney U检验分析结果",
        ["名称", "组1", "组2", "组1秩均值", "组2秩均值", "U", "统计量Z值", "p", "Cohen's d"],
        rows,
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="上表展示每个检验变量在两个独立组之间的Mann-Whitney U检验结果。",
    )
    section["headerRows"] = [
        [
            {"text": "名称", "rowspan": 2},
            {"text": "组别中位数M(P25，P75)", "colspan": 2},
            {"text": "秩均值", "colspan": 2},
            {"text": "U", "rowspan": 2},
            {"text": "统计量Z值", "rowspan": 2},
            {"text": "p", "rowspan": 2},
            {"text": "Cohen's d", "rowspan": 2},
        ],
        ["组1", "组2", "组1", "组2"],
    ]
    return section


def _effect_section(items):
    rows = []
    for item in items:
        rows.append([
            f"{item['var']}：{item['g1_label']} vs {item['g2_label']}",
            f"{item['g1_label']} vs {item['g2_label']}",
            str(item["n1"]),
            str(item["n2"]),
            _fmt(item["median1"] - item["median2"], 3),
            _fmt(abs(item["cohens_d"]), 3),
            _effect_level(item["cohens_d"]),
        ])
    return _sec_table(
        "深入分析-差异幅度指标",
        ["名称", "组别", "组1样本量", "组2样本量", "中位数差值", "Cohen's d值", "差异幅度"],
        rows,
        description="该表补充展示样本量、中位数差值和标准化差异幅度；Cohen's d仅作为差异大小参考。",
    )


def _smart_text(items):
    sig_items = [item for item in items if np.isfinite(item["p"]) and item["p"] < 0.05]
    parts = [f"本次共分析{len(items)}个检验变量，其中{len(sig_items)}个变量在两组之间呈现显著差异（p<0.05）。"]
    for item in items:
        if np.isfinite(item["p"]) and item["p"] < 0.05:
            direction = "高于" if item["median1"] > item["median2"] else "低于" if item["median1"] < item["median2"] else "不同于"
            conclusion = f"{item['g1_label']}组在{item['var']}上的中位数显著{direction}{item['g2_label']}组"
        else:
            conclusion = f"{item['var']}在{item['g1_label']}组与{item['g2_label']}组之间未呈现显著差异"
        parts.append(
            f"{item['var']}：{item['g1_label']}组中位数为{_fmt(item['median1'], 3)}，"
            f"{item['g2_label']}组中位数为{_fmt(item['median2'], 3)}；"
            f"U={_fmt(item['u'], 3)}，Z={_fmt(item['z'], 3)}，p={_p_with_sig(item['p'])}，"
            f"说明{conclusion}；Cohen's d={_fmt(abs(item['cohens_d']), 3)}，差异幅度{_effect_level(item['cohens_d'])}。"
        )
    return "\n".join(parts)


def mann_whitney_u_test(df, params):
    """
    独立样本 Mann-Whitney U 检验。

    @param df: 数据 DataFrame
    @param params: group_var 为分组变量，test_vars/test_var 为一个或多个定量检验变量
    @return: 多变量 Mann-Whitney 主结果、可选正态性辅助和智能分析
    """
    resolved, error = _resolve_items(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    output_normality = _bool_param(params, "output_normality", True)
    items = [_analysis_item(item) for item in resolved]
    sections = [_config_section(items, output_normality)]
    if output_normality:
        sections.append(_normality_section(items))
        chart_section = _normality_chart_section(items)
        if chart_section:
            sections.append(chart_section)
    result_section = _result_section(items)
    sections.extend([
        result_section,
        _sec_advice(
            "独立样本MannWhitney检验用于比较独立组在定量变量上的秩次分布差异；\n"
            "第一：确认变量X为分组变量，变量Y为定量变量；若变量X超过2组，本方法会自动进行两两比较；\n"
            "第二：先查看正态性辅助结果，若数据明显非正态，可优先参考Mann-Whitney结果；\n"
            "第三：若p<0.05，说明对应两组存在显著差异，再结合中位数和秩均值判断差异方向；\n"
            "第四：结合Cohen's d等差异幅度指标进行总结。",
            title="分析步骤",
        ),
        _sec_smart(_smart_text(items)),
        _effect_section(items),
        _sec_refs(_REFS_GENERAL + [
            "[3] Rosner B, Glynn R J, Ting Lee M. Incorporation of Clustering Effects for the Wilcoxon Rank Sum Test: A Large-Sample Approach[J]. Biometrics, 2015, 59(4):1089-1098.",
        ]),
    ])
    title_suffix = "_".join(list(dict.fromkeys(item["var"] for item in items))[:3])
    return {
        "name": f"独立样本MannWhitney检验_{title_suffix}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": _smart_text(items),
        "sections": sections,
    }


run = mann_whitney_u_test
