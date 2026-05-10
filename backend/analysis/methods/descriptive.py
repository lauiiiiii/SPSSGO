# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "descriptive"
METHOD_META = {'label': '描述性统计',
 'category': '常用方法',
 'description': '计算各变量的均值、标准差、最小值、最大值等描述性指标',
 'order': 30,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要描述的定量变量'}],
 'options': [],
 'param_builder': 'direct'}

PERCENTILE_POINTS = [
    ("P2.5", 0.025),
    ("P5", 0.05),
    ("P10", 0.10),
    ("P25", 0.25),
    ("P27", 0.27),
    ("P33", 0.33),
    ("P50", 0.50),
    ("P67", 0.67),
    ("P73", 0.73),
    ("P75", 0.75),
    ("P90", 0.90),
    ("P95", 0.95),
    ("P97.5", 0.975),
]


def _numeric_series(df, variable):
    return pd.to_numeric(df[variable], errors="coerce")


def _series_stats(series):
    clean = series.dropna()
    n = int(len(clean))
    mean = float(clean.mean()) if n else np.nan
    std = float(clean.std()) if n > 1 else 0.0 if n == 1 else np.nan
    variance = float(clean.var()) if n > 1 else 0.0 if n == 1 else np.nan
    sem = std / np.sqrt(n) if n > 1 else 0.0 if n == 1 else np.nan
    if n > 1 and np.isfinite(sem):
        ci_delta = float(stats.t.ppf(0.975, n - 1) * sem)
        ci_low = mean - ci_delta
        ci_high = mean + ci_delta
    else:
        ci_low = mean
        ci_high = mean
    q1 = float(clean.quantile(0.25)) if n else np.nan
    q3 = float(clean.quantile(0.75)) if n else np.nan
    return {
        "n": n,
        "mean": mean,
        "std": std,
        "min": float(clean.min()) if n else np.nan,
        "max": float(clean.max()) if n else np.nan,
        "median": float(clean.median()) if n else np.nan,
        "variance": variance,
        "sum": float(clean.sum()) if n else np.nan,
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1 if n else np.nan,
        "sem": sem,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "skew": float(clean.skew()) if n > 2 else np.nan,
        "kurtosis": float(clean.kurtosis()) if n > 3 else np.nan,
        "cv": abs(std / mean) if n > 1 and mean != 0 else np.nan,
    }


def _fmt_cv(value):
    if value is None or not np.isfinite(value):
        return "—"
    return f"{float(value) * 100:.3f}%"


def _mean_compare_chart(stats_rows):
    return {
        "chartType": "metric_comparison",
        "title": "平均值对比图",
        "data": {
            "metric": "平均值",
            "labels": [row["variable"] for row in stats_rows],
            "values": [round(float(row["mean"]), 4) for row in stats_rows],
        },
    }


def _build_percentile_table(df, variables):
    headers = ["名称"] + [label for label, _ in PERCENTILE_POINTS]
    rows = []
    for variable in variables:
        clean = _numeric_series(df, variable).dropna()
        rows.append([
            variable,
            *[_fmt(clean.quantile(point)) if len(clean) else "—" for _, point in PERCENTILE_POINTS],
        ])
    description = "百分位数用于观察变量在不同位置上的分布水平，帮助判断数据集中、分散和尾部情况。"
    return _sec_table("百分位数", headers, rows, description=description)


