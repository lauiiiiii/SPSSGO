# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "survey_cross_tab"
METHOD_META = {'label': '交叉表（调研专项）',
 'category': '问卷分析包',
 'description': '输出交叉频数、行百分比和列百分比，适合调研问卷分析场景',
 'order': 60,
 'slots': [{'key': 'var1',
            'label': '行变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第一个调研变量'},
           {'key': 'var2',
            'label': '列变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第二个调研变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "cross_labels"

def survey_cross_tabulation(df, params):
    """
    调研专项交叉表：在交叉频数基础上追加行百分比和列百分比
    """
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    var1_labels = params.get("var1_labels", {})
    var2_labels = params.get("var2_labels", {})
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": "交叉表（调研专项）", "headers": [], "rows": [], "description": "变量不存在。"}

    temp = df[[var1, var2]].dropna()
    if temp.empty:
        return {"name": "交叉表（调研专项）", "headers": [], "rows": [], "description": "有效样本不足。"}

    ct = pd.crosstab(temp[var1], temp[var2])
    chi2, p, dof, _ = chi2_contingency(ct)
    headers = [f"{var1}\\{var2}"] + [var2_labels.get(str(c), str(c)) for c in ct.columns] + ["合计"]
    count_rows = []
    row_pct_rows = []
    col_pct_rows = []

    for idx in ct.index:
        label = var1_labels.get(str(idx), str(idx))
        count_values = [int(v) for v in ct.loc[idx].tolist()]
        total = sum(count_values)
        count_rows.append([label] + [str(v) for v in count_values] + [str(total)])
        row_pct_rows.append([label] + [_fmt(v / total * 100 if total else 0, 1) + "%" for v in count_values] + ["100.0%"])

    col_sums = ct.sum(axis=0)
    for idx in ct.index:
        label = var1_labels.get(str(idx), str(idx))
        pct_values = [_fmt(ct.loc[idx, col] / col_sums[col] * 100 if col_sums[col] else 0, 1) + "%" for col in ct.columns]
        col_pct_rows.append([label] + pct_values + ["—"])

    count_rows.append(["合计"] + [str(int(v)) for v in col_sums.tolist()] + [str(int(col_sums.sum()))])

    sections = []
    sections.append(_sec_table("交叉频数表", headers, count_rows, description="展示两个调研变量在不同类别组合下的样本数量。"))
    sections.append(_sec_table("行百分比表", headers, row_pct_rows, description="展示每个行变量类别内部的列变量构成比例。"))
    sections.append(_sec_table("列百分比表", headers, col_pct_rows, description="展示每个列变量类别内部的行变量构成比例。"))
    sections.append(_sec_table("卡方检验结果", ["χ²", "df", "p"], [[_fmt(chi2, 2), str(dof), _fmt(p)]]))
    smart = (
        f"对{var1}与{var2}进行调研专项交叉分析，卡方检验结果"
        f"{'显著' if p < 0.05 else '不显著'}（χ²={_fmt(chi2, 2)}，df={dof}，{_p_expr(p)}）。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": f"交叉表（调研专项）：{var1} × {var2}", "headers": headers, "rows": count_rows, "description": smart, "sections": sections}

run = survey_cross_tabulation
