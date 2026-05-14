# -*- coding: utf-8 -*-
# 单样本 T 检验：按 SPSSAU 风格输出主结果、效应量和样本差异解读。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "one_sample_t_test"
METHOD_META = {
    "label": "单样本T检验",
    "category": "差异对比分析包",
    "description": "检验样本均值是否显著偏离给定检验值",
    "order": 5,
    "slots": [
        {
            "key": "test_vars",
            "label": "检验变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入需要进行检验的变量",
        },
    ],
    "options": [
        {
            "key": "test_value",
            "label": "检验值",
            "choices": ["0", "1", "3", "5"],
            "default": "0",
        },
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": False,
        },
    ],
    "param_builder": "direct",
}


def _p_with_sig(p_value):
    if p_value < 0.001:
        return f"{_fmt(p_value, 3)}****"
    if p_value < 0.01:
        return f"{_fmt(p_value, 3)}***"
    if p_value < 0.05:
        return f"{_fmt(p_value, 3)}**"
    if p_value < 0.1:
        return f"{_fmt(p_value, 3)}*"
    return _fmt(p_value, 3)


def _effect_level(cohens_d):
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        return "大"
    if abs_d >= 0.5:
        return "中"
    if abs_d >= 0.2:
        return "小"
    return "极小"


def _normality_row(var, series):
    n = len(series)
    if n < 3:
        return [var, str(n), "—", "—", "—", "—"]
    try:
        sample = series.sample(min(5000, n), random_state=42) if n > 5000 else series
        sw_stat, sw_p = shapiro(sample)
    except Exception:
        sw_stat, sw_p = (np.nan, np.nan)
    try:
        std_value = series.std(ddof=1)
        if np.isfinite(std_value) and std_value > 0:
            standardized = (series - series.mean()) / std_value
            ks_stat, ks_p = stats.kstest(standardized, "norm")
        else:
            ks_stat, ks_p = (np.nan, np.nan)
    except Exception:
        ks_stat, ks_p = (np.nan, np.nan)
    return [
        var,
        str(n),
        _fmt(series.mean(), 3),
        _fmt(series.std(ddof=1), 3),
        f"{_fmt(sw_stat, 3)}({_p_with_sig(float(sw_p))})" if np.isfinite(sw_p) else "—",
        f"{_fmt(ks_stat, 3)}({_p_with_sig(float(ks_p))})" if np.isfinite(ks_p) else "—",
    ]


def _result_summary(rows, test_value):
    if not rows:
        return "未找到可用于单样本T检验的有效变量。"
    names = [row["name"] for row in rows]
    sig_rows = [row for row in rows if row["p"] < 0.05]
    if sig_rows:
        sig_names = [row["name"] for row in sig_rows]
        higher = [row["name"] for row in sig_rows if row["mean"] > test_value]
        lower = [row["name"] for row in sig_rows if row["mean"] < test_value]
        direction_parts = []
        if higher:
            direction_parts.append(f"{'、'.join(higher)}的平均值显著高于{_fmt(test_value, 3)}")
        if lower:
            direction_parts.append(f"{'、'.join(lower)}的平均值显著低于{_fmt(test_value, 3)}")
        direction_text = "；".join(direction_parts) if direction_parts else "均值与检验值存在显著差异"
        return (
            f"从上表可知，{'、'.join(sig_names)}共{len(sig_rows)}项呈现出显著性"
            f"(p<0.05)，{direction_text}。"
        )
    return (
        f"从上表可知，{'、'.join(names)}共{len(rows)}项均未呈现出显著性"
        f"(p>=0.05)，说明其平均值与{_fmt(test_value, 3)}没有统计学显著差异。"
    )


