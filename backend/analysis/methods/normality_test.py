# -*- coding: utf-8 -*-
# 这里只放正态性分析的业务编排，表和图共用同一份统计结果，别拆成几套各算各的。
# 这里要同时兼容 SPSSAU/SPSSPRO 的常见输出，后面补别的检验时也别绕开这层。
from backend.analysis.common import *
from statsmodels.stats.diagnostic import normal_ad

METHOD_KEY = "normality_test"
METHOD_META = {
    'label': '正态性分析',
    'category': '常用方法',
    'description': '综合输出正态性检验表、直方图、P-P 图和 Q-Q 图',
    'order': 50,
    'slots': [{
        'key': 'variables',
        'label': '分析变量',
        'type': 'multiple',
        'accept': 'numeric',
        'min': 1,
        'hint': '放入需要检验正态性的变量',
    }],
    'options': [],
    'param_builder': 'direct',
}


def _safe_std(series):
    return float(series.std()) if len(series) > 1 else np.nan


def _safe_shapiro(series):
    if len(series) < 3:
        return (np.nan, np.nan)
    sample = series.sample(min(5000, len(series)), random_state=42) if len(series) > 5000 else series
    try:
        statistic, p_value = shapiro(sample)
        return (float(statistic), float(p_value))
    except Exception:
        return (np.nan, np.nan)


def _safe_ks(series):
    if len(series) < 3:
        return (np.nan, np.nan)
    std_value = series.std(ddof=1)
    if not np.isfinite(std_value) or std_value == 0:
        return (np.nan, np.nan)
    standardized = (series - series.mean()) / std_value
    try:
        statistic, p_value = stats.kstest(standardized, "norm")
        return (float(statistic), float(p_value))
    except Exception:
        return (np.nan, np.nan)


def _safe_jarque_bera(series):
    if len(series) < 3:
        return (np.nan, np.nan, np.nan)
    try:
        statistic, p_value = stats.jarque_bera(series)
        return (float(statistic), 2.0, float(p_value))
    except Exception:
        return (np.nan, np.nan, np.nan)


def _safe_anderson(series):
    if len(series) < 3:
        return (np.nan, np.nan)
    try:
        statistic, p_value = normal_ad(series)
        return (float(statistic), float(p_value))
    except Exception:
        return (np.nan, np.nan)


def _p_with_sig(p_value):
    if not np.isfinite(p_value):
        return "—"
    return f"{_fmt(p_value)}{_sig(p_value)}"


def _plot_sample(series, max_points=1000):
    if len(series) <= max_points:
        return series.sort_values().reset_index(drop=True)
    return series.sample(max_points, random_state=42).sort_values().reset_index(drop=True)


