# -*- coding: utf-8 -*-
# 单样本等价检验：只处理一个定量变量与目标值/等价限值的 TOST 判断。
from backend.analysis.common import *

METHOD_KEY = "one_sample_equivalence_test"

ALT_INTERVAL = "下限<检验均值-目标值<上限"
ALT_GT_TARGET = "检验均值>目标值"
ALT_LT_TARGET = "检验均值<目标值"
ALT_GT_LOWER = "检验均值-目标值>下限"
ALT_LT_UPPER = "检验均值-目标值<上限"

METHOD_META = {
    "label": "单样本等价检验",
    "category": "差异对比分析包",
    "description": "单样本等价检验用于检验单个总体的参数是否与某个目标值处于预先定义的等价区间内。",
    "order": 70,
    "slots": [
        {
            "key": "variable",
            "label": "变量",
            "type": "single",
            "accept": "numeric",
            "hint": "拖入变量到此区域",
        }
    ],
    "options": [
        {
            "key": "alternative",
            "label": "备择假设",
            "choices": [ALT_INTERVAL, ALT_GT_TARGET, ALT_LT_TARGET, ALT_GT_LOWER, ALT_LT_UPPER],
            "default": ALT_INTERVAL,
        },
        {"key": "target_value", "label": "目标值", "default": "0"},
        {"key": "lower", "label": "下限", "default": "-0.1"},
        {"key": "upper", "label": "上限", "default": "0.1"},
        {
            "key": "scale_by_target",
            "label": "乘以目标值",
            "type": "checkbox",
            "default": True,
            "hint": "勾选后，下限和上限按目标值比例换算，例如目标值为2、上下限为±0.1时，等价区间为±0.2。",
        },
    ],
    "param_builder": "direct",
}