def run(df, params):
    """
    单样本 T 检验。

    @param df: 数据 DataFrame
    @param params: test_vars/variables 为检验变量，test_value 为对比数字
    @return: SPSSAU 风格主结果表、效应量表和解读
    """
    variables = _resolve_cols(
        df,
        params.get("test_vars", []) or params.get("variables", []),
    )
    test_value = float(params.get("test_value", 0) or 0)
    if not variables:
        return {
            "name": METHOD_META["label"],
            "headers": [],
            "rows": [],
            "description": "至少需要 1 个检验变量。",
        }

    result_rows = []
    effect_rows = []
    normality_rows = []
    normality_charts = []
    summaries = []
    for var in variables:
        series = pd.to_numeric(df[var], errors="coerce").dropna()
        n = len(series)
        if n < 2:
            continue

        if params.get("output_normality"):
            normality_rows.append(_normality_row(var, series))
            histogram_chart = _normality_histogram_chart(var, series)
            if histogram_chart:
                normality_charts.append(histogram_chart)

        mean = float(series.mean())
        std = float(series.std(ddof=1))
        t_val, p_val = ttest_1samp(series, popmean=test_value)
        mean_diff = mean - test_value
        se = std / np.sqrt(n)
        dfree = n - 1
        crit = stats.t.ppf(0.975, dfree)
        ci_low = mean_diff - crit * se
        ci_high = mean_diff + crit * se
        cohens_d = mean_diff / std if std else np.nan

        summaries.append({
            "name": var,
            "mean": mean,
            "p": float(p_val),
            "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else np.nan,
        })
        result_rows.append([
            var,
            str(n),
            _fmt(series.min(), 3),
            _fmt(series.max(), 3),
            _fmt(mean, 3),
            _fmt(std, 3),
            _fmt(t_val, 3),
            _p_with_sig(float(p_val)),
        ])
        effect_rows.append([
            var,
            _fmt(mean, 3),
            _fmt(test_value, 3),
            _fmt(mean_diff, 3),
            f"{_fmt(ci_low, 3)} ~ {_fmt(ci_high, 3)}",
            str(dfree),
            _fmt(std, 3),
            _fmt(cohens_d, 3),
        ])

    result_headers = [
        "名称",
        "样本量",
        "最小值",
        "最大值",
        "平均值",
        "标准差",
        "t",
        "p",
    ]
    effect_headers = [
        "名称",
        "平均值",
        "对比数字",
        "差值",
        "差值95% CI",
        "df",
        "标准差",
        "Cohen's d 值",
    ]
    smart = _result_summary(summaries, test_value)
    effect_texts = [
        (
            f"{row['name']}的Cohen's d值为{_fmt(row['cohens_d'], 3)}，"
            f"属于{_effect_level(row['cohens_d'])}效应"
        )
        for row in summaries
        if np.isfinite(row.get("cohens_d", np.nan))
    ]
    sections = [
        _sec_table(
            "输出结果1：单样本T检验分析结果",
            result_headers,
            result_rows,
            note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description="上表展示单样本T检验结果，包括样本量、均值、标准差、t值及显著性。",
        ),
    ]
    if params.get("output_normality") and normality_rows:
        sections.extend([
            _sec_table(
                "正态性检验结果",
                ["名称", "样本量", "平均值", "标准差", "S-W检验", "K-S检验"],
                normality_rows,
                note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
                description="上表展示检验变量的正态性检验结果，可辅助判断单样本T检验的适用性。",
            ),
            _sec_charts(
                "正态性检验直方图",
                normality_charts,
                "上图展示各检验变量的分布形态，若直方图大致呈钟形，可作为正态性判断的辅助参考。",
            ),
        ])
    sections.extend([
        _sec_advice(
            "单样本T检验研究定量数据是否明显不等于某个数字；\n"
            "第一：分析每个分析项是否呈现出显著性；\n"
            "第二：如果呈现出显著性，结合平均值与对比数字判断差异方向；\n"
            "第三：对分析进行总结。"
        ),
        _sec_smart(smart),
        _sec_table(
            "深入分析-效应量指标",
            effect_headers,
            effect_rows,
        ),
        _sec_advice(
            "如果显示呈现出显著性差异，可通过平均值对比具体差异，同时还可使用效应量研究差异幅度情况；\n"
            "第一：使用Cohen's d值表示效应量大小，该值越大说明差异越大；\n"
            "第二：单样本检验使用Cohen's d值表示效应量大小时，0.2、0.5和0.8通常分别代表小、中、大效应；\n"
            "第三：Cohen's d值计算公式为差值除以标准差。"
        ),
    ])
    if effect_texts:
        sections.append(_sec_smart("；".join(effect_texts) + "。"))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {
        "name": METHOD_META["label"],
        "headers": result_headers,
        "rows": result_rows,
        "description": smart,
        "sections": sections,
    }
