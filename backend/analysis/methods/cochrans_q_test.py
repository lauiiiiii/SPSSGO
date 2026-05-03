# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "cochrans_q_test"
METHOD_META = {'label': "Cochran's Q检验",
 'category': '数据检验',
 'description': '比较三个及以上相关二分类变量的比例差异',
 'order': 60,
 'slots': [{'key': 'variables', 'label': '二分类变量', 'type': 'multiple', 'accept': 'categorical', 'min': 3, 'hint': '放入三个及以上二分类变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Cochran's Q 检验至少需要 3 个二分类变量。"}
    temp = df[variables].copy()
    for var in variables:
        temp[var] = _selected_mask(temp[var]).astype(int)
    temp = temp.dropna()
    if len(temp) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    result = cochrans_q(temp.to_numpy())
    desc_rows = [[var, str(int(temp[var].sum())), _fmt(temp[var].mean(), 4)] for var in variables]
    sections = [
        _sec_table("变量描述", ["变量", "阳性数", "阳性比例"], desc_rows),
        _sec_table("Cochran's Q 检验", ["Q", "p"], [[_fmt(result.statistic, 4), _fmt(result.pvalue, 4)]]),
        _sec_advice("Cochran's Q 适用于三个及以上相关样本的二分类比例比较。"),
        _sec_smart(f"Cochran's Q 检验完成，p 值为 {_fmt(result.pvalue, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["变量", "阳性数", "阳性比例"], "rows": desc_rows, "description": "Cochran's Q 检验完成。", "sections": sections}
