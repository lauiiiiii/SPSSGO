# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "multiple_choice"
METHOD_META = {'label': '多选分析',
 'category': '问卷分析包',
 'description': '对同一多选题拆分后的多个选项变量进行选择频次统计',
 'order': 50,
 'slots': [{'key': 'variables',
            'label': '多选题变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一多选题的多个选项变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "multiple_choice_labels"

def multiple_choice_analysis(df, params):
    """
    多选分析：针对多选题拆分后的多个二值变量统计选择频次
    """
    variables = _resolve_cols(df, params.get("variables", []))
    variable_labels = params.get("variable_labels", {})
    if len(variables) < 2:
        return {"name": "多选分析", "headers": [], "rows": [], "description": "需要至少2个多选题选项变量。"}

    valid_df = df[variables].copy()
    sample_size = int(valid_df.shape[0])
    headers = ["选项", "选择人数", "选择占比(%)", "被提及率(%)"]
    rows = []
    picked = []
    for var in variables:
        mask = _selected_mask(valid_df[var].fillna(0))
        count = int(mask.sum())
        label = variable_labels.get(var, var)
        pct = count / sample_size * 100 if sample_size else 0
        rows.append([label, str(count), _fmt(pct, 1), _fmt(pct, 1)])
        picked.append((label, count, pct))

    rows.sort(key=lambda item: float(item[1]), reverse=True)
    top_label, top_count, top_pct = max(picked, key=lambda item: item[1])
    low_label, low_count, low_pct = min(picked, key=lambda item: item[1])

    sections = []
    sections.append(_sec_table("多选题汇总表", headers, rows, description="统计各选项被选择的人数及在样本中的占比。"))
    advice = (
        "多选分析适合用于查看多选题各选项的总体偏好；\n"
        "第一：优先关注选择人数和选择占比最高的选项；\n"
        "第二：若总占比超过100%，属于多选题的正常现象；\n"
        "第三：可进一步结合交叉分析查看不同人群的偏好差异。"
    )
    sections.append(_sec_advice(advice))
    smart = (
        f"本次多选分析共纳入{sample_size}个样本。"
        f"{top_label}被选择次数最多（{top_count}人，占{_fmt(top_pct, 1)}%），"
        f"{low_label}被选择次数最少（{low_count}人，占{_fmt(low_pct, 1)}%）。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": "多选分析", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = multiple_choice_analysis
