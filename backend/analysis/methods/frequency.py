# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "frequency"
METHOD_META = {'label': '频数分析',
 'category': '数据概览',
 'description': '统计各类别的频次和百分比分布',
 'order': 10,
 'slots': [{'key': 'variable',
            'label': '分析变量',
            'type': 'single',
            'accept': 'any',
            'hint': '放入需要统计频次的变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "frequency_labels"

def frequency_table(df, params):
    """
    频率/百分比统计，含累积百分比

    @param df: 数据 DataFrame
    @param params: 包含 variable 的参数字典
    @return: 含 sections 的结果字典
    """
    variable = params.get("variable", "")
    labels = params.get("labels", {})
    if variable not in df.columns:
        return {"name": "频率统计", "headers": [], "rows": [], "description": f"变量 {variable} 不存在。"}

    vc = df[variable].value_counts().sort_index()
    total = vc.sum()
    headers = ["类别", "频次", "百分比(%)", "累积百分比(%)"]
    rows = []
    cum = 0
    for val, cnt in vc.items():
        if isinstance(val, str):
            label = labels.get(val, val)
        else:
            label = labels.get(str(int(val)), labels.get(str(val), str(val)))
        pct = cnt / total * 100
        cum += pct
        rows.append([label, str(cnt), _fmt(pct, 1), _fmt(cum, 1)])
    rows.append(["合计", str(total), "100.0", "—"])

    sections = []
    sections.append(_sec_table("频率分布表", headers, rows,
                               description="频率分布表展示了各类别的频次、百分比和累积百分比。"))

    # 找出最多和最少的类别
    max_cat = vc.idxmax()
    min_cat = vc.idxmin()
    max_label = labels.get(str(int(max_cat)), labels.get(str(max_cat), str(max_cat))) if not isinstance(max_cat, str) else labels.get(max_cat, max_cat)
    min_label = labels.get(str(int(min_cat)), labels.get(str(min_cat), str(min_cat))) if not isinstance(min_cat, str) else labels.get(min_cat, min_cat)
    smart = (
        f"{variable}的频率分布如表所示，共{total}个有效样本。"
        f"其中，{max_label}频次最高（{vc.max()}，占{_fmt(vc.max() / total * 100, 1)}%），"
        f"{min_label}频次最低（{vc.min()}，占{_fmt(vc.min() / total * 100, 1)}%）。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": f"频数分析：{variable}", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = frequency_table
