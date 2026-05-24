# -*- coding: utf-8 -*-
# 双样本等价检验：支持同列分组和不同列两种输入，只在这里处理 TOST 业务口径。
from backend.analysis.common import *

METHOD_KEY = "two_sample_equivalence_test"

ALT_INTERVAL = "下限<检验均值 - 参考均值<上限"
ALT_GT_REF = "检验均值>参考均值"
ALT_LT_REF = "检验均值<参考均值"
ALT_GT_LOWER = "检验均值 - 参考均值>下限"
ALT_LT_UPPER = "检验均值 - 参考均值<上限"

REL_DIFF = "检验均值 - 参考均值"
REL_RATIO = "检验均值/参考均值"
REL_LOG_RATIO = "检验均值/参考均值(通过对数变换)"

METHOD_META = {
    "label": "双样本等价检验",
    "category": "差异对比分析包",
    "description": "双样本等价检验用于验证两个独立总体的参数均值差异是否在预设的等价区间内。",
    "order": 75,
    "slots": [
        {"key": "test_var", "label": "检验样本", "type": "single", "accept": "numeric", "hint": "拖入变量到此区域"},
        {"key": "group_var", "label": "二分类", "type": "single", "accept": "categorical", "hint": "拖入变量到此区域"},
        {"key": "reference_var", "label": "参考样本", "type": "single", "accept": "numeric", "hint": "拖入变量到此区域", "min": 0},
    ],
    "options": [
        {"key": "data_format", "label": "检验数据形式", "choices": ["样本在同一列", "样本在不同列"], "default": "样本在同一列"},
        {"key": "reference_level", "label": "参考水平", "default": ""},
        {"key": "relationship", "label": "相关假设", "choices": [REL_DIFF, REL_RATIO, REL_LOG_RATIO], "default": REL_DIFF},
        {"key": "alternative", "label": "备择假设", "choices": [ALT_INTERVAL, ALT_GT_REF, ALT_LT_REF, ALT_GT_LOWER, ALT_LT_UPPER], "default": ALT_INTERVAL},
        {"key": "lower", "label": "下限", "default": "-0.1"},
        {"key": "upper", "label": "上限", "default": "0.1"},
        {"key": "scale_by_reference", "label": "乘以参考均值", "type": "checkbox", "default": True},
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


def _sample_stats(name, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    n = len(values)
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    se = std / np.sqrt(n)
    skew = float(stats.skew(values, bias=False)) if n >= 3 else np.nan
    kurtosis = float(stats.kurtosis(values, fisher=True, bias=False)) if n >= 4 else np.nan
    sw_stat = sw_p = np.nan
    if 3 <= n <= 5000:
        sw_stat, sw_p = stats.shapiro(values)
    ks_stat = ks_p = np.nan
    if std > 0:
        ks_stat, ks_p = stats.kstest((values - mean) / std, "norm")
    return {
        "name": name,
        "values": values,
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


def _group_label(value):
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except Exception:
        pass
    return str(value)


def _resolve_samples(df, params):
    data_format = params.get("data_format") or "样本在同一列"
    test_var = params.get("test_var", "")
    if data_format == "样本在不同列":
        reference_var = params.get("reference_var", "")
        if test_var not in df.columns or reference_var not in df.columns:
            return None, None, "检验样本或参考样本不存在。"
        test = _sample_stats(test_var, df[test_var])
        reference = _sample_stats(reference_var, df[reference_var])
        return test, reference, ""

    group_var = params.get("group_var", "")
    if group_var not in df.columns or test_var not in df.columns:
        return None, None, "分组变量或检验变量不存在。"
    temp = df[[group_var, test_var]].copy()
    temp[test_var] = pd.to_numeric(temp[test_var], errors="coerce")
    temp = temp.dropna()
    groups = list(pd.Series(temp[group_var]).dropna().unique())
    if len(groups) != 2:
        return None, None, "样本ID必须只存在两个可区分的水平。"
    reference_level = str(params.get("reference_level", "")).strip()
    ref_group = None
    if reference_level:
        for group in groups:
            if str(group) == reference_level or _group_label(group) == reference_level:
                ref_group = group
                break
    if ref_group is None:
        ref_group = groups[1]
    test_group = next(group for group in groups if group != ref_group)
    test = _sample_stats(f"{test_var}({group_var}={_group_label(test_group)})", temp.loc[temp[group_var] == test_group, test_var])
    reference = _sample_stats(f"{test_var}({group_var}={_group_label(ref_group)})", temp.loc[temp[group_var] == ref_group, test_var])
    return test, reference, ""


def _welch_df(test, reference, se_sq):
    n1, n2 = test["n"], reference["n"]
    v1 = test["std"] ** 2 / n1
    v2 = reference["std"] ** 2 / n2
    denominator = (v1 ** 2) / (n1 - 1) + (v2 ** 2) / (n2 - 1)
    return (se_sq ** 2) / denominator if denominator > 0 else n1 + n2 - 2


def _estimate(test, reference, relationship):
    if relationship == REL_RATIO:
        ratio = test["mean"] / reference["mean"] if reference["mean"] else np.nan
        se = abs(ratio) * np.sqrt((test["se"] / test["mean"]) ** 2 + (reference["se"] / reference["mean"]) ** 2)
        return ratio, se, "比值"
    if relationship == REL_LOG_RATIO:
        ratio = test["mean"] / reference["mean"] if reference["mean"] else np.nan
        value = np.log(ratio) if ratio > 0 else np.nan
        se = np.sqrt((test["se"] / test["mean"]) ** 2 + (reference["se"] / reference["mean"]) ** 2)
        return value, se, "对数比值"
    se_sq = test["std"] ** 2 / test["n"] + reference["std"] ** 2 / reference["n"]
    return test["mean"] - reference["mean"], np.sqrt(se_sq), "差值"


def _bounds(params, reference, relationship):
    lower = _to_float(params.get("lower", -0.1), -0.1)
    upper = _to_float(params.get("upper", 0.1), 0.1)
    if lower > upper:
        lower, upper = upper, lower
    if relationship == REL_DIFF and _to_bool(params.get("scale_by_reference"), True):
        lower *= reference["mean"]
        upper *= reference["mean"]
        if lower > upper:
            lower, upper = upper, lower
    return lower, upper


def _test_rows(alternative, value, se, dfree, lower, upper):
    if se <= 0 or not np.isfinite(se):
        return [], False

    def t_gt(bound):
        t_value = (value - bound) / se
        return t_value, stats.t.sf(t_value, dfree)

    def t_lt(bound):
        t_value = (value - bound) / se
        return t_value, stats.t.cdf(t_value, dfree)

    if alternative == ALT_GT_REF:
        t_value, p_value = t_gt(0)
        return [["差值 ≤ 0", _fmt(dfree, 0), _fmt(t_value, 3), _fmt_p(p_value)]], p_value < 0.05
    if alternative == ALT_LT_REF:
        t_value, p_value = t_lt(0)
        return [["差值 ≥ 0", _fmt(dfree, 0), _fmt(t_value, 3), _fmt_p(p_value)]], p_value < 0.05
    if alternative == ALT_GT_LOWER:
        t_value, p_value = t_gt(lower)
        return [[f"差值 ≤ {_fmt(lower, 3)}", _fmt(dfree, 0), _fmt(t_value, 3), _fmt_p(p_value)]], p_value < 0.05
    if alternative == ALT_LT_UPPER:
        t_value, p_value = t_lt(upper)
        return [[f"差值 ≥ {_fmt(upper, 3)}", _fmt(dfree, 0), _fmt(t_value, 3), _fmt_p(p_value)]], p_value < 0.05
    lower_t, lower_p = t_gt(lower)
    upper_t, upper_p = t_lt(upper)
    return [
        [f"差值 ≤ {_fmt(lower, 3)}", _fmt(dfree, 0), _fmt(lower_t, 3), _fmt_p(lower_p)],
        [f"差值 ≥ {_fmt(upper, 3)}", _fmt(dfree, 0), _fmt(upper_t, 3), _fmt_p(upper_p)],
        [f"原假设：差值 ≤ {_fmt(lower, 3)} 或 差值 ≥ {_fmt(upper, 3)}", "", "", ""],
        [f"备择假设：{_fmt(lower, 3)} < 差值 < {_fmt(upper, 3)}", "", "", ""],
    ], max(lower_p, upper_p) < 0.05


def _chart(value, ci_low, ci_high, lower, upper):
    return {
        "chartType": "equivalence_interval",
        "title": "等价检验可视化",
        "data": {
            "difference": round(float(value), 6),
            "ciLow": round(float(ci_low), 6),
            "ciHigh": round(float(ci_high), 6),
            "lower": round(float(lower), 6),
            "upper": round(float(upper), 6),
            "ciLabel": "对等项的95% CI",
        },
    }


def run(df, params):
    test, reference, error = _resolve_samples(df, params)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}
    if test["n"] < 3 or reference["n"] < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    relationship = params.get("relationship") or REL_DIFF
    alternative = params.get("alternative") or ALT_INTERVAL
    value, se, value_label = _estimate(test, reference, relationship)
    se_sq = test["std"] ** 2 / test["n"] + reference["std"] ** 2 / reference["n"]
    dfree = _welch_df(test, reference, se_sq)
    lower, upper = _bounds(params, reference, relationship)
    t_crit = stats.t.ppf(0.975, dfree)
    ci_low = value - t_crit * se
    ci_high = value + t_crit * se
    test_rows, tost_passed = _test_rows(alternative, value, se, dfree, lower, upper)
    ci_inside = ci_low > lower and ci_high < upper
    equivalent = ci_inside and tost_passed if alternative == ALT_INTERVAL else tost_passed

    desc_headers = ["变量", "N", "均值", "标准差", "均值标准误", "偏度", "峰度", "S-W检验", "K-S检验"]
    desc_rows = []
    for item in [test, reference]:
        desc_rows.append([
            item["name"],
            str(item["n"]),
            _fmt(item["mean"], 3),
            _fmt(item["std"], 3),
            _fmt(item["se"], 3),
            _fmt(item["skew"], 3),
            _fmt(item["kurtosis"], 3),
            _normality_expr(item["sw_stat"], item["sw_p"]),
            _normality_expr(item["ks_stat"], item["ks_p"]),
        ])

    ci_headers = [value_label, "SE", "对等项的 95% CI", "等价区间"]
    ci_rows = [
        [_fmt(value, 3), _fmt(se, 3), f"({_fmt(ci_low, 3)}, {_fmt(ci_high, 3)})", f"({_fmt(lower, 3)}, {_fmt(upper, 3)})"],
        [f"{value_label}：均值({test['name']}) - 均值({reference['name']})", "", "", ""],
    ]
    conclusion = (
        f"置信区间({_fmt(ci_low, 3)}, {_fmt(ci_high, 3)})"
        f"{'完全落在' if ci_inside else '不完全落在'}等价区间({_fmt(lower, 3)}, {_fmt(upper, 3)})内，"
        f"认为均值({test['name']})与均值({reference['name']}){'等价' if equivalent else '不等价'}。"
    )

    sections = [
        _sec_advice(
            "1. 数据特征与分布判断：计算样本核心统计量（如均值、标准差、标准误、偏度、峰度等）；\n"
            "2. 置信区间法判断等价性：构建与显著性水平对应的置信区间，判断其是否完全落在等价界值范围内；\n"
            "3. P值法辅助验证：通过双单侧t检验计算P值，与置信区间法形成相互印证。",
            title="分析步骤",
        ),
        _sec_table("输出结果1：描述性统计", desc_headers, desc_rows, description="上表展示了描述统计结果，因双样本等价检验要求数据近似正态，若数据非正态可能会导致结论偏差。"),
        _sec_smart("；".join([
            f"{row['name']}样本N={row['n']}，S-W检验显著性P值为{_fmt_p(row['sw_p'])}"
            for row in [test, reference]
        ]) + "。"),
        _sec_table("输出结果2：置信区间与等价限值比较", ci_headers, ci_rows, description="上表展示了置信区间与等价限值对比结果，若置信区间完全落在预设的等价界值范围内，则拒绝原假设，认为检验均值与参考均值等价。"),
        _sec_smart(conclusion),
        _sec_table("输出结果3：等价检验", ["原假设", "自由度", "T值", "P值"], test_rows, note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001", description="上表展示了等价检验结果，若原假设P值小于设定的显著性水平（如0.05），则从概率角度支持等价结论。"),
        _sec_charts("输出结果4：等价检验可视化", [_chart(value, ci_low, ci_high, lower, upper)], "上图展示了等价检验可视化结果，若置信区间完全落在预设的等价界值范围内，则认为总体参数与目标值等价。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["原假设", "自由度", "T值", "P值"], "rows": test_rows, "description": conclusion, "sections": sections}
