# -*- coding: utf-8 -*-
# 配对样本 Wilcoxon 符号秩检验：支持多组配对输入，输出 SPSSAU 主表和 SPSSPRO 差值正态性辅助判断。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "wilcoxon_signed_rank_test"
METHOD_META = {
    "label": "配对样本Wilcoxon符号秩检验",
    "category": "数据检验",
    "description": "比较一组或多组配对样本在中位数水平上的差异",
    "order": 35,
    "slots": [
        {
            "key": "var1",
            "label": "变量X1",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入第一组配对测量变量",
        },
        {
            "key": "var2",
            "label": "变量X2",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入第二组配对测量变量，数量和顺序需与变量X1一致",
        },
    ],
    "options": [
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": True,
            "hint": "输出每组配对差值的正态性检验和直方图，便于和配对样本T检验互相参照。",
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


def _resolve_pairs(df, params):
    var1_list = _as_list(params.get("var1") or params.get("test_vars"))
    var2_list = _as_list(params.get("var2") or params.get("reference_vars"))
    if not var1_list or not var2_list:
        return [], "变量X1和变量X2均至少需要放入 1 个定量变量。"
    if len(var1_list) != len(var2_list):
        return [], "变量X1的输入项个数必须与变量X2输入项个数相同。"

    missing = [var for var in var1_list + var2_list if var not in df.columns]
    if missing:
        return [], f"变量不存在：{'、'.join(missing)}。"

    pairs = []
    for index, (var1, var2) in enumerate(zip(var1_list, var2_list), start=1):
        temp = df[[var1, var2]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(temp) < 1:
            continue
        s1 = temp[var1]
        s2 = temp[var2]
        raw_diff = s1 - s2
        nonzero_diff = raw_diff[raw_diff != 0]
        if len(nonzero_diff) < 1:
            continue
        pairs.append({
            "index": index,
            "var1": var1,
            "var2": var2,
            "label": f"{var1}配对{var2}",
            "short_label": f"{var1}-{var2}",
            "s1": s1,
            "s2": s2,
            "diff": raw_diff,
            "nonzero_diff": nonzero_diff,
            "n": len(raw_diff),
            "rank_n": len(nonzero_diff),
        })

    if not pairs:
        return [], "每组配对变量至少需要 1 个非零差值样本。"
    return pairs, ""


def _pair_stats(pair):
    s1 = pair["s1"]
    s2 = pair["s2"]
    diff = pair["diff"]
    nonzero_diff = pair["nonzero_diff"]
    stat, p_value = wilcoxon(nonzero_diff)
    z_value = _signed_rank_z(nonzero_diff.to_numpy())
    diff_std = float(diff.std(ddof=1)) if len(diff) > 1 else np.nan
    cohens_d = float(diff.mean() / diff_std) if np.isfinite(diff_std) and diff_std > 0 else np.nan
    sw_stat, sw_p, ks_stat, ks_p = _safe_normality(diff)
    diff_has_variance = np.isfinite(diff_std) and diff_std > 0
    return {
        **pair,
        "median1": float(s1.median()),
        "median2": float(s2.median()),
        "median_diff": float(diff.median()),
        "mean_diff": float(diff.mean()),
        "diff_std": diff_std,
        "w": float(stat),
        "z": float(z_value) if np.isfinite(z_value) else np.nan,
        "p": float(p_value),
        "cohens_d": cohens_d,
        "skew": float(stats.skew(diff, bias=False)) if diff_has_variance and len(diff) >= 3 else np.nan,
        "kurtosis": float(stats.kurtosis(diff, fisher=True, bias=False)) if diff_has_variance and len(diff) >= 4 else np.nan,
        "sw_stat": sw_stat,
        "sw_p": sw_p,
        "ks_stat": ks_stat,
        "ks_p": ks_p,
    }


def _config_section(items, output_normality):
    rows = [
        ["算法", "配对样本Wilcoxon符号秩检验"],
        ["配对关系", "；".join(item["label"] for item in items)],
        ["配对组数", str(len(items))],
        ["正态性辅助", "输出" if output_normality else "不输出"],
        ["缺失值处理", "每组配对变量逐行剔除缺失值；零差值不参与符号秩计算"],
    ]
    return _sec_table(
        "分析配置",
        ["项目", "内容"],
        rows,
        description="本表记录本次配对检验的变量关系和缺失处理口径。",
    )


def _normality_section(items):
    rows = []
    for item in items:
        rows.append([
            item["label"],
            str(item["n"]),
            _fmt(item["mean_diff"], 3),
            _fmt(item["diff_std"], 3),
            _fmt(item["skew"], 3),
            _fmt(item["kurtosis"], 3),
            _normality_expr(item["sw_stat"], item["sw_p"]),
            _normality_expr(item["ks_stat"], item["ks_p"]),
        ])
    return _sec_table(
        "输出结果1：配对差值正态性检验结果",
        ["变量名", "样本量", "平均值", "标准差", "偏度", "峰度", "S-W检验", "K-S检验"],
        rows,
        note="注：*、**、***、**** 分别代表10%、5%、1%、0.1%的显著性水平",
        description="上表展示样本配对差值的描述统计和正态性检验结果，用于判断是否可同步参考配对样本T检验。",
    )


def _normality_chart_section(items):
    charts = []
    for item in items:
        chart = _normality_histogram_chart(item["short_label"], item["diff"])
        if chart:
            charts.append(chart)
    if not charts:
        return None
    return _sec_charts(
        "输出结果2：正态性检验直方图",
        charts,
        "上图展示各组配对差值的分布形态；若差值明显偏离正态，可优先参考Wilcoxon符号秩检验。",
    )


def _result_section(items):
    rows = []
    for item in items:
        rows.append([
            item["label"],
            _median_expr(item["s1"]),
            _median_expr(item["s2"]),
            _fmt(item["median_diff"], 3),
            _fmt(item["z"], 3),
            _p_with_sig(item["p"]),
        ])
    section = _sec_table(
        "输出结果3：配对样本Wilcoxon分析结果",
        ["名称", "配对1", "配对2", "中位数差值(配对1-配对2)", "统计量Z值", "p"],
        rows,
        note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
        description="上表展示配对样本Wilcoxon符号秩检验结果，每一行对应一组配对变量。",
    )
    section["headerRows"] = [
        [
            {"text": "名称", "rowspan": 2},
            {"text": "配对中位数M(P25，P75)", "colspan": 2},
            {"text": "中位数差值(配对1-配对2)", "rowspan": 2},
            {"text": "统计量Z值", "rowspan": 2},
            {"text": "p", "rowspan": 2},
        ],
        ["配对1", "配对2"],
    ]
    return section


def _effect_section(items):
    rows = []
    for item in items:
        rows.append([
            item["label"],
            str(item["n"]),
            str(item["rank_n"]),
            _fmt(item["mean_diff"], 3),
            _fmt(item["diff_std"], 3),
            _fmt(abs(item["cohens_d"]), 3),
            _effect_level(item["cohens_d"]),
        ])
    return _sec_table(
        "深入分析-差异幅度指标",
        ["名称", "有效样本量", "非零差值样本量", "平均差值", "差值标准差", "Cohen's d值", "差异幅度"],
        rows,
        description="该表补充展示差值的描述统计和标准化差异幅度；Cohen's d仅作为差异大小参考，不替代Wilcoxon显著性结论。",
    )


def _smart_text(items):
    sig_items = [item for item in items if np.isfinite(item["p"]) and item["p"] < 0.05]
    parts = [f"本次共分析{len(items)}组配对数据，其中{len(sig_items)}组呈现显著差异（p<0.05）。"]
    for item in items:
        if np.isfinite(item["p"]) and item["p"] < 0.05:
            direction = "显著高于" if item["median_diff"] > 0 else "显著低于" if item["median_diff"] < 0 else "存在显著差异"
            conclusion = f"{item['var1']}相对{item['var2']}{direction}"
        else:
            conclusion = f"{item['var1']}与{item['var2']}未呈现显著差异"
        parts.append(
            f"{item['label']}：配对1中位数为{_fmt(item['median1'], 3)}，配对2中位数为{_fmt(item['median2'], 3)}，"
            f"中位数差值为{_fmt(item['median_diff'], 3)}；Z={_fmt(item['z'], 3)}，p={_p_with_sig(item['p'])}，"
            f"说明{conclusion}；Cohen's d={_fmt(abs(item['cohens_d']), 3)}，差异幅度{_effect_level(item['cohens_d'])}。"
        )
    return "\n".join(parts)


def wilcoxon_signed_rank_test(df, params):
    """
    配对样本 Wilcoxon 符号秩检验。

    @param df: 数据 DataFrame
    @param params: var1/var2 可传单个变量或等长变量列表，output_normality 控制差值正态性辅助输出
    @return: 多组配对 Wilcoxon 主结果、可选正态性检验和解读
    """
    pairs, error = _resolve_pairs(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    output_normality = _bool_param(params, "output_normality", True)
    items = [_pair_stats(pair) for pair in pairs]
    sections = [
        _config_section(items, output_normality),
    ]
    if output_normality:
        sections.append(_normality_section(items))
        chart_section = _normality_chart_section(items)
        if chart_section:
            sections.append(chart_section)
    result_section = _result_section(items)
    sections.extend([
        result_section,
        _sec_advice(
            "配对样本Wilcoxon符号秩检验研究配对数据的差异关系；\n"
            "第一：分析每组配对项是否呈现显著性；\n"
            "第二：如果呈现显著性，结合中位数差值判断差异方向；\n"
            "第三：若差值近似正态，可同步参考配对样本T检验；若差值明显非正态，优先参考Wilcoxon结果；\n"
            "第四：结合差异幅度指标进行总结。",
            title="分析步骤",
        ),
        _sec_smart(_smart_text(items)),
        _effect_section(items),
        _sec_refs(_REFS_GENERAL + [
            "[3] Rosner B, Glynn R J, Ting Lee M. Incorporation of Clustering Effects for the Wilcoxon Rank Sum Test: A Large-Sample Approach[J]. Biometrics, 2015, 59(4):1089-1098.",
        ]),
    ])
    title_suffix = "_".join(item["short_label"] for item in items[:3])
    return {
        "name": f"配对样本Wilcoxon符号秩检验_{title_suffix}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": _smart_text(items),
        "sections": sections,
    }


run = wilcoxon_signed_rank_test
