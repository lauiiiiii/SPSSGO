# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "kappa_consistency"
METHOD_META = {'label': 'Kappa一致性检验',
 'category': '数据检验',
 'description': '评估两个评价者或两次分类结果之间的一致性',
 'order': 65,
 'slots': [{'key': 'rater1', 'label': '评价者1', 'type': 'single', 'accept': 'categorical', 'hint': '放入第一个分类变量'},
           {'key': 'rater2', 'label': '评价者2', 'type': 'single', 'accept': 'categorical', 'hint': '放入第二个分类变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    rater1 = params.get("rater1", "")
    rater2 = params.get("rater2", "")
    if rater1 not in df.columns or rater2 not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "评价变量不存在。"}
    temp = df[[rater1, rater2]].dropna().astype(str)
    if len(temp) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    kappa = cohen_kappa_score(temp[rater1], temp[rater2])
    agree = float((temp[rater1] == temp[rater2]).mean())
    rows = [["观察一致率", _fmt(agree, 4)], ["Kappa", _fmt(kappa, 4)]]
    sections = [
        _sec_table("Kappa 一致性结果", ["指标", "值"], rows),
        _sec_advice("Kappa 越接近 1，说明一致性越强；接近 0 说明与随机一致性相差不大。"),
        _sec_smart(f"Kappa 一致性检验完成，Kappa={_fmt(kappa, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "值"], "rows": rows, "description": "Kappa 一致性检验完成。", "sections": sections}
