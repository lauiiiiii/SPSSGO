# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "pearson_correlation"
METHOD_META = {'label': '相关性分析',
 'category': '问卷分析包',
 'description': '分析两个或多个定量变量之间的线性相关程度',
 'order': 40,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入需要分析相关性的变量（至少2个）'}],
 'options': [],
 'param_builder': 'direct'}

def pearson_correlation(df, params):
    """
    Pearson 积差相关分析，含相关系数矩阵和显著性

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": "相关性分析", "headers": [], "rows": [], "description": "需要至少2个变量。"}

    corr_m, p_m = {}, {}
    for v1 in variables:
        corr_m[v1], p_m[v1] = {}, {}
        for v2 in variables:
            s1 = pd.to_numeric(df[v1], errors="coerce")
            s2 = pd.to_numeric(df[v2], errors="coerce")
            mask = s1.notna() & s2.notna()
            if mask.sum() < 3 or s1[mask].nunique() < 2 or s2[mask].nunique() < 2:
                r, p = np.nan, np.nan
            else:
                r, p = pearsonr(s1[mask], s2[mask])
            corr_m[v1][v2] = r
            p_m[v1][v2] = p

    headers = ["变量", "M", "SD"] + variables
    rows = []
    for v in variables:
        s = pd.to_numeric(df[v], errors="coerce").dropna()
        row = [v, _fmt(s.mean()), _fmt(s.std())]
        for v2 in variables:
            if v == v2:
                row.append("1")
            else:
                row.append(_fmt(corr_m[v][v2]) + _sig(p_m[v][v2]) if pd.notna(corr_m[v][v2]) else "—")
        rows.append(row)

    descs = []
    for v1, v2 in combinations(variables, 2):
        r = corr_m[v1][v2]
        p = p_m[v1][v2]
        if pd.isna(r) or pd.isna(p):
            descs.append(f"{v1}与{v2}样本不足或变量为常量，无法计算 Pearson 相关。")
            continue
        direction = "正" if r > 0 else "负"
        if p < 0.05:
            descs.append(f"{v1}与{v2}之间呈显著{direction}相关（r={_fmt(r, 3)}，{_p_expr(p)}）")
        else:
            descs.append(f"{v1}与{v2}之间的相关未达到统计学显著水平（r={_fmt(r, 3)}，{_p_expr(p)}）")

    note = "注：*p<0.05，**p<0.01，***p<0.001。"
    desc = f"采用Pearson积差相关分析，结果如表所示。{'；'.join(descs)}。{note}"

    sections = []
    sections.append(_sec_table("相关系数矩阵", headers, rows, note=note,
                               description="对角线为1，上/下三角为各变量间的 Pearson 相关系数，*表示显著水平。"))
    advice = (
        "Pearson相关分析用于衡量两个定量变量之间的线性相关程度；\n"
        "第一：|r|≥0.8为高度相关，0.5~0.8为中等相关，0.3~0.5为低相关，<0.3为微弱相关；\n"
        "第二：p<0.05表示相关系数具有统计学意义；\n"
        "第三：相关不等于因果，需结合专业知识和其他分析方法进行推断。"
    )
    sections.append(_sec_advice(advice))
    smart = f"采用Pearson积差相关分析。{'；'.join(descs)}。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_CORRELATION))

    return {"name": "相关性分析", "headers": headers, "rows": rows, "description": desc, "sections": sections}

run = pearson_correlation
