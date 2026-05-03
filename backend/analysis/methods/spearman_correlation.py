# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "spearman_correlation"
METHOD_META = {'label': 'Spearman 等级相关',
 'category': '数据检验',
 'description': '分析两个或多个变量之间的等级相关程度（非参数）',
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入需要分析相关性的变量（至少2个）'}],
 'options': [],
 'param_builder': 'direct'}

def spearman_correlation(df, params):
    """
    Spearman 等级相关分析

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": "Spearman相关分析", "headers": [], "rows": [], "description": "需要至少2个变量。"}

    headers = ["变量"] + variables
    rows = []
    descs = []
    for v1 in variables:
        row = [v1]
        for v2 in variables:
            s1 = pd.to_numeric(df[v1], errors="coerce")
            s2 = pd.to_numeric(df[v2], errors="coerce")
            mask = s1.notna() & s2.notna()
            if v1 == v2:
                row.append("1")
            else:
                rho, p = spearmanr(s1[mask], s2[mask])
                row.append(_fmt(rho) + _sig(p))
        rows.append(row)

    for v1, v2 in combinations(variables, 2):
        s1 = pd.to_numeric(df[v1], errors="coerce")
        s2 = pd.to_numeric(df[v2], errors="coerce")
        mask = s1.notna() & s2.notna()
        rho, p = spearmanr(s1[mask], s2[mask])
        direction = "正" if rho > 0 else "负"
        if p < 0.05:
            descs.append(f"{v1}与{v2}呈显著{direction}相关（ρ={_fmt(rho, 3)}，{_p_expr(p)}）")

    note = "注：*p<0.05，**p<0.01，***p<0.001。"
    desc = f"采用Spearman等级相关分析。{'；'.join(descs)}。{note}" if descs else f"Spearman相关分析结果如表所示。{note}"

    sections = []
    sections.append(_sec_table("Spearman等级相关系数矩阵", headers, rows, note=note))
    advice = (
        "Spearman等级相关是一种非参数相关分析方法，适用于顺序变量或不满足正态分布假设的数据；\n"
        "第一：|ρ|≥0.8为高度相关，0.5~0.8为中等相关，0.3~0.5为低相关；\n"
        "第二：p<0.05表示相关系数具有统计学意义。"
    )
    sections.append(_sec_advice(advice))
    smart = f"采用Spearman等级相关分析。{'；'.join(descs)}。" if descs else "各变量之间的Spearman相关均未达到统计学显著水平。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_CORRELATION))

    return {"name": "Spearman相关分析", "headers": headers, "rows": rows, "description": desc, "sections": sections}

run = spearman_correlation
