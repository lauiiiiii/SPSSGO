# -*- coding: utf-8 -*-
# 单样本 Wilcoxon 符号秩检验：支持多变量批量检验，输出 SPSSAU 主表和 SPSSPRO 正态性辅助判断。
from backend.analysis.common import *
from backend.analysis.methods.normality_test import _normality_histogram_chart

METHOD_KEY = "one_sample_wilcoxon"
METHOD_META = {
    "label": "单样本Wilcoxon符号秩检验",
    "category": "数据检验",
    "description": "检验一个或多个样本中位数是否显著偏离给定检验值",
    "order": 30,
    "slots": [
        {
            "key": "test_vars",
            "label": "检验变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入需要逐个检验的定量变量",
        },
    ],
    "options": [
        {
            "key": "test_value",
            "label": "检验值",
            "type": "number",
            "default": "0",
            "hint": "自动选择关闭时生效，可输入任意数字。",
        },
        {
            "key": "auto_test_value",
            "label": "自动选择检验值",
            "type": "checkbox",
            "default": True,
            "hint": "勾选后每个变量使用自身均值作为检验值，和 SPSSPRO 的自动检验值口径保持一致。",
        },
        {
            "key": "output_normality",
            "label": "输出正态性检验图",
            "type": "checkbox",
            "default": True,
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


def _result_summary(rows):
    if not rows:
        return "未找到可用于单样本Wilcoxon符号秩检验的有效变量。"
    names = [row["name"] for row in rows]
    sig_rows = [row for row in rows if row["p"] < 0.05]
    if sig_rows:
        sig_names = [row["name"] for row in sig_rows]
        higher = [row for row in sig_rows if row["median"] > row["test_value"]]
        lower = [row for row in sig_rows if row["median"] < row["test_value"]]
        direction_parts = []
        if higher:
            direction_parts.append(
                "、".join(f"{row['name']}的中位数显著高于{_fmt(row['test_value'], 3)}" for row in higher)
            )
        if lower:
            direction_parts.append(
                "、".join(f"{row['name']}的中位数显著低于{_fmt(row['test_value'], 3)}" for row in lower)
            )
        direction_text = "；".join(direction_parts) if direction_parts else "中位数与检验值存在显著差异"
        return (
            f"从上表可知，{'、'.join(sig_names)}共{len(sig_rows)}项呈现出显著性"
            f"(p<0.05)，{direction_text}。"
        )
    return (
        f"从上表可知，{'、'.join(names)}共{len(rows)}项均未呈现出显著性"
        "(p>=0.05)，说明其中位数与对应检验值没有统计学显著差异。"
    )


def _param_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        return [value]
    return []


def _bool_param(params, key, default=False):
    value = params.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "否", "关闭"}
    return bool(value)


def _config_section(variables, auto_test_value, manual_test_value, output_normality):
    value_mode = "自动选择：每个变量使用自身均值作为检验值" if auto_test_value else f"手动输入：统一检验值 {_fmt(manual_test_value, 3)}"
    rows = [
        ["算法", "单样本Wilcoxon符号秩检验"],
        ["变量", "、".join(variables)],
        ["检验值", value_mode],
        ["正态性辅助", "输出" if output_normality else "不输出"],
        ["缺失值处理", "逐变量剔除缺失值；与检验值相等的零差值不参与符号秩计算"],
    ]
    return _sec_table(
        "分析配置",
        ["项目", "内容"],
        rows,
        description="本表记录本次分析的核心配置，避免报告脱离配置页后看不出检验值来源。",
    )


def run(df, params):
    """
    单样本 Wilcoxon 符号秩检验。

    @param df: 数据 DataFrame
    @param params: test_vars/variables/variable 为检验变量，test_value 为手动对比数字，
        auto_test_value=True 时按每个变量的均值自动设置检验值
    @return: 多变量批量 Wilcoxon 主结果、可选正态性检验和解读
    """
    variables = _resolve_cols(
        df,
        (
            _param_list(params.get("test_vars"))
            or _param_list(params.get("variables"))
            or _param_list(params.get("variable"))
        ),
    )
    manual_test_value = float(params.get("test_value", 0) or 0)
    auto_test_value = _bool_param(params, "auto_test_value", True)
    output_normality = _bool_param(params, "output_normality", True)
    if not variables:
        return {
            "name": METHOD_META["label"],
            "headers": [],
            "rows": [],
            "description": "至少需要 1 个检验变量。",
        }

    rows = []
    summaries = []
    normality_rows = []
    normality_charts = []
    for var in variables:
        series = pd.to_numeric(df[var], errors="coerce").dropna()
        if len(series) < 1:
            continue

        if output_normality:
            normality_rows.append(_normality_row(var, series))
            histogram_chart = _normality_histogram_chart(var, series)
            if histogram_chart:
                normality_charts.append(histogram_chart)

        test_value = float(series.mean()) if auto_test_value else manual_test_value
        diff = series - test_value
        diff = diff[diff != 0]
        if len(diff) < 1:
            continue

        stat, p_val = wilcoxon(diff)
        median = float(series.median())
        z_value = _signed_rank_z(diff.to_numpy())
        summaries.append({
            "name": var,
            "median": median,
            "test_value": test_value,
            "p": float(p_val),
        })
        rows.append([
            var,
            str(len(diff)),
            _fmt(test_value, 3),
            _fmt(series.quantile(0.25), 3),
            _fmt(median, 3),
            _fmt(series.quantile(0.75), 3),
            _fmt(z_value, 3),
            _p_with_sig(float(p_val)),
        ])

    headers = ["名称", "样本量", "检验值", "25分位数", "中位数", "75分位数", "统计量Z值", "p"]
    smart = _result_summary(summaries)
    value_description = "自动按每个变量均值设置检验值" if auto_test_value else f"统一检验值为{_fmt(manual_test_value, 3)}"
    sections = [
        _config_section(variables, auto_test_value, manual_test_value, output_normality),
        _sec_table(
            "输出结果1：单样本Wilcoxon分析结果",
            headers,
            rows,
            note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description=f"上表展示单样本Wilcoxon符号秩检验结果，每个变量独立与检验值比较；本次{value_description}。",
        ),
    ]
    if output_normality and normality_rows:
        sections.extend([
            _sec_table(
                "正态性检验结果",
                ["名称", "样本量", "平均值", "标准差", "S-W检验", "K-S检验"],
                normality_rows,
                note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
                description="上表展示检验变量的正态性检验结果，可辅助判断是否需要使用非参数检验。",
            ),
            _sec_charts(
                "正态性检验直方图",
                normality_charts,
                "上图展示各检验变量的分布形态，若数据明显偏离正态，可优先参考Wilcoxon符号秩检验。",
            ),
        ])
    sections.extend([
        _sec_advice(
            "单样本Wilcoxon符号秩检验研究数据是否明显不等于某个数字；\n"
            "第一：分析每个分析项是否呈现出显著性；\n"
            "第二：如果呈现出显著性，结合中位数与对比数字判断差异方向；\n"
            "第三：若正态性检验显示数据近似正态，可同步参考单样本T检验；若明显非正态，优先参考Wilcoxon结果；\n"
            "第四：对分析进行总结。",
            title="分析步骤",
        ),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL),
    ])
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": smart,
        "sections": sections,
    }
