# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "chi_square"
METHOD_META = {'label': '卡方检验',
 'category': '差异对比分析包',
 'description': '检验两个分类变量之间是否存在显著关联',
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

def chi_square_test(df, params):
    """
    卡方检验，含 Cramer's V 效应量

    @param df: 数据 DataFrame
    @param params: 包含 var1, var2 的参数字典
    @return: 含 sections 的结果字典
    """
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    var1_labels = params.get("var1_labels", {})
    var2_labels = params.get("var2_labels", {})
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": "卡方检验", "headers": [], "rows": [], "description": "变量不存在。"}

    ct = pd.crosstab(df[var1], df[var2])
    chi2, p, dof, expected = chi2_contingency(ct, correction=False)
    cc_chi2 = None
    cc_p = None
    if ct.shape == (2, 2):
        cc_chi2, cc_p, _, _ = chi2_contingency(ct, correction=True)
    n_total = ct.sum().sum()
    min_dim = min(ct.shape[0], ct.shape[1]) - 1
    cramers_v = np.sqrt(chi2 / (n_total * min_dim)) if min_dim > 0 and n_total > 0 else 0

    headers = [f"{var1}\\{var2}"] + [var2_labels.get(str(c), str(c)) for c in ct.columns] + ["合计"]
    rows = []
    for idx in ct.index:
        row = [var1_labels.get(str(idx), str(idx))] + [str(int(v)) for v in ct.loc[idx]] + [str(int(ct.loc[idx].sum()))]
        rows.append(row)
    totals = ["合计"] + [str(int(v)) for v in ct.sum(axis=0)] + [str(int(ct.sum().sum()))]
    rows.append(totals)

    sections = []
    sections.append(_sec_table("交叉表", headers, rows, description="交叉表展示了两个分类变量的频数分布。"))

    # 卡方检验结果表
    v_level = "强" if cramers_v >= 0.5 else ("中等" if cramers_v >= 0.3 else "弱")
    chi_headers = ["统计量", "值", "df", "p", "说明"]
    chi_rows = [["Pearson χ²", _fmt(chi2, 3), str(dof), _fmt(p, 4), "主检验结果"]]
    if cc_chi2 is not None:
        chi_rows.append(["连续性校正", _fmt(cc_chi2, 3), "1", _fmt(cc_p, 4), "2x2 列联表参考"])
    chi_rows.append(["Cramer's V", _fmt(cramers_v, 3), "", "", f"关联强度{v_level}"])
    sections.append(_sec_table("卡方检验结果", chi_headers, chi_rows))

    advice = (
        "卡方检验用于检验两个分类变量之间是否存在显著关联；\n"
        "第一：p<0.05说明两变量之间存在显著关联；\n"
        "第二：Cramer's V衡量关联强度，V≥0.5为强关联，0.3~0.5为中等，<0.3为弱关联。"
    )
    sections.append(_sec_advice(advice))

    smart = (
        f"对{var1}与{var2}进行卡方检验，结果表明两变量之间"
        f"{'存在' if p < 0.05 else '不存在'}显著关联"
        f"（χ²={_fmt(chi2, 2)}，df={dof}，{_p_expr(p)}），"
        f"Cramer's V={_fmt(cramers_v, 3)}，关联强度{v_level}。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": f"卡方检验：{var1} × {var2}", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = chi_square_test
