# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "wilcoxon_signed_rank_test"
METHOD_META = {'label': '配对样本Wilcoxon符号秩检验',
 'category': '数据检验',
 'description': '比较两个配对样本在中位数水平上的差异',
 'order': 35,
 'slots': [{'key': 'var1', 'label': '变量1', 'type': 'single', 'accept': 'numeric', 'hint': '放入第一个配对变量'},
           {'key': 'var2', 'label': '变量2', 'type': 'single', 'accept': 'numeric', 'hint': '放入第二个配对变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "配对变量不存在。"}
    temp = df[[var1, var2]].apply(pd.to_numeric, errors="coerce").dropna()
    diff = temp[var1] - temp[var2]
    diff = diff[diff != 0]
    if len(diff) < 1:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有足够的非零差值样本。"}
    stat, p_val = wilcoxon(temp[var1], temp[var2])
    rows = [[f"{var1} vs {var2}", str(len(temp)), _fmt(temp[var1].median(), 4), _fmt(temp[var2].median(), 4), _fmt(stat, 4), _fmt(p_val, 4)]]
    sections = [
        _sec_table("配对样本Wilcoxon结果", ["配对变量", "N", "变量1中位数", "变量2中位数", "W", "p"], rows),
        _sec_advice("配对样本 Wilcoxon 符号秩检验适用于配对数据且不满足正态假设时。"),
        _sec_smart(f"配对样本 Wilcoxon 检验完成，{var1} 与 {var2} 的 p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["配对变量", "N", "变量1中位数", "变量2中位数", "W", "p"], "rows": rows, "description": "配对样本 Wilcoxon 检验完成。", "sections": sections}
