# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "goodness_of_fit_chi_square"
METHOD_META = {'label': '卡方拟合优度检验',
 'category': '数据检验',
 'description': '检验样本分布是否符合给定理论分布',
 'order': 55,
 'slots': [{'key': 'variable', 'label': '分类变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分类变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variable = params.get("variable", "")
    if variable not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分类变量不存在。"}
    counts = df[variable].dropna().astype(str).value_counts().sort_index()
    if len(counts) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个类别。"}
    expected = np.repeat(counts.sum() / len(counts), len(counts))
    stat, p_val = chisquare(counts.values, f_exp=expected)
    rows = [[cat, str(int(obs)), _fmt(exp, 4)] for cat, obs, exp in zip(counts.index, counts.values, expected)]
    sections = [
        _sec_table("观测频数与理论频数", ["类别", "观测频数", "理论频数"], rows),
        _sec_table("卡方拟合优度检验", ["χ²", "df", "p"], [[_fmt(stat, 4), str(len(counts) - 1), _fmt(p_val, 4)]]),
        _sec_advice("当前版本默认按等概率理论分布进行拟合优度检验。"),
        _sec_smart(f"卡方拟合优度检验完成，p 值为 {_fmt(p_val, 4)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["类别", "观测频数", "理论频数"], "rows": rows, "description": "卡方拟合优度检验完成。", "sections": sections}
