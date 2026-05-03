# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "friedman_test"
METHOD_META = {'label': '多配对样本Friedman检验',
 'category': '数据检验',
 'description': '比较三个及以上配对样本在秩次上的差异',
 'order': 50,
 'slots': [{'key': 'variables', 'label': '配对变量', 'type': 'multiple', 'accept': 'numeric', 'min': 3, 'hint': '放入三个及以上配对变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Friedman 检验至少需要 3 个配对变量。"}
    temp = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(temp) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    stat, p_val = friedmanchisquare(*[temp[var] for var in variables])
    desc_rows = [[var, _fmt(temp[var].median(), 4)] for var in variables]
    sections = [
        _sec_table("变量描述", ["变量", "中位数"], desc_rows),
        _sec_table("Friedman 检验", ["χ²", "p"], [[_fmt(stat, 4), _fmt(p_val, 4)]]),
        _sec_advice("Friedman 检验适合三个及以上配对样本的非参数比较。"),
        _sec_smart(f"Friedman 检验完成，p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["变量", "中位数"], "rows": desc_rows, "description": "Friedman 检验完成。", "sections": sections}
