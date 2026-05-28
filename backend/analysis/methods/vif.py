# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "vif"
METHOD_META = {'label': '共线性分析',
 'category': '回归&因果分析包',
 'description': '检测多个自变量之间是否存在共线性',
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入需要检测共线性的变量（至少2个）'}],
 'options': [],
 'param_builder': 'direct'}

def vif_analysis(df, params):
    """
    共线性分析，含 VIF 与容忍度

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": "共线性分析", "headers": [], "rows": [], "description": "需要至少2个变量。"}

    temp = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if temp.empty:
        return {"name": "共线性分析", "headers": [], "rows": [], "description": "有效样本不足。" }

    constant_vars = [v for v in variables if temp[v].nunique(dropna=True) <= 1]
    if constant_vars:
        return {
            "name": "共线性分析",
            "headers": [],
            "rows": [],
            "description": f"以下变量在有效样本中没有变异，无法计算 VIF：{'、'.join(constant_vars)}。",
        }

    X = sm.add_constant(temp, has_constant="add")

    headers = ["变量", "VIF", "容忍度", "判断"]
    rows = []
    descs = []
    for v in variables:
        vif = variance_inflation_factor(X.values, X.columns.get_loc(v))
        tol = 1.0 / vif
        judge = "严重共线性" if vif > 10 else ("有共线性" if vif > 5 else "正常")
        rows.append([v, _fmt(vif, 2), _fmt(tol, 3), judge])
        if vif > 10:
            descs.append(f"{v}（VIF={_fmt(vif, 2)}）存在严重多重共线性")
        elif vif > 5:
            descs.append(f"{v}（VIF={_fmt(vif, 2)}）存在一定多重共线性")

    sections = []
    sections.append(_sec_table("共线性诊断", headers, rows,
                               description="VIF（方差膨胀因子）用于检测自变量之间的共线性。容忍度=1/VIF。"))

    advice = (
        "共线性分析用于检测多个自变量之间是否存在共线性；\n"
        "第一：VIF<5，不存在共线性问题；\n"
        "第二：5≤VIF<10，存在一定共线性，需要关注；\n"
        "第三：VIF≥10，存在严重共线性，建议删除或合并变量。"
    )
    sections.append(_sec_advice(advice))

    smart = "共线性分析结果如表所示。"
    if descs:
        smart += '；'.join(descs) + "。建议对高VIF变量进行处理（如删除、合并或使用岭回归）。"
    else:
        smart += "各变量VIF均小于5，不存在严重多重共线性问题，可放心进行回归分析。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": "共线性分析", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = vif_analysis
