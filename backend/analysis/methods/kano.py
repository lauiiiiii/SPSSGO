# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "kano"
METHOD_META = {'label': 'Kano模型',
 'category': '问卷分析包',
 'description': '基于正向题与反向题的配对回答识别题项的Kano类别',
 'order': 90,
 'slots': [{'key': 'functional_vars',
            'label': '正向题',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 1,
            'hint': '按顺序放入正向题变量'},
           {'key': 'dysfunctional_vars',
            'label': '反向题',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 1,
            'hint': '按顺序放入与正向题一一对应的反向题变量'}],
 'options': [],
 'param_builder': 'direct'}

def kano_analysis(df, params):
    """
    Kano模型：基于正向/反向题对计算Kano类别
    """
    functional_vars = _resolve_cols(df, params.get("functional_vars", []))
    dysfunctional_vars = _resolve_cols(df, params.get("dysfunctional_vars", []))
    if not functional_vars or not dysfunctional_vars or len(functional_vars) != len(dysfunctional_vars):
        return {"name": "Kano模型", "headers": [], "rows": [], "description": "请成对提供等数量的正向题和反向题。"}

    kano_map = {
        ("喜欢", "喜欢"): "Q", ("喜欢", "理所当然"): "A", ("喜欢", "无所谓"): "A", ("喜欢", "勉强接受"): "A", ("喜欢", "不喜欢"): "O",
        ("理所当然", "喜欢"): "R", ("理所当然", "理所当然"): "I", ("理所当然", "无所谓"): "I", ("理所当然", "勉强接受"): "I", ("理所当然", "不喜欢"): "M",
        ("无所谓", "喜欢"): "R", ("无所谓", "理所当然"): "I", ("无所谓", "无所谓"): "I", ("无所谓", "勉强接受"): "I", ("无所谓", "不喜欢"): "M",
        ("勉强接受", "喜欢"): "R", ("勉强接受", "理所当然"): "I", ("勉强接受", "无所谓"): "I", ("勉强接受", "勉强接受"): "I", ("勉强接受", "不喜欢"): "M",
        ("不喜欢", "喜欢"): "R", ("不喜欢", "理所当然"): "R", ("不喜欢", "无所谓"): "R", ("不喜欢", "勉强接受"): "R", ("不喜欢", "不喜欢"): "Q",
    }
    answer_labels = {"1": "喜欢", "2": "理所当然", "3": "无所谓", "4": "勉强接受", "5": "不喜欢"}
    category_labels = {"A": "魅力型", "O": "期望型", "M": "必备型", "I": "无差异型", "R": "反向型", "Q": "可疑结果"}

    headers = ["题项", "主导类别", "A", "O", "M", "I", "R", "Q"]
    rows = []
    sections = []
    summary = []
    for f_var, d_var in zip(functional_vars, dysfunctional_vars):
        temp = df[[f_var, d_var]].dropna()
        counts = {key: 0 for key in category_labels}
        for _, row in temp.iterrows():
            f_ans = answer_labels.get(str(int(row[f_var])) if pd.notna(row[f_var]) and str(row[f_var]).replace('.', '', 1).isdigit() else str(row[f_var]), str(row[f_var]))
            d_ans = answer_labels.get(str(int(row[d_var])) if pd.notna(row[d_var]) and str(row[d_var]).replace('.', '', 1).isdigit() else str(row[d_var]), str(row[d_var]))
            counts[kano_map.get((f_ans, d_ans), "Q")] += 1
        dominant = max(counts.items(), key=lambda item: item[1])[0]
        rows.append([f"{f_var} / {d_var}", category_labels[dominant], str(counts["A"]), str(counts["O"]), str(counts["M"]), str(counts["I"]), str(counts["R"]), str(counts["Q"])])
        summary.append(f"{f_var}对应的主导Kano类别为{category_labels[dominant]}")

    sections.append(_sec_table("Kano分类结果", headers, rows, description="根据正向题与反向题的组合回答，将题项划分为Kano类别。"))
    sections.append(_sec_smart("；".join(summary) + "。"))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": "Kano模型", "headers": headers, "rows": rows, "description": "；".join(summary) + "。", "sections": sections}

run = kano_analysis