def _to_float(value, default=0.0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not np.isfinite(number):
        return default
    return number


def _to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是"}


def _fmt_p(value):
    if value is None or not np.isfinite(value):
        return "—"
    return f"{value:.3f}{_sig(value)}"


def _normality_expr(statistic, p_value):
    if statistic is None or p_value is None or not np.isfinite(statistic) or not np.isfinite(p_value):
        return "—"
    return f"{_fmt(statistic, 3)}({_fmt_p(p_value)})"


def _scaled_bounds(params):
    target = _to_float(params.get("target_value", params.get("reference_value", 0)), 0.0)
    lower = _to_float(params.get("lower", -abs(_to_float(params.get("margin", 0.1), 0.1))), -0.1)
    upper = _to_float(params.get("upper", abs(_to_float(params.get("margin", 0.1), 0.1))), 0.1)
    if lower > upper:
        lower, upper = upper, lower
    if _to_bool(params.get("scale_by_target"), True):
        lower *= target
        upper *= target
        if lower > upper:
            lower, upper = upper, lower
    return target, lower, upper


def _descriptive_stats(variable, series):
    n = len(series)
    mean = float(series.mean())
    std = float(series.std(ddof=1))
    se = std / np.sqrt(n)
    skew = float(stats.skew(series, bias=False)) if n >= 3 else np.nan
    kurtosis = float(stats.kurtosis(series, fisher=True, bias=False)) if n >= 4 else np.nan

    sw_stat = sw_p = np.nan
    if 3 <= n <= 5000:
        sw_stat, sw_p = stats.shapiro(series)

    ks_stat = ks_p = np.nan
    if std > 0:
        standardized = (series - mean) / std
        ks_stat, ks_p = stats.kstest(standardized, "norm")

    return {
        "variable": variable,
        "n": n,
        "mean": mean,
        "std": std,
        "se": se,
        "skew": skew,
        "kurtosis": kurtosis,
        "sw_stat": float(sw_stat) if np.isfinite(sw_stat) else np.nan,
        "sw_p": float(sw_p) if np.isfinite(sw_p) else np.nan,
        "ks_stat": float(ks_stat) if np.isfinite(ks_stat) else np.nan,
        "ks_p": float(ks_p) if np.isfinite(ks_p) else np.nan,
    }


def _test_rows(alternative, diff, se, dfree, lower, upper):
    if se <= 0 or not np.isfinite(se):
        return [], False

    def t_gt(bound):
        t_value = (diff - bound) / se
        return t_value, stats.t.sf(t_value, dfree)

    def t_lt(bound):
        t_value = (diff - bound) / se
        return t_value, stats.t.cdf(t_value, dfree)

    if alternative == ALT_GT_TARGET:
        t_value, p_value = t_gt(0)
        rows = [["差值 ≤ 0", str(dfree), _fmt(t_value, 3), _fmt_p(p_value)]]
        return rows, p_value < 0.05
    if alternative == ALT_LT_TARGET:
        t_value, p_value = t_lt(0)
        rows = [["差值 ≥ 0", str(dfree), _fmt(t_value, 3), _fmt_p(p_value)]]
        return rows, p_value < 0.05
    if alternative == ALT_GT_LOWER:
        t_value, p_value = t_gt(lower)
        rows = [[f"差值 ≤ {_fmt(lower, 3)}", str(dfree), _fmt(t_value, 3), _fmt_p(p_value)]]
        return rows, p_value < 0.05
    if alternative == ALT_LT_UPPER:
        t_value, p_value = t_lt(upper)
        rows = [[f"差值 ≥ {_fmt(upper, 3)}", str(dfree), _fmt(t_value, 3), _fmt_p(p_value)]]
        return rows, p_value < 0.05

    lower_t, lower_p = t_gt(lower)
    upper_t, upper_p = t_lt(upper)
    rows = [
        [f"差值 ≤ {_fmt(lower, 3)}", str(dfree), _fmt(lower_t, 3), _fmt_p(lower_p)],
        [f"差值 ≥ {_fmt(upper, 3)}", str(dfree), _fmt(upper_t, 3), _fmt_p(upper_p)],
        [f"原假设：差值 ≤ {_fmt(lower, 3)} 或 差值 ≥ {_fmt(upper, 3)}", "", "", ""],
        [f"备择假设：{_fmt(lower, 3)} < 差值 < {_fmt(upper, 3)}", "", "", ""],
    ]
    return rows, max(lower_p, upper_p) < 0.05


def _chart(variable, diff, ci_low, ci_high, lower, upper):
    return {
        "chartType": "equivalence_interval",
        "title": "等价检验可视化",
        "varName": variable,
        "data": {
            "variable": variable,
            "difference": round(float(diff), 6),
            "ciLow": round(float(ci_low), 6),
            "ciHigh": round(float(ci_high), 6),
            "lower": round(float(lower), 6),
            "upper": round(float(upper), 6),
            "ciLabel": "对等项的95% CI",
        },
    }


def run(df, params):
    variable = params.get("variable", "")
    if variable not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "检验变量不存在。"}

    series = pd.to_numeric(df[variable], errors="coerce").dropna()
    if len(series) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    target, lower, upper = _scaled_bounds(params)
    alternative = params.get("alternative") or ALT_INTERVAL
    stats_info = _descriptive_stats(variable, series)
    n = stats_info["n"]
    dfree = n - 1
    mean = stats_info["mean"]
    se = stats_info["se"]
    diff = mean - target
    t_crit = stats.t.ppf(0.975, dfree)
    ci_low = diff - t_crit * se
    ci_high = diff + t_crit * se

    desc_headers = ["变量", "N", "均值", "标准差", "均值标准误", "偏度", "峰度", "S-W检验", "K-S检验"]
    desc_rows = [[
        variable,
        str(n),
        _fmt(mean, 3),
        _fmt(stats_info["std"], 3),
        _fmt(se, 3),
        _fmt(stats_info["skew"], 3),
        _fmt(stats_info["kurtosis"], 3),
        _normality_expr(stats_info["sw_stat"], stats_info["sw_p"]),
        _normality_expr(stats_info["ks_stat"], stats_info["ks_p"]),
    ]]

    ci_headers = ["差值", "SE", "对等项的 95% CI", "等价区间"]
    ci_rows = [
        [_fmt(diff, 3), _fmt(se, 3), f"({_fmt(ci_low, 3)}, {_fmt(ci_high, 3)})", f"({_fmt(lower, 3)}, {_fmt(upper, 3)})"],
        [f"差值：均值({variable}) - 目标值", "", "", ""],
    ]

    test_headers = ["原假设", "自由度", "T值", "P值"]
    test_rows, tost_passed = _test_rows(alternative, diff, se, dfree, lower, upper)
    ci_inside = ci_low > lower and ci_high < upper
    equivalent = ci_inside and tost_passed if alternative == ALT_INTERVAL else tost_passed

    if alternative == ALT_INTERVAL:
        conclusion = (
            f"置信区间({_fmt(ci_low, 3)}, {_fmt(ci_high, 3)})"
            f"{'完全落在' if ci_inside else '未完全落在'}等价区间({_fmt(lower, 3)}, {_fmt(upper, 3)})内，"
            f"认为总体参数与目标值{'等价' if equivalent else '不等价'}。"
        )
    else:
        conclusion = f"基于备择假设“{alternative}”，检验结果{'支持' if equivalent else '不支持'}该判断。"

    sections = [
        _sec_advice(
            "1. 数据特征与分布判断：计算样本核心统计量（如均值、标准差、标准误、偏度、峰度等）；\n"
            "2. 置信区间法判断等价性：根据数据分布和样本量，构建与显著性水平对应的置信区间；\n"
            "3. P值法辅助验证：通过软件计算等价检验的P值，与置信区间法形成相互印证。",
            title="分析步骤",
        ),
        _sec_table(
            "输出结果1：描述性统计",
            desc_headers,
            desc_rows,
            description="上表展示了描述统计结果，因单样本等价检验通常要求数据近似正态，若数据非正态可能会导致结论偏差。",
        ),
        _sec_smart(
            f"{variable}样本N={n}，均值为{_fmt(mean, 3)}，标准差为{_fmt(stats_info['std'], 3)}。"
            f"S-W检验显著性P值为{_fmt_p(stats_info['sw_p'])}。"
        ),
        _sec_table(
            "输出结果2：置信区间与等价限值比较",
            ci_headers,
            ci_rows,
            description="上表展示了置信区间与等价限值对比结果，若置信区间完全落在预设等价限值范围内，则拒绝原假设，认为总体参数与目标值等价；反之则无法判定等价。",
        ),
        _sec_smart(conclusion),
        _sec_table(
            "输出结果3：等价检验",
            test_headers,
            test_rows,
            note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description="上表展示了等价检验结果，若原假设P值小于设定的显著性水平（如0.05），则从概率角度支持等价结论。",
        ),
        _sec_charts(
            "输出结果4：等价检验可视化",
            [_chart(variable, diff, ci_low, ci_high, lower, upper)],
            "上图展示了等价检验可视化结果，若置信区间完全落在预设的等价界值范围内，则认为总体参数与目标值等价。",
        ),
        _sec_refs(_REFS_GENERAL),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": test_headers,
        "rows": test_rows,
        "description": conclusion,
        "sections": sections,
    }