def _normality_histogram_chart(variable, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if len(values) == 0:
        return None
    unique_count = len(values.unique())
    bin_count = min(10, max(5, unique_count))
    counts, bin_edges = np.histogram(values, bins=bin_count)
    mean_value = float(values.mean())
    std_value = float(values.std(ddof=1)) if len(values) > 1 else np.nan
    density_x = np.linspace(bin_edges[0], bin_edges[-1], 120)
    if np.isfinite(std_value) and std_value > 0:
        bin_width = float(bin_edges[1] - bin_edges[0]) if len(bin_edges) > 1 else 1.0
        density_y = stats.norm.pdf(density_x, loc=mean_value, scale=std_value) * len(values) * bin_width
    else:
        density_y = np.zeros_like(density_x)
    return {
        "chartType": "normality_histogram",
        "title": variable,
        "varName": variable,
        "data": {
            "binEdges": [round(float(edge), 4) for edge in bin_edges],
            "counts": [int(count) for count in counts],
            "curveX": [round(float(value), 4) for value in density_x],
            "curveY": [round(float(value), 4) for value in density_y],
        },
    }


def _pp_plot_chart(variable, series):
    sample = _plot_sample(series)
    if len(sample) < 3:
        return None
    mean_value = sample.mean()
    std_value = sample.std(ddof=1)
    if not np.isfinite(std_value) or std_value == 0:
        return None
    observed = (np.arange(1, len(sample) + 1) - 0.5) / len(sample)
    expected = stats.norm.cdf((sample - mean_value) / std_value)
    points = [
        {"x": round(float(expected_value), 6), "y": round(float(observed_value), 6)}
        for expected_value, observed_value in zip(expected, observed)
    ]
    return {
        "chartType": "pp_plot",
        "title": variable,
        "varName": variable,
        "data": {
            "points": points,
            "xLabel": "理论累计概率",
            "yLabel": "观察累计概率",
            "lineStart": {"x": 0, "y": 0},
            "lineEnd": {"x": 1, "y": 1},
        },
    }


def _qq_plot_chart(variable, series):
    sample = _plot_sample(series)
    if len(sample) < 3:
        return None
    try:
        theoretical, observed = stats.probplot(sample, dist="norm", fit=False)
        fit_slope, fit_intercept, _ = stats.probplot(sample, dist="norm", fit=True)[1]
    except Exception:
        return None
    points = [
        {"x": round(float(theoretical_value), 6), "y": round(float(observed_value), 6)}
        for theoretical_value, observed_value in zip(theoretical, observed)
    ]
    x_min = float(np.min(theoretical))
    x_max = float(np.max(theoretical))
    return {
        "chartType": "qq_plot",
        "title": variable,
        "varName": variable,
        "data": {
            "points": points,
            "xLabel": "理论分位数",
            "yLabel": "观察值",
            "lineStart": {"x": round(x_min, 6), "y": round(fit_intercept + fit_slope * x_min, 6)},
            "lineEnd": {"x": round(x_max, 6), "y": round(fit_intercept + fit_slope * x_max, 6)},
        },
    }


def _build_hist_section(charts):
    return _sec_charts(
        "输出结果2：正态性检验直方图",
        charts,
        "上图展示各变量的频数分布与正态拟合曲线，用于直观看分布是否近似钟形。",
    )


def _build_pp_section(charts):
    return _sec_charts(
        "输出结果3：正态性检验P-P图",
        charts,
        "P-P 图用于比较观察累计概率与理论累计概率，点越贴近参考线，越接近正态分布。",
    )


def _build_qq_section(charts):
    return _sec_charts(
        "输出结果4：正态性检验Q-Q图",
        charts,
        "Q-Q 图用于比较样本分位数与理论正态分位数，点越贴近参考线，越接近正态分布。",
    )


def normality_test(df, params):
    """
    正态性检验：综合输出描述统计、常用正态检验和图形诊断

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if not variables:
        return {"name": "正态性分析", "headers": [], "rows": [], "description": "未指定变量。"}

    summary_headers = ["名称", "样本量", "中位数", "平均值", "标准差", "偏度", "峰度", "D值", "p", "W值", "p"]
    summary_header_rows = [
        [
            {"text": "名称", "rowspan": 2},
            {"text": "样本量", "rowspan": 2},
            {"text": "中位数", "rowspan": 2},
            {"text": "平均值", "rowspan": 2},
            {"text": "标准差", "rowspan": 2},
            {"text": "偏度", "rowspan": 2},
            {"text": "峰度", "rowspan": 2},
            {"text": "Kolmogorov-Smirnov检验", "colspan": 2},
            {"text": "Shapiro-Wilk检验", "colspan": 2},
        ],
        ["统计量D值", "p", "统计量W值", "p"],
    ]
    summary_rows = []
    jb_rows = []
    ad_rows = []
    histogram_charts = []
    pp_charts = []
    qq_charts = []
    interpretation_rows = []

    for variable in variables:
        series = pd.to_numeric(df[variable], errors="coerce").dropna()
        sample_size = len(series)
        mean_value = float(series.mean()) if sample_size else np.nan
        median_value = float(series.median()) if sample_size else np.nan
        std_value = _safe_std(series)
        skew_value = float(series.skew()) if sample_size >= 3 else np.nan
        kurt_value = float(series.kurtosis()) if sample_size >= 4 else np.nan
        ks_stat, ks_p = _safe_ks(series)
        sw_stat, sw_p = _safe_shapiro(series)
        jb_stat, jb_df, jb_p = _safe_jarque_bera(series)
        ad_stat, ad_p = _safe_anderson(series)

        summary_rows.append([
            variable,
            str(sample_size),
            _fmt(median_value),
            _fmt(mean_value),
            _fmt(std_value),
            _fmt(skew_value),
            _fmt(kurt_value),
            _fmt(ks_stat),
            _p_with_sig(ks_p),
            _fmt(sw_stat),
            _p_with_sig(sw_p),
        ])
        jb_rows.append([variable, str(sample_size), _fmt(jb_stat), _fmt(jb_df, 0), _fmt(jb_p)])
        ad_rows.append([variable, str(sample_size), _fmt(ad_stat), _fmt(ad_p)])

        histogram_chart = _normality_histogram_chart(variable, series)
        if histogram_chart:
            histogram_charts.append(histogram_chart)
        pp_chart = _pp_plot_chart(variable, series)
        if pp_chart:
            pp_charts.append(pp_chart)
        qq_chart = _qq_plot_chart(variable, series)
        if qq_chart:
            qq_charts.append(qq_chart)

        primary_test_name = "Shapiro-Wilk" if sample_size <= 5000 else "Kolmogorov-Smirnov"
        primary_p = sw_p if sample_size <= 5000 else ks_p
        primary_ok = bool(np.isfinite(primary_p) and primary_p > 0.05)
        interpretation_rows.append({
            "variable": variable,
            "sample_size": sample_size,
            "primary_test_name": primary_test_name,
            "primary_p": primary_p,
            "primary_ok": primary_ok,
            "skew": skew_value,
            "kurt": kurt_value,
        })

    sections = []
    summary_section = _sec_table(
        "输出结果1：总体描述结果",
        summary_headers,
        summary_rows,
        note="注：`* p<0.05` `** p<0.01` `*** p<0.001`。",
        description=(
            "上表同时展示描述统计、Kolmogorov-Smirnov 检验和 Shapiro-Wilk 检验结果。"
            "建议优先结合样本量、p 值、偏度峰度和图形综合判断。"
        ),
    )
    summary_section["headerRows"] = summary_header_rows
    sections.append(summary_section)

    advice = (
        "正态性判断可参考以下规则：\n"
        "1. 样本量 ≤ 5000 时优先看 Shapiro-Wilk，> 5000 时可参考 Kolmogorov-Smirnov；\n"
        "2. p < 0.05 说明在该检验下偏离正态，但大样本时轻微偏离也容易显著；\n"
        "3. 若偏度绝对值 < 2、峰度绝对值 < 7，且图形整体贴近参考形态，可视为近似正态；\n"
        "4. 实际分析中建议把统计检验、偏度峰度和图形诊断交叉使用，不要只盯着 p 值。"
    )
    sections.append(_sec_advice(advice))

    near_normal = [item["variable"] for item in interpretation_rows if item["primary_ok"]]
    non_normal = [item["variable"] for item in interpretation_rows if not item["primary_ok"]]

    # 总体结论
    if not near_normal and not non_normal:
        conclusion = "所分析变量暂无可用的正态性检验结果。"
    elif not near_normal:
        conclusion = f"从检验结果看，{'、'.join(non_normal)}均未通过严格正态性检验。"
    elif not non_normal:
        conclusion = f"从检验结果看，{'、'.join(near_normal)}均通过正态性检验。"
    else:
        conclusion = f"从检验结果看，{'、'.join(near_normal)}通过正态性检验；{'、'.join(non_normal)}未通过。"

    # 逐变量结论
    detail_parts = []
    for item in interpretation_rows:
        p_value_text = _fmt(item["primary_p"]) if np.isfinite(item["primary_p"]) else "—"
        skew_text = _fmt(item["skew"])
        kurt_text = _fmt(item["kurt"])
        verdict = "通过" if item["primary_ok"] else "未通过"
        detail_parts.append(
            f"{item['variable']}（n={item['sample_size']}）：{item['primary_test_name']} 检验 p={p_value_text}，"
            f"{verdict}；偏度={skew_text}，峰度={kurt_text}"
        )

    # 后续建议
    if non_normal:
        suggestion = (
            "后续分析建议：未通过严格检验的变量，可结合样本量、偏度峰度及图形结果综合判断；"
            "若偏离不严重，参数检验（如 t 检验、方差分析、Pearson 相关或线性回归）仍可酌情使用。"
        )
    else:
        suggestion = "后续可直接使用参数检验（如 t 检验、方差分析、Pearson 相关或线性回归）。"

    smart = conclusion
    if detail_parts:
        smart += "具体来看：" + "；".join(detail_parts) + "。"
    smart += suggestion
    sections.append(_sec_smart(smart))

    if histogram_charts:
        sections.append(_build_hist_section(histogram_charts))
    if pp_charts:
        sections.append(_build_pp_section(pp_charts))
    if qq_charts:
        sections.append(_build_qq_section(qq_charts))

    jb_section = _sec_table(
        "Jarque-Bera检验",
        ["名称", "样本量", "χ²", "df", "p值"],
        jb_rows,
        description="Jarque-Bera 检验基于偏度和峰度构造，适合与其他正态检验交叉参考。",
    )
    sections.append(jb_section)

    ad_section = _sec_table(
        "Anderson-darling检验",
        ["名称", "样本量", "AD值", "p值"],
        ad_rows,
        description="Anderson-Darling 检验对尾部偏离更敏感，可作为补充判断依据。",
    )
    sections.append(ad_section)
    sections.append(_sec_refs([
        "[1] 盛骤，谢式千，潘承毅。概率论与数理统计 [M]. 5 版。北京：高等教育出版社，2019.",
        "[2] Feller W. An Introduction to Probability Theory and Its Applications: Vol.1 [M]. 3rd ed. New York: Wiley, 1968.",
        "[3] 宗序平，姚玉兰。利用 Q-Q 图与 P-P 图快速检验数据的统计分布 [J]. 统计与决策，2010 (20):151-152.",
    ]))

    return {
        "name": "正态性分析",
        "headers": summary_headers,
        "rows": summary_rows,
        "description": smart,
        "sections": sections,
    }


run = normality_test
