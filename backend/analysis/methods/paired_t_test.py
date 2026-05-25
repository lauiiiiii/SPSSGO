# -*- coding: utf-8 -*-
# 配对样本 T 检验：只处理同一对象两次测量的均值差异，输出对齐 SPSSAU/SPSSPRO。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "paired_t_test"
METHOD_META = {
    "label": "配对样本T检验",
    "category": "差异对比分析包",
    "description": "比较同一组受试者在两个条件/时间点上的均值差异",
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
    "options": [],
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


def _p_with_sig(p_value):
    if p_value is None or not np.isfinite(p_value):
        return "—"
    return f"{_fmt(p_value, 3)}{_sig(p_value)}"


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


def _effect_level(cohens_d):
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        return "大"
    if abs_d >= 0.5:
        return "中等"
    if abs_d >= 0.2:
        return "小"
    return "极小"


def _resolve_pairs(df, params):
    var1_list = _as_list(params.get("var1") or params.get("test_vars"))
    var2_list = _as_list(params.get("var2") or params.get("reference_vars"))
    if not var1_list or not var2_list:
        return [], "变量X1和变量X2均至少需要放入 1 个定量变量。"
    if len(var1_list) != len(var2_list):
        return [], "变量X1的输入项个数必须与变量X2输入项个数相同。"

    pairs = []
    missing = [var for var in var1_list + var2_list if var not in df.columns]
    if missing:
        return [], f"变量不存在：{'、'.join(missing)}。"

    for index, (var1, var2) in enumerate(zip(var1_list, var2_list), start=1):
        temp = df[[var1, var2]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(temp) < 2:
            continue
        s1 = temp[var1]
        s2 = temp[var2]
        diff = s1 - s2
        pairs.append({
            "index": index,
            "var1": var1,
            "var2": var2,
            "label": f"{var1}配对{var2}",
            "short_label": f"{var1}-{var2}",
            "s1": s1,
            "s2": s2,
            "diff": diff,
            "n": len(diff),
        })

    if not pairs:
        return [], "每组配对变量至少需要 2 个有效样本。"
    return pairs, ""


def _pair_stats(pair):
    s1, s2, diff = pair["s1"], pair["s2"], pair["diff"]
    n = pair["n"]
    t_val, p_val = ttest_rel(s1, s2)
    diff_std = float(diff.std(ddof=1)) if n > 1 else np.nan
    se_diff = diff_std / np.sqrt(n) if n > 1 and np.isfinite(diff_std) else np.nan
    mean_diff = float(diff.mean())
    df_value = n - 1
    t_crit = stats.t.ppf(0.975, df_value) if df_value > 0 else np.nan
    ci_low = mean_diff - t_crit * se_diff if np.isfinite(t_crit) and np.isfinite(se_diff) else np.nan
    ci_high = mean_diff + t_crit * se_diff if np.isfinite(t_crit) and np.isfinite(se_diff) else np.nan
    cohens_d = mean_diff / diff_std if np.isfinite(diff_std) and diff_std > 0 else np.nan
    corr, corr_p = pearsonr(s1, s2) if n >= 3 and s1.nunique() > 1 and s2.nunique() > 1 else (np.nan, np.nan)
    sw_stat, sw_p, ks_stat, ks_p = _safe_normality(diff)
    return {
        **pair,
        "mean1": float(s1.mean()),
        "std1": float(s1.std(ddof=1)),
        "mean2": float(s2.mean()),
        "std2": float(s2.std(ddof=1)),
        "mean_diff": mean_diff,
        "diff_std": diff_std,
        "se_diff": se_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "t": float(t_val),
        "p": float(p_val),
        "df": df_value,
        "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else np.nan,
        "corr": float(corr) if np.isfinite(corr) else np.nan,
        "corr_p": float(corr_p) if np.isfinite(corr_p) else np.nan,
        "skew": float(stats.skew(diff, bias=False)) if n >= 3 else np.nan,
        "kurtosis": float(stats.kurtosis(diff, fisher=True, bias=False)) if n >= 4 else np.nan,
        "sw_stat": sw_stat,
        "sw_p": sw_p,
        "ks_stat": ks_stat,
        "ks_p": ks_p,
    }


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
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description="上表展示样本配对差值的描述统计和正态性检验结果，用于判断配对样本T检验的适用性。",
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
        "上图展示各组配对差值的频数分布和正态拟合曲线，可辅助判断差值是否近似正态。",
    )


def _result_section(items):
    headers = ["配对变量", "配对1", "配对2", "配对差值（配对1-配对2）", "t", "df", "P", "Cohen's d"]
    rows = []
    for item in items:
        rows.append([
            item["label"],
            f"{_fmt(item['mean1'], 3)}±{_fmt(item['std1'], 3)}",
            f"{_fmt(item['mean2'], 3)}±{_fmt(item['std2'], 3)}",
            f"{_fmt(item['mean_diff'], 3)}±{_fmt(item['diff_std'], 3)}",
            _fmt(item["t"], 3),
            str(item["df"]),
            _p_with_sig(item["p"]),
            _fmt(abs(item["cohens_d"]), 3),
        ])
    section = _sec_table(
        "输出结果3：配对样本T检验结果",
        headers,
        rows,
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description="上表展示配对样本T检验结果，包括均值、标准差、t值、自由度、显著性P值和效应量Cohen's d。",
    )
    section["headerRows"] = [
        [
            {"text": "配对变量", "rowspan": 2},
            {"text": "平均值±标准差", "colspan": 3},
            {"text": "t", "rowspan": 2},
            {"text": "df", "rowspan": 2},
            {"text": "P", "rowspan": 2},
            {"text": "Cohen's d", "rowspan": 2},
        ],
        ["配对1", "配对2", "配对差值（配对1-配对2）"],
    ]
    return section


def _effect_section(items):
    rows = []
    for item in items:
        rows.append([
            item["label"],
            _fmt(item["mean_diff"], 3),
            f"{_fmt(item['ci_low'], 3)} ~ {_fmt(item['ci_high'], 3)}",
            str(item["df"]),
            _fmt(item["diff_std"], 3),
            _fmt(abs(item["cohens_d"]), 3),
        ])
    return _sec_table(
        "深入分析-效应量指标",
        ["名称", "平均值差值", "差值95% CI", "df", "差值标准差", "Cohen's d值"],
        rows,
        description=(
            "上表补充展示均值差值的95%置信区间和效应量。"
            "Cohen's d绝对值越大，说明配对差异幅度越大。"
        ),
    )


def _detail_section(items):
    rows = []
    for item in items:
        rows.extend([
            [
                f"配对{item['index']}",
                item["var1"],
                _fmt(item["mean1"], 3),
                _fmt(item["std1"], 3),
                _fmt(item["mean_diff"], 3),
                _fmt(item["t"], 3),
                _p_with_sig(item["p"]),
            ],
            [
                "",
                item["var2"],
                _fmt(item["mean2"], 3),
                _fmt(item["std2"], 3),
                "",
                "",
                "",
            ],
        ])
    return _sec_table(
        "配对T检验分析结果-详细格式",
        ["配对编号", "项", "平均值", "标准差", "平均值差值", "t", "p"],
        rows,
        note="注：***、**、* 分别代表1%、5%、10%的显著性水平",
        description="上表按配对编号展开每个变量的均值和标准差，便于核对具体配对关系。",
    )


def _correlation_section(items):
    rows = [
        [item["label"], str(item["n"]), _fmt(item["corr"], 3), _p_with_sig(item["corr_p"])]
        for item in items
    ]
    return _sec_table(
        "配对样本相关",
        ["配对变量", "N", "相关系数", "P"],
        rows,
        description="该表补充展示两次测量之间的 Pearson 相关，便于判断配对关系强弱。",
    )


def _smart_text(items):
    significant_count = sum(1 for item in items if np.isfinite(item["p"]) and item["p"] < 0.05)
    parts = [
        f"本次共分析{len(items)}组配对数据，其中{significant_count}组呈现显著差异（P<0.05）。"
    ]
    for item in items:
        significant = np.isfinite(item["p"]) and item["p"] < 0.05
        if significant:
            conclusion = f"{item['var1']}{'显著低于' if item['mean_diff'] < 0 else '显著高于'}{item['var2']}"
        else:
            conclusion = f"{item['var1']}与{item['var2']}未呈现显著差异"
        parts.append(
            f"{item['var1']}与{item['var2']}：配对1均值为{_fmt(item['mean1'], 3)}，"
            f"配对2均值为{_fmt(item['mean2'], 3)}，均值差为{_fmt(item['mean_diff'], 3)}；"
            f"t={_fmt(item['t'], 3)}，df={item['df']}，P={_p_with_sig(item['p'])}，"
            f"说明{conclusion}；"
            f"Cohen's d={_fmt(abs(item['cohens_d']), 3)}，差异幅度{_effect_level(item['cohens_d'])}。"
        )
    return "\n".join(parts)


def paired_t_test(df, params):
    """
    配对样本 T 检验。

    @param df: 数据 DataFrame
    @param params: var1/var2 可传单个变量或等长变量列表
    @return: SPSSAU/SPSSPRO 风格的正态性、检验结果、效应量和详细表
    """
    pairs, error = _resolve_pairs(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    items = [_pair_stats(pair) for pair in pairs]
    sections = [
        _sec_advice(
            "1. 配对样本T检验研究同一对象在两个时间点、两种条件或前后测之间的均值差异。\n"
            "2. 先检查配对差值的正态性；若差值明显偏离正态，可考虑配对样本Wilcoxon符号秩检验。\n"
            "3. 若P<0.05，说明该组配对变量存在显著差异；再结合均值差、95%CI和Cohen's d判断方向与幅度。",
            title="分析步骤",
        ),
        _normality_section(items),
    ]
    chart_section = _normality_chart_section(items)
    if chart_section:
        sections.append(chart_section)
    sections.extend([
        _result_section(items),
        _sec_advice(
            "配对样本T检验关注成对数据的差异关系。\n"
            "第一：分析每组配对项之间是否呈现显著差异；\n"
            "第二：如果呈现显著性，可结合平均值差值描述具体差异方向；\n"
            "第三：结合Cohen's d判断差异幅度，0.2、0.5、0.8通常可作为小、中、大效应参考点。",
        ),
        _sec_smart(_smart_text(items)),
        _effect_section(items),
        _detail_section(items),
        _correlation_section(items),
        _sec_refs(_REFS_GENERAL + [
            "[3] Fisher Box, Joan. Guinness, Gosset, Fisher, and Small Samples. Statistical Science, 1987, 2(1):45-52.",
        ]),
    ])

    result_section = next(section for section in sections if section["title"] == "输出结果3：配对样本T检验结果")
    title_suffix = "_".join([item["short_label"] for item in items[:3]])
    return {
        "name": f"配对样本T检验_{title_suffix}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": _smart_text(items),
        "sections": sections,
    }


run = paired_t_test
