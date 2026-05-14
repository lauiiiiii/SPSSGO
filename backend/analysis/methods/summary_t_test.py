# -*- coding: utf-8 -*-
# 摘要 T 检验只处理已汇总的均值、标准差、样本量，不读取原始明细数据。
from backend.analysis.common import *

METHOD_KEY = "summary_t_test"
METHOD_META = {
    "label": "摘要T检验",
    "category": "差异对比分析包",
    "description": "适用于只有汇总数据时，检验均值或均值差是否符合指定假设",
    "order": 20,
    "slots": [],
    "options": [
        {"key": "test_type", "label": "检验类型", "choices": ["one_sample", "independent"], "default": "one_sample"},
        {"key": "confidence_level", "label": "置信水平", "choices": ["90", "95", "99"], "default": "95"},
        {"key": "alternative", "label": "假设检验", "choices": ["等于", "大于", "小于"], "default": "等于"},
    ],
    "param_builder": "direct",
}


def _num(params, key, default=np.nan):
    return _safe_float(params.get(key), default)


def _confidence(params):
    value = _num(params, "confidence_level", 95)
    if value in (90, 95, 99):
        return value / 100
    if value in (0.9, 0.95, 0.99):
        return value
    return 0.95


def _hypothesis_sign(alternative):
    if alternative == "大于":
        return ">"
    if alternative == "小于":
        return "<"
    return "="


def _support_p(t_value, alternative, dfree):
    """
    SPSSAU 的摘要 t 检验是验证用户输入的假设方向，这里别改成固定双侧 p。
    等于使用常规双侧 p；大于/小于使用对应方向的支持概率口径。
    """
    if not np.isfinite(t_value):
        return np.nan
    if alternative == "大于":
        return float(stats.t.cdf(t_value, dfree))
    if alternative == "小于":
        return float(stats.t.sf(t_value, dfree))
    return float(2 * stats.t.sf(abs(t_value), dfree))


def _conclusion(p_value, ci, alternative):
    alpha = 1 - ci
    if not np.isfinite(p_value):
        return "—"
    return "假设成立" if p_value > alpha else "假设不成立"


def _fmt_ci(low, high):
    return f"{_fmt(low, 3)} ~ {_fmt(high, 3)}"


def _validate_number(value, label):
    if not np.isfinite(value):
        return f"{label}不能为空。"
    return ""


def _validate_positive(value, label, allow_zero=False):
    if not np.isfinite(value):
        return f"{label}不能为空。"
    if allow_zero and value < 0:
        return f"{label}不能小于 0。"
    if not allow_zero and value <= 0:
        return f"{label}必须大于 0。"
    return ""


def _one_sample(params):
    mean = _num(params, "mean")
    std = _num(params, "std")
    n = int(_num(params, "n", 0))
    test_value = _num(params, "test_value", 0)
    ci = _confidence(params)
    alternative = params.get("alternative") or "等于"

    errors = [
        _validate_number(mean, "平均值"),
        _validate_positive(std, "标准差", allow_zero=False),
        _validate_positive(n, "样本量", allow_zero=False),
        _validate_number(test_value, "对比均值"),
    ]
    errors = [item for item in errors if item]
    if errors:
        return _error("；".join(errors))
    if n < 2:
        return _error("样本量至少需要大于 1。")

    se = std / np.sqrt(n)
    dfree = n - 1
    mean_diff = mean - test_value
    ci_label = f"{int(ci * 100)}% CI"
    ci_low = mean - stats.t.ppf(1 - (1 - ci) / 2, dfree) * se
    ci_high = mean + stats.t.ppf(1 - (1 - ci) / 2, dfree) * se
    t_value = mean_diff / se if se > 0 else np.nan
    p_value = _support_p(t_value, alternative, dfree)
    sign = _hypothesis_sign(alternative)
    conclusion = _conclusion(p_value, ci, alternative)

    ci_headers = ["项", "样本量", "平均值", "标准差", "标准误", ci_label]
    ci_rows = [["值", str(n), _fmt(mean, 3), _fmt(std, 3), _fmt(se, 3), _fmt_ci(ci_low, ci_high)]]
    test_headers = ["项", "样本量", "平均值", "检验均值", "假设", "t", "p", "置信水平", "检验结论"]
    hypothesis = f"{_fmt(mean, 3)}{sign}{_fmt(test_value, 3)}"
    test_rows = [[
        "值",
        str(n),
        _fmt(mean, 3),
        _fmt(test_value, 3),
        hypothesis,
        _fmt(t_value, 3),
        _fmt(p_value, 3),
        f"{int(ci * 100)}%",
        conclusion,
    ]]
    smart = (
        f"本次单样本T检验的检验原假设为“{hypothesis}”，"
        f"检验显示在{int(ci * 100)}%置信水平下{conclusion}。"
    )
    sections = [
        _sec_table("单样本t检验置信区间", ci_headers, ci_rows),
        _sec_advice(
            "单样本t检验研究数据均值是否明显等于、大于或小于某个数字，以及均值的置信区间情况。\n"
            "第一：上表列出均值的置信区间；\n"
            "第二：下表列出假设检验结果。"
        ),
        _sec_smart(
            f"从上表可知：研究样本数据(n={n})的均值为{_fmt(mean, 3)}，标准差为{_fmt(std, 3)}，"
            f"计算得出{int(ci * 100)}%的置信区间为({ci_label}:{_fmt_ci(ci_low, ci_high)})。"
        ),
        _sec_table("单样本t检验假设检验", test_headers, test_rows),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": test_headers,
        "rows": test_rows,
        "description": smart,
        "sections": sections,
    }