def descriptive(df, params):
    """
    描述统计分析，输出基础指标、深入指标、百分位数和图形报告

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if not variables:
        return {"name": "描述性统计", "headers": [], "rows": [], "description": "未找到指定变量。"}

    headers = ["变量名", "样本量", "最大值", "最小值", "平均值", "标准差", "中位数", "方差", "峰度", "偏度", "变异系数（CV）"]
    rows = []
    stats_rows = []
    descs = []
    for v in variables:
        stats_row = _series_stats(_numeric_series(df, v))
        stats_row["variable"] = v
        stats_rows.append(stats_row)
        rows.append([
            v,
            str(stats_row["n"]),
            _fmt(stats_row["max"]),
            _fmt(stats_row["min"]),
            _fmt(stats_row["mean"]),
            _fmt(stats_row["std"]),
            _fmt(stats_row["median"]),
            _fmt(stats_row["variance"]),
            _fmt(stats_row["kurtosis"]),
            _fmt(stats_row["skew"]),
            _fmt_cv(stats_row["cv"]),
        ])
        descs.append(f"{v}的均值为{_fmt(stats_row['mean'])}（SD={_fmt(stats_row['std'])}）")

    sections = []
    desc_text = (
        "上表展示了描述性统计的基础指标，包括样本量、最大值、最小值、平均值、标准差等，"
        "用于研究定量数据的整体情况。"
    )
    sections.append(_sec_table("输出结果1：总体描述结果", headers, rows, description=desc_text))
    advice_text = (
        "描述分析用于研究定量数据的整体情况，建议先查看样本量、均值和标准差；"
        "再结合中位数、偏度、峰度和变异系数判断数据是否存在明显离散或偏态。"
    )
    sections.append(_sec_advice(advice_text))

    # 智能分析
    smart_parts = []
    for item in stats_rows:
        skew = item["skew"] if np.isfinite(item["skew"]) else 0
        cv = item["cv"] if np.isfinite(item["cv"]) else 0
        skew_desc = "近似对称" if abs(skew) < 0.5 else ("右偏" if skew > 0 else "左偏")
        cv_note = f"变异系数（CV）为{_fmt(abs(cv), 3)}，{'大于0.15，当前数据中可能存在异常值，建议对异常或者表现较为突出的指标进行分析' if abs(cv) > 0.15 else '小于0.15，数据离散程度较低'}。"
        smart_parts.append(
            f"基于{item['variable']}，平均值为{_fmt(item['mean'])}，中位数为{_fmt(item['median'])}，分布{skew_desc}；{cv_note}"
        )
    sections.append(_sec_smart("\n".join(smart_parts)))

    mean_chart = _mean_compare_chart(stats_rows)
    sections.append(_sec_charts(
        "输出结果2：平均值对比图",
        [mean_chart],
        "上图展示各变量平均值的对比情况，可用于快速观察不同变量的均值水平差异。"
    ))

    deep_headers = ["名称", "平均值±标准差", "方差", "求和", "25分位数", "中位数", "75分位数", "标准误", "均值95% CI(LL)", "均值95% CI(UL)", "IQR", "峰度", "偏度", "变异系数(CV)"]
    deep_rows = [[
        item["variable"],
        f"{_fmt(item['mean'])}±{_fmt(item['std'])}",
        _fmt(item["variance"]),
        _fmt(item["sum"]),
        _fmt(item["q1"]),
        _fmt(item["median"]),
        _fmt(item["q3"]),
        _fmt(item["sem"]),
        _fmt(item["ci_low"]),
        _fmt(item["ci_high"]),
        _fmt(item["iqr"]),
        _fmt(item["kurtosis"]),
        _fmt(item["skew"]),
        _fmt_cv(item["cv"]),
    ] for item in stats_rows]
    sections.append(_sec_table("输出结果3：深入指标", deep_headers, deep_rows, description="深入指标补充展示方差、求和、分位数、标准误、均值置信区间、IQR 和变异系数等信息。"))
    sections.append(_build_percentile_table(df, variables))

    # 直方图
    hist_charts = [c for c in (_hist_chart(v, df[v]) for v in variables) if c]
    if hist_charts:
        hist_desc = (
            "上图以直方图的形式展示了各变量的频率分布情况，"
            "可用来直观了解数据的分布特征。"
        )
        sections.append(_sec_charts("输出结果4：直方图", hist_charts, hist_desc))

    # 箱型图
    box_charts = [c for c in (_box_chart(v, df[v]) for v in variables) if c]
    if box_charts:
        box_desc = (
            "上图以箱型图的形式展示了各变量高峰趋势分析的结果，"
            "高峰趋势用极大值、极小值、25%分位数、中位数、75%分位数等统计指标对数据分布进行差异（稳定性）溯源。\n"
            "PS：极大值、极小值并非该数据的最大值、最小值，"
            "该值为箱型图的内限，即大于极大值或小于极小值的点视为异常点。"
        )
        sections.append(_sec_charts("输出结果5：箱型图", box_charts, box_desc))

    sections.append(_build_missing_table(df, variables))
    sections.append(_build_variable_missing_table(df, variables))
    sections.append(_sec_refs(_REFS_GENERAL))

    description = f"各变量的描述统计结果如表所示。{'，'.join(descs)}。"
    return {"name": "描述性统计", "headers": headers, "rows": rows, "description": description, "sections": sections}

run = descriptive
