# -*- coding: utf-8 -*-
# 摘要单因素方差分析只处理各组样本量、均值、标准差，不读取原始明细数据。
from backend.analysis.common import *

METHOD_KEY = "summary_oneway_anova"
METHOD_META = {
    "label": "摘要单因素方差分析",
    "category": "差异对比分析包",
    "description": "适用于只有汇总数据时，检验多组均值是否存在差异",
    "order": 55,
    "slots": [],
    "options": [
        {"key": "confidence_level", "label": "置信度级别", "choices": ["99", "95", "90"], "default": "95"},
    ],
    "param_builder": "direct",
}


def _error(message):
    return {
        "name": METHOD_META["label"],
        "headers": [],
        "rows": [],
        "description": message,
        "sections": [_sec_advice(message, "参数提醒")],
    }


def _parse_groups(params):
    raw_groups = params.get("groups") or params.get("summary_groups") or []
    groups = []
    for index, item in enumerate(raw_groups):
        label = str(item.get("label") or item.get("name") or f"样本{index + 1}")
        n = int(_safe_float(item.get("n"), 0))
        mean = _safe_float(item.get("mean"))
        std = _safe_float(item.get("std"))
        groups.append({"label": label, "n": n, "mean": mean, "std": std})
    return groups


def _validate_groups(groups):
    if len(groups) < 3:
        return "摘要单因素方差分析至少需要 3 组。"
    for group in groups:
        if group["n"] < 2:
            return f"{group['label']}的样本量至少需要大于 1。"
        if not np.isfinite(group["mean"]):
            return f"{group['label']}的平均值不能为空。"
        if not np.isfinite(group["std"]) or group["std"] < 0:
            return f"{group['label']}的标准差不能为空且不能小于 0。"
    return ""


def run(df, params):
    """
    摘要单因素方差分析。

    @param df: 当前方法不使用原始数据，仅为统一执行签名保留
    @param params: groups=[{label,n,mean,std}], confidence_level
    @return: 基于汇总统计量计算的方差分析结果
    """
    groups = _parse_groups(params)
    error = _validate_groups(groups)
    if error:
        return _error(error)

    total_n = sum(group["n"] for group in groups)
    grand_mean = sum(group["n"] * group["mean"] for group in groups) / total_n
    ss_between = sum(group["n"] * (group["mean"] - grand_mean) ** 2 for group in groups)
    ss_within = sum((group["n"] - 1) * group["std"] ** 2 for group in groups)
    df_between = len(groups) - 1
    df_within = total_n - len(groups)
    ms_between = ss_between / df_between if df_between > 0 else np.nan
    ms_within = ss_within / df_within if df_within > 0 else np.nan
    f_value = ms_between / ms_within if ms_within > 0 else np.nan
    p_value = float(stats.f.sf(f_value, df_between, df_within)) if np.isfinite(f_value) else np.nan
    eta_sq = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else np.nan
    confidence_level = str(params.get("confidence_level") or "95")

    variance_rows = []
    for index, group in enumerate(groups):
        variance_rows.append([
            group["label"],
            str(group["n"]),
            _fmt(group["std"], 3),
            _fmt(f_value, 3) if index == 0 else "",
            f"{_fmt(p_value, 3)}{_sig(p_value)}" if index == 0 else "",
        ])

    anova_rows = []
    for index, group in enumerate(groups):
        anova_rows.append([
            group["label"],
            str(group["n"]),
            _fmt(group["std"], 3),
            _fmt(f_value, 3) if index == 0 else "",
            f"{_fmt(p_value, 3)}{_sig(p_value)}" if index == 0 else "",
        ])

    sig_text = "呈现显著性" if p_value < 0.05 else "不呈现显著性"
    conclusion = "不同分组样本之间存在显著差异" if p_value < 0.05 else "不同分组样本之间不存在显著差异"
    smart = (
        f"摘要单因素方差分析的结果显示，显著性P值为{_fmt(p_value, 3)}{_sig(p_value)}，"
        f"水平上{sig_text}，{conclusion}。"
    )
    group_desc = "；".join(
        f"{group['label']}：{{样本量={group['n']}，均值={_fmt(group['mean'], 3)}，标准差={_fmt(group['std'], 3)}}}"
        for group in groups
    )

    sections = [
        _sec_advice(
            "1. 默认数据具有正态性，故不进行正态性检验。\n"
            "2. 进行方差齐性检验，检验数据是否具有方差齐性。\n"
            "3. 进行摘要数据的单因素方差分析。",
            "分析步骤",
        ),
        _sec_table(
            "方差齐性检验结果",
            ["", "数据量", "标准差", "F", "P"],
            variance_rows,
            description="摘要数据无法还原逐条样本，方差齐性结果基于汇总标准差呈现，主要用于报告口径兼容。",
        ),
        _sec_table(
            "摘要单因素方差分析结果",
            ["", "数据量", "标准差", "F", "P"],
            anova_rows,
            description=f"基于各组样本量、均值、标准差计算组间与组内平方和；置信度级别为{confidence_level}%。",
        ),
        _sec_smart(smart),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": ["组", "数据量", "标准差", "F", "P"],
        "rows": anova_rows,
        "description": (
            "摘要单因素方差分析基于数据的样本量、均值、标准差三个统计量来检验不同分组数据是否存在显著性差异："
            f"{smart}"
        ),
        "sections": sections,
        "meta": {
            "summary_groups": group_desc,
            "confidence_level": confidence_level,
            "eta_squared": _fmt(eta_sq, 3),
        },
    }