def _independent(params):
    mean1 = _num(params, "group1_mean")
    std1 = _num(params, "group1_std")
    n1 = int(_num(params, "group1_n", 0))
    mean2 = _num(params, "group2_mean")
    std2 = _num(params, "group2_std")
    n2 = int(_num(params, "group2_n", 0))
    test_value = _num(params, "diff_test_value", 0)
    ci = _confidence(params)
    alternative = params.get("alternative") or "等于"

    errors = [
        _validate_number(mean1, "第1组平均值"),
        _validate_positive(std1, "第1组标准差", allow_zero=False),
        _validate_positive(n1, "第1组样本量", allow_zero=False),
        _validate_number(mean2, "第2组平均值"),
        _validate_positive(std2, "第2组标准差", allow_zero=False),
        _validate_positive(n2, "第2组样本量", allow_zero=False),
        _validate_number(test_value, "差值对比"),
    ]
    errors = [item for item in errors if item]
    if errors:
        return _error("；".join(errors))
    if n1 < 2 or n2 < 2:
        return _error("两组样本量都至少需要大于 1。")

    dfree = n1 + n2 - 2
    pooled_var = ((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / dfree
    se_diff = np.sqrt(pooled_var * (1 / n1 + 1 / n2))
    mean_diff = mean1 - mean2
    ci_label = f"{int(ci * 100)}% CI"
    crit = stats.t.ppf(1 - (1 - ci) / 2, dfree)
    ci_low = mean_diff - crit * se_diff
    ci_high = mean_diff + crit * se_diff
    t_value = (mean_diff - test_value) / se_diff if se_diff > 0 else np.nan
    p_value = _support_p(t_value, alternative, dfree)
    sign = _hypothesis_sign(alternative)
    conclusion = _conclusion(p_value, ci, alternative)

    ci_headers = [
        "项",
        f"第一组(n={n1}) 平均值",
        "第一组标准差",
        f"第二组(n={n2}) 平均值",
        "第二组标准差",
        "均值差值",
        "差值标准误",
        ci_label,
    ]
    ci_rows = [[
        "值",
        _fmt(mean1, 3),
        _fmt(std1, 3),
        _fmt(mean2, 3),
        _fmt(std2, 3),
        _fmt(mean_diff, 3),
        _fmt(se_diff, 3),
        _fmt_ci(ci_low, ci_high),
    ]]
    hypothesis = f"{_fmt(mean_diff, 3)}{sign}{_fmt(test_value, 3)}"
    test_headers = ["项", "均值差值", "差值检验值", "假设", "t", "p", "置信水平", "检验结论"]
    test_rows = [[
        "值",
        _fmt(mean_diff, 3),
        _fmt(test_value, 3),
        hypothesis,
        _fmt(t_value, 3),
        _fmt(p_value, 3),
        f"{int(ci * 100)}%",
        conclusion,
    ]]
    smart = (
        f"本次独立样本T检验的检验原假设为“{hypothesis}”，"
        f"检验显示在{int(ci * 100)}%置信水平下{conclusion}。"
    )
    sections = [
        _sec_table("独立样本t检验差值置信区间", ci_headers, ci_rows),
        _sec_advice(
            "独立样本t检验研究两组数据均值差值是否相等，或差值与数字对比的情况。\n"
            "第一：上表列出均值差值的置信区间；\n"
            "第二：下表列出假设检验结果。"
        ),
        _sec_smart(
            f"从上表可知：两组数据的均值差值为{_fmt(mean_diff, 3)}，"
            f"计算得出{int(ci * 100)}%的置信区间为({ci_label}:{_fmt_ci(ci_low, ci_high)})。"
        ),
        _sec_table("独立样本t检验差值假设检验", test_headers, test_rows),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": test_headers,
        "rows": test_rows,
        "description": smart,
        "sections": sections,
    }


def _error(message):
    return {
        "name": METHOD_META["label"],
        "headers": [],
        "rows": [],
        "description": message,
        "sections": [_sec_advice(message, "参数提醒")],
    }


def run(df, params):
    """
    摘要 T 检验。

    @param df: 当前方法不使用原始数据，仅为统一执行签名保留
    @param params: 汇总统计量、置信水平、假设方向
    @return: SPSSAU 风格的置信区间表和假设检验表
    """
    test_type = params.get("test_type") or "one_sample"
    if test_type == "independent":
        return _independent(params)
    return _one_sample(params)
