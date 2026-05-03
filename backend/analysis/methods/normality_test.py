# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "normality_test"
METHOD_META = {'label': '正态性分析',
 'category': '数据概览',
 'description': '使用 Shapiro-Wilk 检验判断变量是否服从正态分布',
 'order': 50,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要检验正态性的变量'}],
 'options': [],
 'param_builder': 'direct'}

def normality_test(df, params):
    """
    正态性检验（Shapiro-Wilk）

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if not variables:
        return {"name": "正态性分析", "headers": [], "rows": [], "description": "未指定变量。"}

    headers = ["变量", "N", "Shapiro-Wilk W", "p", "偏度", "峰度", "是否正态"]
    rows = []
    for v in variables:
        s = pd.to_numeric(df[v], errors="coerce").dropna()
        sample = s.sample(min(5000, len(s)), random_state=42) if len(s) > 5000 else s
        w_stat, w_p = shapiro(sample)
        skew = s.skew()
        kurt = s.kurtosis()
        normal = "是" if w_p > 0.05 else "否"
        rows.append([v, str(len(s)), _fmt(w_stat), _fmt(w_p), _fmt(skew), _fmt(kurt), normal])

    sections = []
    sections.append(_sec_table("正态性检验结果", headers, rows,
                               description="Shapiro-Wilk检验原假设为数据服从正态分布。p>0.05则不能拒绝原假设，认为近似正态。"))

    advice = (
        "正态性检验用于判断数据是否服从正态分布；\n"
        "第一：Shapiro-Wilk检验适用于小样本（N<5000），p>0.05说明近似正态；\n"
        "第二：偏度绝对值<2、峰度绝对值<7时，可近似认为正态；\n"
        "第三：大样本（N>30）下，根据中心极限定理，参数检验具有稳健性。"
    )
    sections.append(_sec_advice(advice))

    normal_vars = [r[0] for r in rows if r[6] == "是"]
    non_vars = [r[0] for r in rows if r[6] == "否"]
    smart = "采用Shapiro-Wilk检验对各变量进行正态性检验。"
    if normal_vars:
        smart += f"{'、'.join(normal_vars)}近似服从正态分布（p>0.05）。"
    if non_vars:
        smart += f"{'、'.join(non_vars)}偏离正态分布（p<0.05），但大样本下参数检验仍具稳健性。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": "正态性分析", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = normality_test
