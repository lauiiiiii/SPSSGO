# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "cross_tabulation"
METHOD_META = {'label': '列联（交叉）分析',
 'category': '数据概览',
 'description': '查看两个分类变量的交叉分布，并给出卡方检验与关联强度',
 'order': 20,
 'slots': [{'key': 'var1',
            'label': '行变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第一个分类变量'},
           {'key': 'var2',
            'label': '列变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第二个分类变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "cross_labels"

def cross_tabulation_analysis(df, params):
    """
    列联（交叉）分析，包含交叉频数、行百分比与卡方检验摘要

    @param df: 数据 DataFrame
    @param params: 包含 var1, var2 的参数字典
    @return: 含 sections 的结果字典
    """
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    var1_labels = params.get("var1_labels", {})
    var2_labels = params.get("var2_labels", {})
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": "列联（交叉）分析", "headers": [], "rows": [], "description": "变量不存在。"}

    temp = df[[var1, var2]].dropna()
    if temp.empty:
        return {"name": "列联（交叉）分析", "headers": [], "rows": [], "description": "有效样本不足，无法完成列联分析。"}

    ct = pd.crosstab(temp[var1], temp[var2])
    chi2, p, dof, expected = chi2_contingency(ct)
    n_total = int(ct.to_numpy().sum())
    min_dim = min(ct.shape[0], ct.shape[1]) - 1
    cramers_v = np.sqrt(chi2 / (n_total * min_dim)) if min_dim > 0 and n_total > 0 else 0
    v_level = "强" if cramers_v >= 0.5 else ("中等" if cramers_v >= 0.3 else "弱")

    col_headers = [var2_labels.get(str(c), str(c)) for c in ct.columns]
    headers = [f"{var1}\\{var2}"] + col_headers + ["合计"]

    count_rows = []
    for idx in ct.index:
        label = var1_labels.get(str(idx), str(idx))
        values = [str(int(v)) for v in ct.loc[idx].tolist()]
        count_rows.append([label] + values + [str(int(ct.loc[idx].sum()))])
    count_rows.append(["合计"] + [str(int(v)) for v in ct.sum(axis=0).tolist()] + [str(n_total)])

    row_pct_rows = []
    for idx in ct.index:
        label = var1_labels.get(str(idx), str(idx))
        total = ct.loc[idx].sum()
        pct_values = [_fmt(v / total * 100 if total else 0, 1) + "%" for v in ct.loc[idx].tolist()]
        row_pct_rows.append([label] + pct_values + ["100.0%"])

    expected_headers = [f"{var1}\\{var2}"] + col_headers
    expected_rows = []
    expected_df = pd.DataFrame(expected, index=ct.index, columns=ct.columns)
    for idx in expected_df.index:
        label = var1_labels.get(str(idx), str(idx))
        expected_rows.append([label] + [_fmt(v, 2) for v in expected_df.loc[idx].tolist()])

    sections = []
    sections.append(_sec_table("交叉频数表", headers, count_rows, description="展示两个分类变量组合下的样本频数分布。"))
    sections.append(_sec_table("行百分比表", headers, row_pct_rows, description="展示每个行类别内部在不同列类别上的构成比例。"))
    sections.append(_sec_table("理论频数表", expected_headers, expected_rows, description="理论频数用于辅助判断卡方检验前提是否基本满足。"))

    chi_headers = ["有效样本", "χ²", "df", "p", "Cramer's V", "关联强度"]
    chi_rows = [[str(n_total), _fmt(chi2, 2), str(dof), _fmt(p), _fmt(cramers_v, 3), v_level]]
    sections.append(_sec_table("关联检验结果", chi_headers, chi_rows))

    advice = (
        "列联（交叉）分析用于查看两个分类变量之间的分布关系；\n"
        "第一：先看交叉频数和行百分比，判断不同类别之间的分布差异；\n"
        "第二：若卡方检验p<0.05，说明两个分类变量之间存在统计学显著关联；\n"
        "第三：可结合Cramer's V判断关联强度，V越大说明关联越强。"
    )
    sections.append(_sec_advice(advice))

    smart = (
        f"对{var1}与{var2}进行列联（交叉）分析，共纳入{n_total}个有效样本。"
        f"卡方检验结果显示两变量之间{'存在' if p < 0.05 else '不存在'}显著关联"
        f"（χ²={_fmt(chi2, 2)}，df={dof}，{_p_expr(p)}），"
        f"Cramer's V={_fmt(cramers_v, 3)}，关联强度{v_level}。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": f"列联（交叉）分析：{var1} × {var2}", "headers": headers, "rows": count_rows, "description": smart, "sections": sections}

run = cross_tabulation_analysis
